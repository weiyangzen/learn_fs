# Research: subset-b-009825

Grouped research for Samba source3 locking files. Each section preserves the source path in the title and is wrapped for source-tree-aligned per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/brlock.c -->
# sources/user-network-fs/samba/source3/locking/brlock.c

## Purpose
`brlock.c` implements Samba's byte-range lock service on top of `brlock.tdb`. It replaces direct `fcntl`-only behavior with a database-backed model that can emulate Windows byte-range semantics, POSIX byte-range semantics, durable-handle disconnect/reconnect behavior, and optional mapping to kernel POSIX locks.

## Important APIs, Types, And Functions
The private `struct byte_range_lock` carries the current `files_struct`, optional request memory/GUID context, the in-memory `struct lock_struct` array, a modified bit, and the locked `db_record`. Public entry points include `brl_init`, `brl_shutdown`, `brl_get_locks`, `brl_get_locks_readonly`, `brl_lock`, `brl_unlock`, `brl_locktest`, `brl_lockquery`, `brl_close_fnum`, `brl_mark_disconnected`, `brl_reconnect_disconnected`, `brl_cleanup_disconnected`, `share_mode_do_locked_brl`, and `file_has_brlocks`. Key helpers are `byte_range_valid`, `byte_range_overlap`, `brl_conflict`, `brl_conflict_posix`, `brl_conflict_other`, `brlock_posix_split_merge`, and `byte_range_lock_flush`.

## Control Flow
Writers call `brl_get_locks`, which fetches and chain-locks a `brlock.tdb` record keyed by `struct file_id`; freeing the returned talloc object flushes changes and releases the record. Windows locks check overlap conflicts, prune dead pids opportunistically, optionally set lower POSIX locks through `set_posix_lock_windows_flavour`, append one `lock_struct`, and mark modified. POSIX-flavour locks rebuild the array through split/merge logic so same-context overlapping ranges coalesce or replace as POSIX semantics require, then optionally map directly to kernel locks. Unlock paths mirror this: Windows unlock removes an exact lock, while POSIX unlock may split retained ranges. `share_mode_do_locked_brl` runs a callback with a share-mode g-lock held and a read-only byte-range snapshot that can be upgraded and flushed afterward.

## State And Persistence
`brlock.tdb` is a volatile TDB opened with `TDB_SEQNUM` and lock order 2. Keys are raw `struct file_id`; values are raw arrays of `struct lock_struct`, not NDR. `byte_range_lock_flush` deletes empty records, stores non-empty arrays with `TDB_REPLACE`, and removes entries whose pid was marked zero after dead-server detection. Read-only lookups cache `fsp->brlock_rec` until the database sequence number changes. Durable-handle disconnects rewrite lock pids/tids/fnums to disconnected sentinels; reconnect restores them to the current server id and handle.

## Dependencies And Integration Points
This file depends on dbwrap/TDB, Samba server ids, messaging context, VFS byte-range lock hooks (`SMB_VFS_BRL_LOCK_WINDOWS`, `SMB_VFS_BRL_UNLOCK_WINDOWS`), POSIX mapping functions from `posix.c`, share-mode locking from `share_mode_lock.c`, and oplock contention accounting. It is invoked by `locking.c` request wrappers and by close/durable-handle paths in smbd.

## Risks And Test Signals
The raw on-disk value format is ABI-sensitive to `struct lock_struct` layout and endian assumptions. Range math is delicate around zero-length locks and `UINT64_MAX` overflow; Windows and POSIX semantics intentionally differ. Destructor-driven flush makes talloc lifetime correctness part of the locking protocol. Stale-pid cleanup mutates records during conflict checks, so tests need multi-process death scenarios. Good test signals include SMB byte-range lock torture tests, zero-length and wraparound ranges, same-context read/write stacking, POSIX split/merge cases, durable disconnect/reconnect cleanup, lock waiter wakeups, and operation with `lp_posix_locking` both enabled and disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/brlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.c -->
# sources/user-network-fs/samba/source3/locking/leases_db.c

## Purpose
`leases_db.c` maintains `leases.tdb`, the reverse mapping from SMB2 lease identity to the files currently attached to that lease. It stores lease state, break state, version/epoch, and the per-file names needed to update lease metadata across rename and close paths.

## Important APIs, Types, And Functions
The public API is `leases_db_init`, `leases_db_add`, `leases_db_del`, `leases_db_parse`, `leases_db_rename`, `leases_db_set`, `leases_db_get`, `leases_db_get_current_state`, and `leases_db_copy_file_ids`. Internally, `leases_db_key` serializes `struct leases_db_key` from client GUID plus SMB2 lease key into a fixed 32-byte key. `leases_db_do_locked` centralizes locked record update: decode `struct leases_db_value`, call a mutator, delete empty records, or NDR-store updated values.

## Control Flow
Mutating callers enter `leases_db_do_locked`, which lazily opens the database read/write, locks the key, decodes any existing NDR value, and invokes an operation-specific callback. Add rejects duplicate file ids, initializes lease-wide state on the first file, appends a `leases_db_file`, and stores. Delete swaps the target file with the last entry and may cause whole-record deletion. Rename finds the matching file id and rewrites service path, base name, and stream name. Set updates lease-wide current/break state and epoch only when the record already has files. Read paths use `dbwrap_parse_record` with NDR decode, except `leases_db_get_current_state`, which peeks the first NDR uint32 for speed and uses the database sequence number to skip unchanged reads.

## State And Persistence
`leases.tdb` is a volatile sequence-numbered TDB opened at lock order 4. Keys are fixed NDR encodings of `(client_guid, lease_key)`. Values are NDR-encoded `struct leases_db_value` records containing current state, breaking fields, lease version, epoch, and a counted `files` array. `leases_db_get_current_state` relies on `current_state` staying the first encoded field, which is explicitly documented in the source.

## Dependencies And Integration Points
The file depends on dbwrap, TDB, Samba NDR generated code for `leases_db`, `file_id` comparison, and SMB2 lease structures. It is called from share-mode logic for adding/removing stale leases, from rename handling to update path metadata, and from `leases_util.c`/strict-locking checks to read current lease state cheaply.

## Risks And Test Signals
The fast current-state reader is fragile if the generated NDR layout changes. Add/delete use swap-with-last semantics, so callers must not depend on file order. Several callbacks carry string pointers into the decoded value and rely on immediate NDR push before caller-owned strings disappear. Empty-record deletion makes missed `modified` flags visible as stale leases. Useful tests include duplicate add rejection, delete of last file deleting the record, rename propagation, malformed NDR records, sequence-number cache behavior, break-state updates, and lease records with multiple stream/base-name combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.h -->
# sources/user-network-fs/samba/source3/locking/leases_db.h

## Purpose
`leases_db.h` declares the lease database interface used by Samba source3 locking and oplock code. It hides the `leases.tdb` record layout while exposing operations for lease-to-file membership, lease state updates, lookup, rename, and file-id copying.

## Important APIs, Types, And Functions
The header forward-declares `struct GUID`, `struct smb2_lease_key`, `struct file_id`, and `struct leases_db_file`. The API includes `leases_db_init`, `leases_db_add`, `leases_db_del`, `leases_db_parse`, `leases_db_rename`, `leases_db_set`, `leases_db_get`, `leases_db_get_current_state`, and `leases_db_copy_file_ids`. `leases_db_parse` exposes a callback over the file array without exposing the containing `leases_db_value`.

## Control Flow
Callers initialize the database in read-only or read/write mode, then address records by client GUID and lease key. Mutators add/remove a specific `file_id`, rename a file entry, or update lease-wide state. Readers either parse all files for a lease, get lease state for a particular file id, or use the sequence-number optimized current-state accessor.

## State And Persistence
The header does not define storage itself; it defines the contract for `leases.tdb` access implemented in `leases_db.c`. The database state is keyed by lease identity and includes both per-lease fields and per-file membership entries.

## Dependencies And Integration Points
It is included by `leases_db.c`, `leases_util.c`, `locking.c`, and share-mode code that manages lease entries during open, close, rename, and stale-reference cleanup. It depends on Samba NTSTATUS and generated lease/file structures supplied by broader source3 include chains.

## Risks And Test Signals
Because the header intentionally hides `struct leases_db_file`, callers can only consume file arrays through callbacks or copy helpers; misuse of callback lifetimes is the main integration risk. Test signals are compile coverage for all users, read-only initialization paths, callback parsing of multi-file leases, and correct behavior when `leases_db_get_current_state` reports an unchanged database sequence number.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_util.c -->
# sources/user-network-fs/samba/source3/locking/leases_util.c

## Purpose
`leases_util.c` provides small helpers that translate legacy oplock state into SMB2 lease state and retrieve the effective lease type for a `files_struct`.

## Important APIs, Types, And Functions
`map_oplock_to_lease_type` maps `BATCH_OPLOCK`, `EXCLUSIVE_OPLOCK`, and `LEVEL_II_OPLOCK` combinations to SMB2 lease READ/WRITE/HANDLE bits. `fsp_lease_type` returns the effective lease state for a file handle, using the direct oplock-to-lease mapping for non-lease oplocks and `leases_db_get_current_state` for real SMB2 leases. `fsp_client_guid` returns the per-client GUID from the connection's server connection client global.

## Control Flow
For non-`LEASE_OPLOCK` handles, `fsp_lease_type` is pure and returns a mapping from `fsp->oplock_type`. For `LEASE_OPLOCK`, it queries `leases.tdb` using the current file's client GUID and lease key, passing `fsp->leases_db_seqnum` so unchanged database state can avoid a full update. Failures are logged at debug level and collapse the cached `fsp->lease_type` to no lease.

## State And Persistence
This file owns no persistent storage, but it reads and updates per-handle cached fields `fsp->leases_db_seqnum` and `fsp->lease_type`. It relies on `leases.tdb` sequence numbers to keep the cache coherent.

## Dependencies And Integration Points
It depends on open-files NDR constants, `locking/proto.h`, smbd globals, and `leases_db.h`. `strict_lock_check_default` in `locking.c` uses `fsp_lease_type` to bypass strict byte-range checks when a read or write lease makes the check unnecessary.

## Risks And Test Signals
The mapping is security and correctness sensitive because returning too broad a lease can skip strict lock checks. The failure path deliberately returns no lease, which is conservative but may hurt performance. Test signals include every oplock combination, lease database sequence cache hits/misses, lease break state changes, missing lease records, and strict-locking `Auto` behavior for read and write I/O.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/leases_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/locking.c -->
# sources/user-network-fs/samba/source3/locking/locking.c

## Purpose
`locking.c` is the request-facing glue for Samba source3 locking. It wraps byte-range lock operations, strict-lock checks, close-time cleanup, share-mode rename handling, delete-on-close token management, stale share/lease cleanup, and share-mode traversal helpers.

## Important APIs, Types, And Functions
Public functions include `lock_type_name`, `lock_flav_name`, `init_strict_lock_struct`, `strict_lock_check_default`, `query_lock`, `do_lock`, `do_unlock`, `locking_close_file`, `share_mode_str`, `rename_share_filename`, `get_file_infos`, `is_valid_share_mode_entry`, `share_entry_stale_pid`, `remove_lease_if_stale`, `get_delete_on_close_token`, `reset_delete_on_close_lck`, `set_delete_on_close_lck`, `set_delete_on_close`, `is_delete_on_close_set`, `file_has_open_streams`, and `share_mode_forall_leases`. Helper state structs bind callbacks to share-mode traversal and messaging.

## Control Flow
I/O strict locking builds a `lock_struct`, checks configuration and handle capability, optionally bypasses checks under `Auto` strict locking when the handle has a matching SMB2 lease, then tests `brlock.tdb` read-only. On conflict it retries under `share_mode_do_locked_brl` so dead lock owners can be cleaned. Lock/unlock request wrappers validate directories and non-lockable handles, call `brl_lock`/`brl_unlock`, and maintain `fsp->current_lock_count` as a fast close-time heuristic. Rename updates the share-mode record's service/base/stream names, sends `MSG_SMB_FILE_RENAME` to other openers, and updates each unique lease record. Delete-on-close stores security tokens by `name_hash` in `share_mode_data` and notifies peers to cancel deleted notifications.

## State And Persistence
This file mutates `brlock.tdb` indirectly through `brlock.c`, `locking.tdb` through `share_mode_lock.c`, and `leases.tdb` through `leases_db.c`. It also updates per-handle state such as `current_lock_count`, `delete_on_close`, share entry flags, name hashes, and cached lease type. Delete-on-close state is persisted inside share-mode data as token arrays keyed by name hash.

## Dependencies And Integration Points
It integrates the SMB request layer with byte-range locks, share-mode locks, messaging, server-id liveness, generated NDR rename/file-id blobs, security token duplication, SMB2 leases, and stream/base-open flags. It is used by open, read/write, rename, close, durable handle, and stream handling paths.

## Risks And Test Signals
Correctness depends on lock-count heuristics staying synchronized with actual lock records; POSIX-flavour locks intentionally disable exact counting with `NO_LOCKING_COUNT`. Rename notification and lease rename failures are mostly logged, so stale path metadata can persist after partial failure. Delete-token arrays use swap deletion, and repeated entries for a name hash need coverage. Stale pid marking modifies entries during validation. Test signals include strict-locking off/on/Auto, lease bypasses, close with pending locks, rename with multiple openers and hardlink name hashes, delete-on-close token replacement/reset, stale pid cleanup, stream-base-open detection, and SMB1 deny-mode flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/locking.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/posix.c -->
# sources/user-network-fs/samba/source3/locking/posix.c

## Purpose
`posix.c` maps Samba byte-range locks onto underlying kernel POSIX locks and manages deferred file descriptor closes required by process-scoped POSIX locking semantics. It supports both Windows-flavour SMB locks and POSIX-flavour SMB locks.

## Important APIs, Types, And Functions
Public APIs are `is_posix_locked`, `posix_locking_init`, `posix_locking_end`, `fd_close_posix`, `set_posix_lock_windows_flavour`, `release_posix_lock_windows_flavour`, `set_posix_lock_posix_flavour`, and `release_posix_lock_posix_flavour`. Important helpers include `map_posix_lock_type`, `posix_lock_in_range`, `posix_fcntl_lock`, `posix_fcntl_getlock`, reference-count helpers over `posix_pending_close_db`, `add_fd_to_close_entry`, `posix_lock_list`, `increment_posix_lock_count`, `decrement_posix_lock_count`, and `locks_exist_on_context`.

## Control Flow
Requests first map SMB lock type to `F_RDLCK` or `F_WRLCK`, downgrading write locks for read-only file opens. Range conversion rejects zero-length POSIX locks and clamps 64-bit SMB ranges into the host `off_t` range; unmappable ranges are treated as successfully ignored. Windows-flavour lock acquisition computes subranges not already covered by this process's locks, applies `F_SETLK` to each, and backs out partial success on failure. Windows-flavour release computes unlock holes so remaining overlapping locks are preserved and may downgrade write locks to read locks before unlocking. POSIX-flavour acquisition maps directly; release punches holes around retained same-process locks. `fd_close_posix` defers closing fds while any lock refcount remains on the file id and later drains saved fds.

## State And Persistence
`posix_pending_close_db` is an in-memory rb-tree dbwrap database. It stores lock refcounts keyed by `file_id + 'r'`, pending close fd arrays keyed by `file_id`, and POSIX context markers keyed by `smblctx`. This state is process-local, not durable, and exists to avoid POSIX lock release side effects when closing one fd would drop locks held through another fd.

## Dependencies And Integration Points
The file depends on VFS lock/getlock hooks, `files_struct` fd helpers, Samba `file_id`, server ids, dbwrap rb-tree storage, and configuration flags `lp_locking`, `lp_posix_locking`, and `use_ofd_locks`. It is called from `brlock.c` when byte-range locks need lower-level POSIX enforcement and from fd close paths.

## Risks And Test Signals
The range-splitting and hole-punching logic is subtle and must preserve Windows reference-count semantics over non-reference-counted POSIX locks. Treating unmappable high ranges as success is compatibility-driven but can hide enforcement gaps. The context-marker key only contains `smblctx`, so uniqueness assumptions matter. Pending-close state stores raw fds and must not double-close or leak them. Test signals include overlapping read/write locks across fds, downgrade-on-unlock cases, 32-bit/NFS large-offset fallbacks, OFD-lock bypass, deferred close drain, POSIX CIFS unlock holes, and failure rollback after partial `F_SETLK` success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/proto.h -->
# sources/user-network-fs/samba/source3/locking/proto.h

## Purpose
`proto.h` is the consolidated source3 locking prototype header for byte-range locks, general locking glue, POSIX lock mapping, and lease utility helpers. It exposes the cross-file API used by smbd locking callers.

## Important APIs, Types, And Functions
The header declares `brlock.c` APIs for initialization, range validation/overlap, lock/unlock/query/test, durable disconnect/reconnect, traversal, locked share-mode-plus-brlock callbacks, and lock snapshots. It declares `locking.c` APIs for strict-lock checks, request wrappers, close cleanup, share-mode formatting, rename, delete-on-close, stale entry, and lease traversal helpers. It declares `posix.c` APIs for kernel-lock checking, init/end, close handling, and Windows/POSIX flavour lock mapping. It declares lease utility functions `map_oplock_to_lease_type`, `fsp_lease_type`, and `fsp_client_guid`.

## Control Flow
The header defines callback contracts such as `share_mode_do_locked_brl_fn_t`, which receives a share-mode lock plus an optional byte-range lock snapshot. It lets higher-level code choose read-only or write paths by selecting `brl_get_locks_readonly`, `brl_get_locks`, or `share_mode_do_locked_brl`.

## State And Persistence
No state is stored in this header. It describes operations that mutate `locking.tdb`, `brlock.tdb`, `leases.tdb`, in-memory POSIX pending-close state, and per-`files_struct` caches.

## Dependencies And Integration Points
It includes `<tdb.h>` and relies on broad Samba declarations for `files_struct`, `share_mode_lock`, `lock_struct`, `server_id`, `file_id`, GUIDs, SMB2 lease keys, security tokens, NTSTATUS, and locking enums. It is the integration layer between source3 smbd request code and the individual locking implementation files.

## Risks And Test Signals
Because many types are only forward-declared elsewhere, include-order regressions are possible. The broad header also couples independent locking subsystems, so signature changes ripple widely. Test signals are full source3 builds, compile coverage of every prototype, and ABI/API checks for VFS modules or callers using byte-range and share-mode hooks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock.c -->
# sources/user-network-fs/samba/source3/locking/share_mode_lock.c

## Purpose
`share_mode_lock.c` implements Samba's `locking.tdb` share-mode record manager. It stores per-file share-mode metadata, sorted open entries, oplock/lease flags, delete-on-close state, async watch/fetch operations, and g-lock based serialization for local and clustered operation.

## Important APIs, Types, And Functions
The file defines private `struct share_mode_lock { struct file_id id; struct share_mode_data *cached_data; }`. Public APIs include `locking_init`, `locking_init_readonly`, `locking_end`, `share_mode_lock_file_id`, `get_existing_share_mode_lock`, `fetch_share_mode_unlocked`, `fetch_share_mode_send/recv`, `share_mode_watch_send/recv`, `share_mode_wakeup_waiters`, `set_share_mode`, `del_share_mode`, `del_share_mode_open_id`, `remove_share_oplock`, `downgrade_share_oplock`, `mark_share_mode_disconnected`, `reset_share_mode_entry`, `share_mode_forall`, `share_mode_forall_read`, `share_entry_forall`, `share_entry_forall_read`, `share_mode_forall_entries`, `share_mode_count_entries`, `share_mode_flags_get/set`, `_share_mode_do_locked_vfs_denied`, `_share_mode_do_locked_vfs_allowed`, prepare-lock/unlock helpers, `fsp_get_share_entry_flags`, and `fsp_apply_share_entry_flags`.

## Control Flow
Initialization opens `locking.tdb`, wraps it in a `g_lock_ctx`, initializes byte-range and POSIX locking, and sets lock ordering. Record access goes through a single active share-mode key guarded by static refcount state; nested locks are allowed only for the same `file_id`. Fetch parses a record or creates fresh `share_mode_data` for new opens. Store serializes modified `share_mode_data`, writes sorted fixed-size share entries, unlocks g-lock state, and optionally moves clean data into memcache. `set_share_mode` binary-searches the sorted entry array by `(server_id, share_file_id)`, rejects duplicates, builds a fixed NDR entry, and stores vector slices around the insertion. Entry update/delete paths fetch the packed array, update one entry or compact stale entries, and write back. Async fetch/watch use `g_lock_dump_send` and watch APIs to support clustered queue behavior.

## State And Persistence
`locking.tdb` records are g-lock-maintained blobs keyed by raw `struct file_id`. The payload format is a little-endian `uint32_t share_mode_data_len`, NDR `share_mode_data`, followed by a sorted array of fixed 124-byte NDR `share_mode_entry` buffers. `share_mode_data` carries identity, path, stream, flags, delete tokens, modified/not_stored bits, and a `unique_content_epoch` used to validate memcache entries. Global static state (`lock_ctx`, `current_share_mode_glck`, `share_mode_lock_key_id`, refcount, `static_share_mode_data`) enforces one locked record per process thread of control.

## Dependencies And Integration Points
This file integrates dbwrap, g_lock, dbwrap watch, memcache, NDR generated `open_files` records, messaging/global contexts, byte-range initialization, POSIX locking init, VFS deny assertions, lease cleanup in `leases_db.c`, and fd/share flags from smbd. It is central to open/close, share-access checks, oplock break/downgrade, durable reconnect, `smbstatus`, and lock waiter wakeups.

## Risks And Test Signals
The packed record format has strict invariants: share entries must remain sorted, fixed entry size must match generated NDR, and the data-length header must parse correctly. Static single-record locking can panic if code tries to lock two different share modes simultaneously. Destructor/store failures panic. Memcache correctness depends on `unique_content_epoch` and clean ownership transfers. Watcher wakeups must fire after entry deletion/oplock changes. Test signals include duplicate open entry rejection, insertion at every sorted position, stale entry compaction, delete of last entry deleting the record, durable disconnect/reconnect `reset_share_mode_entry`, oplock removal/downgrade with lease cleanup, memcache hit/miss on epoch change, async fetch not-found/corruption paths, and g-lock watcher wakeups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock.h -->
# sources/user-network-fs/samba/source3/locking/share_mode_lock.h

## Purpose
`share_mode_lock.h` exposes the public share-mode lock API for source3 code. It defines initialization, locked and unlocked record access, entry mutation, traversal, async fetch/watch, share-mode flags, and prepare-lock helpers while keeping `struct share_mode_lock` and `struct share_mode_data` opaque to most callers.

## Important APIs, Types, And Functions
The header declares `locking_init`, `locking_init_readonly`, `locking_end`, `share_mode_lock_file_id`, `get_existing_share_mode_lock`, `set_share_mode`, `del_share_mode`, `del_share_mode_open_id`, `reset_share_mode_entry`, `mark_share_mode_disconnected`, `remove_share_oplock`, `downgrade_share_oplock`, `file_has_read_lease`, `fetch_share_mode_unlocked`, async `fetch_share_mode_send/recv`, traversal functions, `share_mode_count_entries`, `share_mode_flags_get/set`, `share_mode_watch_send/recv`, `share_mode_wakeup_waiters`, VFS-allowed/denied locked callback wrappers, and prepare-lock/unlock macros. `struct share_mode_entry_prepare_state` embeds enough private storage for an in-place `share_mode_lock`.

## Control Flow
Callers generally acquire a locked record with `get_existing_share_mode_lock` or through callback helpers, mutate entries or data, and rely on talloc/destructor or explicit helper completion to store and unlock. The prepare-lock macros support open paths that may keep the share-mode lock across a staged operation and later release it through `share_mode_entry_prepare_unlock`.

## State And Persistence
The header owns no state, but its contracts govern mutation of `locking.tdb` records and watcher state. The embedded prepare-state union fixes an ABI-like space requirement for the private lock object.

## Dependencies And Integration Points
It includes tevent, file-id, time, and NTSTATUS headers, and forward-declares smbd structures. It is consumed by locking glue, open/close handling, durable handle code, status reporting, oplock/lease paths, and VFS-sensitive code that must distinguish callbacks allowed to call blocking VFS operations from callbacks that must not.

## Risks And Test Signals
The prepare-state storage size must remain large enough for the private `struct share_mode_lock`; the implementation asserts this at runtime. The macros inject `__location__`, so include context matters. Misusing VFS-denied callbacks for blocking operations risks lock stalls. Test signals include compile coverage of all callers, prepare-lock keep/release paths, async fetch/watch API use, and assertions for share entry flags restored during durable reconnect.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock_private.h -->
# sources/user-network-fs/samba/source3/locking/share_mode_lock_private.h

## Purpose
`share_mode_lock_private.h` provides the narrow private escape hatch for code that must access `struct share_mode_data` behind an opaque `struct share_mode_lock`.

## Important APIs, Types, And Functions
The header forward-declares `struct share_mode_lock` and `struct share_mode_data`, and declares `share_mode_lock_access_private_data(struct share_mode_lock *lck, struct share_mode_data **data)`.

## Control Flow
Callers pass an acquired share-mode lock and receive the cached private data pointer. In the current implementation the function asserts that cached data is present and returns `NT_STATUS_OK`; callers use the status to log or panic depending on context.

## State And Persistence
The header itself stores no state. It grants access to mutable in-memory `share_mode_data`, which later persists to `locking.tdb` if marked modified by the caller or helper routines.

## Dependencies And Integration Points
It is included by `share_mode_lock.c` and selected locking code such as `locking.c` that needs delete-on-close tokens, rename path fields, or other `share_mode_data` internals not exposed in the public header.

## Risks And Test Signals
This private API weakens encapsulation, so callers can create persistence bugs by mutating data without setting modified flags. Test signals include delete-on-close and rename paths that access private data, error-path logging when access fails, and full builds that catch accidental exposure or include-order regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/locking/share_mode_lock_private.h -->
