# sources/distributed-fs/ceph/src/client/Client.cc lines 18202-19256

## Scope

This chunk covers the tail of `sources/distributed-fs/ceph/src/client/Client.cc`, from quota limit predicates through the `StandaloneClient` initialization and shutdown methods. The range is not one cohesive subsystem; it is a collection of late-file `Client` helpers and public control entry points that bridge CephFS metadata state, RADOS/Objecter operations, POSIX ACL handling, Linux fscrypt ioctls, client session reclaim, runtime configuration changes, subvolume IO metrics, a recursive-ish copy helper, and standalone client lifecycle.

The chunk depends on earlier `Client.cc` code for the generic quota ancestor walk, xattr and setattr request paths, sync/flush behavior, session opening, mount-state guards, inode path walking, and file IO. It also depends on declarations in `Client.h`, `Inode.h`, `MetaSession.h`, `FSCrypt.h`, `posix_acl.h`, and the MDS message classes. This document intentionally remains chunk-level; the merged per-file report should reconcile it with earlier chunks that define the helper calls used here.

## Purpose

The quota helpers provide small predicates over the shared `check_quota_condition()` traversal. They answer whether an inode is over file-count quota, whether a pending byte growth would exceed byte quota, and whether local unreported growth is close enough to a quota ceiling to trigger early reporting. They are used by write/create paths to reject operations or accelerate quota accounting before the MDS sees stale client-side state.

`check_pool_perm()` adds an optional client-side data-pool permission probe. When `client_check_pool_perm` is enabled, it verifies that a regular file's layout pool and namespace permit read and/or write operations by issuing low-level Objecter operations to the first object and caching the result by `(pool_id, pool_ns)`.

The POSIX ACL helpers make the client honor ACL xattrs when `client_acl_type=posix_acl`. They evaluate access ACLs for permission checks, update ACL masks during chmod, and derive inherited access/default ACL xattrs during create. These helpers sit between ordinary VFS/libcephfs permission code and the xattr mutation path backed by MDS requests.

The Linux-only fscrypt block exposes key management and policy operations to libcephfs/FUSE callers. It stores and invalidates keys in the client-side `FSCryptKeyStore`, sets encryption policy xattrs on empty directories, retrieves policy from inode fscrypt context, reports encryption status and subvolume encryption tag, and returns key presence/user-count status.

The reclaim methods implement client session state takeover. `start_reclaim()` contacts every active MDS, asks whether it owns state for a previous client UUID, waits for replies, checks the old client is not blocklisted in the relevant OSD map epoch, and records a pending `reclaiming_uuid`. `finish_reclaim()` either clears per-session reclaim state or sends a finish message and promotes `reclaiming_uuid` to the active `uuid` metadata field.

The remaining helpers expose perf dump output, dynamic config observation, intrusive pointer hooks for `InodeRef`, random active MDS selection, subvolume metric aggregation, an fscrypt-aware `fcopyfile()` helper, and the `StandaloneClient` specialization that owns its `Objecter` lifecycle.

## Important APIs, Types, and Functions

Quota and pool-permission functions:

- `Client::is_quota_files_exceeded(Inode *in, const UserPerm& perms)` returns true if any relevant quota root has `quota.max_files` set and `rstat.rsize()` at or above that limit.
- `Client::is_quota_bytes_exceeded(Inode *in, int64_t new_bytes, const UserPerm& perms)` returns true if recursive bytes plus the proposed growth would exceed `quota.max_bytes`.
- `Client::is_quota_bytes_approaching(Inode *in, const UserPerm& perms)` compares local dirty growth, `in->size - in->reported_size`, against one-sixteenth of remaining quota space. It asserts `size >= reported_size`.
- `Client::check_pool_perm(Inode *in, int need)` expects `client_lock` to be held. It uses `POOL_CHECKED`, `POOL_CHECKING`, `POOL_READ`, and `POOL_WRITE` state bits in `pool_perms`, waits on `waiting_for_pool_perm` to serialize concurrent probes, and returns `-EPERM` or `-EIO` for missing or indeterminate access.

ACL functions:

- `_posix_acl_permission(const InodeRef& in, const UserPerm& perms, unsigned want)` delegates to `posix_acl_permits()` when `ACL_EA_ACCESS` exists, otherwise returns `-EAGAIN` so callers can fall back to mode-bit permission logic.
- `_posix_acl_chmod(const InodeRef& in, mode_t mode, const UserPerm& perms)` fetches xattrs with `_getattr(... CEPH_STAT_CAP_XATTR ...)`, adjusts the access ACL with `posix_acl_access_chmod()`, and persists it through `_do_setxattr()`.
- `_posix_acl_create(const InodeRef& dir, mode_t *mode, bufferlist& xattrs_bl, const UserPerm& perms)` inherits `ACL_EA_DEFAULT` from the parent directory, may emit `ACL_EA_ACCESS` and `ACL_EA_DEFAULT` into an encoded xattr map, and applies `umask_cb` only when no default ACL is present.

Client control and fscrypt functions:

- `set_filer_flags()` and `clear_filer_flags()` update Objecter global op flags under `client_lock`. Only `CEPH_OSD_FLAG_LOCALIZE_READS`, or zero for set, is accepted by assertion.
- `set_uuid()` and `set_session_timeout()` are pre-mount metadata setters guarded by `initialize_state`. `set_uuid()` closes sessions after changing metadata so future session opens use the new UUID.
- `add_fscrypt_key()`, `remove_fscrypt_key()`, `get_fscrypt_key_status()`, `set_fscrypt_policy_v2()`, `get_fscrypt_policy_v2()`, `is_encrypted()`, and low-level `ll_*` variants are Linux-only and map FUSE/ioctl-facing operations onto `FSCryptKeyStore`, `FSCryptContext`, and Ceph xattrs.
- `_is_empty_directory()` acquires `client_lock`, ensures shared directory caps or fetches them via `_ll_getattr()`, and checks `dirstat.nsubdirs | dirstat.nfiles`.
- `ll_set_fscrypt_policy_v2()` accepts only directories, treats an identical existing policy as success and a different one as `-EEXIST`, rejects unsupported policies, then writes `ceph.fscrypt.auth` and `ceph.fscrypt.file` using `CEPH_XATTR_CREATE`.

Reclaim, config, and diagnostics:

- `start_reclaim(const std::string& uuid, unsigned flags, const std::string& fs_name)` subscribes to an MDS map, opens sessions, checks `CEPHFS_FEATURE_RECLAIM_CLIENT`, sends `MClientReclaim`, waits on `waiting_for_reclaim`, validates OSD blocklist state, and records `metadata["reclaiming_uuid"]`.
- `finish_reclaim()` resets `MetaSession::reclaim_state` for all sessions and, when reclaim was started, sends `MClientReclaim("", FLAG_FINISH)` then updates `metadata["uuid"]`.
- `handle_client_reclaim_reply()` is the dispatch-side state update for `MClientReclaimReply`; it records `RECLAIM_OK`/`RECLAIM_FAIL`, maximum OSD epoch, target address vector, and signals waiters.
- `set_cap_epoch_barrier(epoch_t e)` updates `cap_epoch_barrier`, which later cap-release messages use to force the MDS to wait for an OSD map epoch after canceled RADOS operations.
- `get_perf_counters(bufferlist *outbl)` executes the admin-socket `perf dump` command in JSON form after checking the client is initialized.
- `get_tracked_keys()` returns the configuration keys this `md_config_obs_t` implementation observes. It contains a sorted static array and asserts sort order at compile time.
- `handle_conf_change(const ConfigProxy& conf, const std::set<std::string>& changed)` applies live config updates under `client_lock`, including permissions, ACL mode, LRU midpoint, ObjectCacher limits, metric collection, cap release delay, mount timeout, write-delay injection, subvolume snapshot visibility, and fscrypt alternate-name behavior.

Reference and metrics helpers:

- `intrusive_ptr_add_ref(Inode *in)` and `intrusive_ptr_release(Inode *in)` are free functions that integrate `InodeRef` intrusive pointers with `Inode::iget()` and `Client::put_inode()`.
- `_get_random_up_mds()` chooses a random rank from `mdsmap->get_up_mds_set()` while `client_lock` is held, or returns `MDS_RANK_NONE`.
- `SubvolumeMetricTracker` owns `inode_subvolume`, `subvolume_metrics`, `last_subvolume_metrics`, and `metrics_lock`. It maps inode IDs to subvolume inode IDs, aggregates `SimpleIOMetric` instances into `AggregatedIOMetrics`, and exposes current plus last metrics through `dump()`.

Copy and lifecycle:

- `Client::fcopyfile(const char *spath, const char *dpath, UserPerm& perms, mode_t mode)` path-walks the source without following symlinks, copies `fscrypt_auth` and `fscrypt_file` options into destination create calls, then handles symlinks with `readlink()`/`do_symlinkat()`, directories with `do_mkdirat()`, and regular files with `do_openat()`, `open()`, `read()`, and `write()`.
- `StandaloneClient::StandaloneClient()` constructs the base `Client` with a newly allocated `Objecter`, wires the messenger into `MonClient`, and sets client incarnation zero.
- `StandaloneClient::init()` performs `_pre_init()`, `objecter->init()`, messenger dispatcher registration, monitor initialization, authentication, `objecter->start()`, `_finish_init()`, and initialize-state transition. Error paths stop the timer, unlock, shut down Objecter/ObjectCacher/MonClient, and return the failure.
- `StandaloneClient::shutdown()` composes `Client::shutdown()` with `objecter->shutdown()` and `monclient->shutdown()`.

## Control Flow

Quota checks are intentionally thin. Each predicate passes a lambda to `check_quota_condition()`, defined just before this range, which walks from the current inode toward the root quota ancestor until a predicate is true or the root is reached. The bytes-approaching path first computes the client-local growth since the last reported size; if a quota root is already full it returns true, otherwise it treats less than one-sixteenth remaining space as approaching.

`check_pool_perm()` has two phases. First it checks fast exits: disabled config, non-regular file, cached result, or concurrent probe in progress. If another thread is checking the same pool/namespace, the caller waits and retries. If no cached result exists, snapshots are skipped because the write probe could create an orphan first object. For normal head files, the method marks the key `POOL_CHECKING`, issues a `stat` and a `create(true)` operation against the first object through `objecter->mutate()`, drops `client_lock` while waiting, reacquires it, translates `0`/`-ENOENT` into read permission and `0`/`-EEXIST` into write permission, and treats non-`EPERM` unexpected errors as indeterminate `-EIO`. Finally it compares the caller's requested capability mask against the cached bits.

The ACL create/chmod paths fetch xattrs before local manipulation so they work against current MDS state. Create inheritance follows POSIX ACL semantics: symlinks are excluded, the parent default ACL can modify the requested mode, an equivalent ACL may collapse into pure mode bits, directories inherit the default ACL, and only non-empty inherited maps are encoded into the create request bufferlist. In the no-default-ACL case, the client applies its registered umask callback.

Fscrypt policy setting starts from an fd wrapper or direct inode call, then enforces directory-only and empty-directory-only semantics. If the directory already has an fscrypt context, the requested policy is standardized before comparison so padding does not affect equality. New policy setup encodes a freshly initialized `FSCryptContext` with a generated nonce into `ceph.fscrypt.auth`, then initializes `ceph.fscrypt.file` to a zero `uint64_t` size record. Policy retrieval is the inverse: convert the inode context to `fscrypt_policy_v2`, reject non-v2 policies, or return `-ENODATA` if encryption is absent.

Fscrypt key management is local to the client process. `add_fscrypt_key()` creates a key handler and copies the kernel-style key identifier out when requested. `remove_fscrypt_key()` invalidates the key for a user and attempts to sync filesystem state when files are not busy, although the expression `kid->removal_status_flags & (FSCRYPT_KEY_REMOVAL_STATUS_FLAG_FILES_BUSY == 0)` deserves scrutiny because the comparison is evaluated before the bitwise operation. `get_fscrypt_key_status()` converts the user key specifier to a Ceph key identifier, looks it up in the key store, and reports ABSENT, INCOMPLETELY_REMOVED, or PRESENT plus user count.

`start_reclaim()` is a blocking state machine under `client_lock`, with deliberate unlock only while waiting for an OSD map epoch. It rejects uninitialized clients, empty UUIDs, and attempts to reclaim the active UUID. It subscribes to the requested filesystem's MDS map and waits for an epoch. For each in-MDS rank, it waits for the rank to be up, opens a session if needed, checks the MDS feature bit, sends reclaim messages while the session is `RECLAIM_NULL` or `RECLAIMING`, waits for `handle_client_reclaim_reply()`, returns on failure state, and advances only after success. When all ranks have answered, it requires some target address unless the reset flag allows `-ENOENT`; non-reset reclaim then waits for the reported OSD epoch and checks that the target addresses are not blocklisted before recording pending reclaim metadata.

Configuration updates are simple dispatch on changed key names. All mutations happen while holding `client_lock`, which matches ObjectCacher setter expectations and protects shared client state such as `client_permissions`, `acl_type`, and timing fields. The `conf` parameter is not used directly; the implementation reads current values from `cct->_conf`.

`SubvolumeMetricTracker::aggregate()` has two modes. Non-clean aggregation takes a shared lock, copies per-subvolume aggregate values into a result vector, and leaves current metrics in place. Clean aggregation swaps the entire `subvolume_metrics` map into a local temporary under a unique lock, then converts the temporary into result entries after releasing the lock. Both modes later take a unique lock again to store `last_subvolume_metrics` for diagnostic dump output.

`fcopyfile()` performs metadata-sensitive source inspection under `client_lock`, then uses public client methods for the actual IO and creation. For regular files it snapshots `srcin->size` before opening and then copies in up to 1 MiB chunks using explicit offsets. It exits through a local cleanup label that closes destination and, when opened, source file descriptors. Zero-length files create/truncate the destination but skip opening the source for read.

`StandaloneClient::init()` uses the initialization-state writer token to prevent concurrent initialization. It registers both Objecter and Client as messenger dispatchers after Objecter init and before monitor authentication. On monitor init or auth failure, it manually unwinds the partially initialized state because `_finish_init()` has not run.

## State and Persistence Behavior

Most persistent cluster-visible changes in this chunk go through existing MDS or OSD paths rather than writing local files. ACL chmod and fscrypt policy setup are persisted as xattr mutations sent to the MDS. `fcopyfile()` persists new dentries/inodes/data through the ordinary symlink, mkdir, open, read, and write client APIs. Pool-permission probes may create the first data object when write permission exists; this is why snapshot inodes bypass the check.

Client-local durable-for-session state includes:

- `pool_perms`, a process-local permission cache keyed by pool id and namespace. Indeterminate errors erase the key so a later operation can re-probe.
- `metadata`, which carries session metadata such as `uuid`, `timeout`, and temporary `reclaiming_uuid`.
- `reclaim_errno`, `reclaim_osd_epoch`, `reclaim_target_addrs`, and every `MetaSession::reclaim_state`, which drive the reclaim state machine.
- `cap_epoch_barrier`, used later when sending cap releases.
- runtime booleans and limits updated by `handle_conf_change()`.
- `SubvolumeMetricTracker` maps and `last_subvolume_metrics`, all in-memory and reset only by clean aggregation, inode removal, or client teardown.
- the client-side `FSCryptKeyStore`; key presence is not a cluster xattr and must be supplied per client process.

Locking is central. Many entry points assert or acquire `client_lock`. `check_pool_perm()` deliberately unlocks while waiting for Objecter completions to avoid blocking unrelated client work. `_is_empty_directory()`, fscrypt xattr tag lookups, config updates, random MDS selection, and StandaloneClient init use explicit locking. `SubvolumeMetricTracker` uses a separate `std::shared_mutex`, which keeps metrics updates independent from the main client lock.

Initialization and mount state are enforced with `RWRef_t` guards. `set_uuid()` and `set_session_timeout()` assert the pre-mount initialized state. `sync_fs()` and xattr low-level wrappers outside this range use mount-state readers; fscrypt fd wrappers rely on valid file handles, while direct `ll_*` fscrypt methods operate on caller-supplied inodes.

## Dependencies and Integration Points

This code integrates with the CephFS MDS through `MetaRequest`, xattr operations, `MClientReclaim`, `MClientReclaimReply`, MDS feature bits, `MetaSession`, and `MDSMap`. Reclaim depends on session opening, MDS map subscription, `waiting_for_mdsmap`, `waiting_for_reclaim`, and connection-bound session lookup.

It integrates with RADOS through `Objecter`, `ObjectOperation`, `OSDMap::file_to_object_locator()`, `SnapContext`, `C_SaferCond`, `objecter->wait_for_map()`, and `objecter->with_osdmap()`. The pool permission probe and reclaim blocklist check are the main OSD-facing actions in this chunk.

It integrates with the object cache and cap flushing indirectly. `remove_fscrypt_key()` may call `sync_fs()`, whose earlier implementation flushes ObjectCacher data, caps, mdlog, cap releases, unsafe requests, and waits for cap flush acknowledgement. `handle_conf_change()` directly updates ObjectCacher limits.

It integrates with Linux fscrypt and FUSE ioctl handling through `fscrypt_uapi.h`, `FSCrypt`, `FSCryptContext`, `FSCryptKeyStore`, `fscrypt_policy_v2`, `fscrypt_remove_key_arg`, and `fscrypt_get_key_status_arg`. `fuse_ll.cc` calls these client methods for fscrypt policy/key ioctls.

It integrates with POSIX ACL parsing and rewriting through `posix_acl.cc` helpers and the `ACL_EA_ACCESS`/`ACL_EA_DEFAULT` xattr names. The xattr API must permit these names even though `_listxattr()` filters internal `ceph.` names elsewhere.

Subvolume metrics tie into earlier inode update, cap removal, read, and write paths. Inode-to-subvolume mappings are added when inode metadata carries a subvolume ID, removed on cap release paths, and metrics are added by read/write completion paths. Periodic global metrics collection calls `aggregate(true)` in earlier code before sending metrics to the MDS.

`StandaloneClient` is the libcephfs-style client specialization for callers that do not supply an externally managed Objecter. It depends on Messenger, MonClient, Objecter, ObjectCacher, timer, authentication, and dispatcher ordering.

## Risks and Edge Cases

`check_pool_perm()` can have observable side effects because the write probe uses `create(true)` against the file's first object. The snapshot bypass avoids orphan object creation, but head-file probes may still create an object earlier than user data would. The permission result is cached by pool and namespace, so permission changes during a client lifetime may not be noticed unless other code clears `pool_perms`.

The permission probe serializes concurrent checks with `POOL_CHECKING`, but it releases `client_lock` during OSD waits. The inode layout values are copied before unlock, which is good; however, callers must tolerate that the inode or session state may have changed by the time the lock is reacquired. The code signals all waiters on both success and indeterminate failure.

Quota checks depend on current recursive stats and snapshot realm ancestry. If `rstat`, `reported_size`, or quota-root cache state is stale, the helpers may be conservative or late. `is_quota_bytes_approaching()` asserts `size >= reported_size`, so any accounting regression that violates that invariant will abort debug builds.

ACL helpers return `-EAGAIN` when no ACL should be applied, not success. Callers must preserve that contract. Create-mode changes happen through a `mode_t *`, so errors after `posix_acl_inherit_mode()` can leave the local mode value modified even though no create request is emitted by this helper.

The fscrypt status/tag helpers set the local pointer variable `enctag = nullptr` on errors or non-encrypted files, which does not clear the caller's buffer or pointer because it is passed by value. Callers should rely on the return code rather than expecting pointer nulling to escape. The tag lookup also uses `sizeof(enctag)`, which is the size of the pointer parameter, not the backing buffer length; that limits copied tag bytes and is a likely bug surface.

`remove_fscrypt_key()` has a suspicious busy-files condition: `FSCRYPT_KEY_REMOVAL_STATUS_FLAG_FILES_BUSY == 0` is a boolean expression, so the bitwise `&` is probably not checking the intended flag. If the intent was "sync when files are not busy," the expression should be validated against Linux fscrypt semantics.

`ll_set_fscrypt_policy_v2()` writes two xattrs sequentially. If `ceph.fscrypt.auth` succeeds and `ceph.fscrypt.file` fails, the directory may be left partially marked with encryption auth data. Recovery behavior depends on MDS/xattr semantics outside this chunk.

`start_reclaim()` waits while holding `client_lock` for MDS map changes, session open contexts, and reclaim replies. That matches existing client wait helpers, but it is sensitive to correct signaling in map/session/message handlers. Reclaim target fields are not obviously reset at the start except `reclaim_errno`; stale `reclaim_target_addrs` or `reclaim_osd_epoch` should be considered when reviewing repeated reclaim attempts.

`SubvolumeMetricTracker::remove_inode()` removes only the inode-to-subvolume mapping. It does not erase the subvolume entry or decrement any aggregate when the last inode leaves, so empty subvolume metric buckets can persist until clean aggregation swaps the map away.

`fcopyfile()` has several correctness edges. It does not check for negative `readlink()` before using `linkpath[link_size]`, it uses a fixed 4096-byte symlink buffer, it snapshots the source size before copying without handling concurrent truncation/growth, and after each read it sets the next requested read length to the previous return length. Short reads before EOF could therefore reduce future chunk size and still loop until the original size is reached. The TODO-style comment notes that size should be reverified. It also returns `0` for unsupported source types other than symlink, directory, or regular file.

`StandaloneClient::init()` has manual cleanup paths for partial initialization. Any future addition to `_pre_init()` or Objecter/MonClient startup must be mirrored in both failure branches to avoid leaked threads, timers, or dispatchers.

## Test Signals

High-signal coverage for this chunk would include:

- Quota tests with root and nested quota realms covering file-count limit, byte-growth rejection, and approaching-threshold behavior when `size - reported_size` crosses one-sixteenth remaining space.
- Pool permission tests with `client_check_pool_perm` enabled for read-only, write-only, no-access, and transient OSD error cases, including concurrent callers waiting on `POOL_CHECKING` and snapshot inodes skipping the probe.
- POSIX ACL tests for permission fallback (`-EAGAIN`), chmod ACL mask updates, create inheritance from default ACL, directory default ACL propagation, symlink exclusion, equivalent-ACL mode collapse, and umask application only when no default ACL exists.
- Fscrypt ioctl/FUSE tests for adding/removing keys, absent/present/incompletely-removed key status, setting policy on non-directories and non-empty directories, idempotent same-policy set, different-policy `-EEXIST`, unsupported cipher/policy `-EINVAL`, and `ENODATA` for unencrypted inodes.
- Failure-injection tests for the two-step fscrypt xattr creation path, especially auth success followed by file-size xattr failure.
- Reclaim tests with multiple MDS ranks: rank down then map update, session open wait, missing `CEPHFS_FEATURE_RECLAIM_CLIENT`, successful replies with increasing OSD epochs, failure replies carrying errno, reset-mode `-ENOENT`, target blocklisted `-ENOTRECOVERABLE`, and finish messages updating metadata.
- Runtime config tests proving `handle_conf_change()` updates every tracked key and ObjectCacher receives size/object/dirty/age changes under lock.
- Subvolume metric tests for add duplicate inode, add metric for unmapped inode, clean vs non-clean aggregation, `last_subvolume_metrics` dump, and inode removal before later metrics.
- `fcopyfile()` tests for symlink, directory, empty file, encrypted source metadata propagation, regular data copy, read/write errors, long symlink/readlink failure, and concurrent source size changes.
- Standalone client init tests or fault injection around `monclient->init()` and `authenticate()` failures to verify timer shutdown, Objecter shutdown, ObjectCacher stop, MonClient shutdown, and initialize-state behavior.

Existing source-visible test hooks are mostly indirect: `fuse_ll.cc` exercises fscrypt methods for ioctls, `posix_acl.cc` supplies ACL parser semantics, earlier `Client.cc` read/write paths feed subvolume metrics, and admin-socket/perf dump can observe metrics and counters. A merged research pass should look for repository-local QA files outside this source snapshot if available; the checked tree paths for `qa`, `src/test`, and `src/pybind` were absent under `sources/distributed-fs/ceph`.

## Cross-Chunk Notes

The immediately preceding code defines `get_quota_root()` and `check_quota_condition()`, which are essential to the first three functions in this chunk. Earlier chunks also define `_sync_fs()`, `_listxattr()`, `_removexattr()`, `_flush()`, `_fsync()`, `path_walk()`, `do_openat()`, `do_mkdirat()`, `do_symlinkat()`, read/write methods, MDS map subscription, session opening, and message dispatch that calls `handle_client_reclaim_reply()`.

This range reaches the end of `Client.cc`; there is no later chunk needed for function closure. The final per-file document should merge this late-file material with the earlier initialization, mount/session, cap, xattr, IO, and request machinery so the helper dependencies are not duplicated or left dangling.
