# Group Research: group_788_linux_sources_os_linux_linux_fs_nfsd_nfs4callback_c_sources_os_linux_50e1eec7ac7f

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4callback.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4callback.c

This file implements the NFSD server-side NFSv4 callback/backchannel RPC client. It builds and tears down per-network-namespace callback RPC program metadata, encodes callback COMPOUND requests, decodes callback replies, manages NFSv4.1 callback slots and `CB_SEQUENCE`, and runs callback work items against each `nfs4_client`.

Primary responsibilities:
- Encode/decode callback XDR for `CB_NULL`, `CB_RECALL`, `CB_RECALL_ANY`, `CB_GETATTR`, `CB_LAYOUTRECALL` when pNFS is enabled, `CB_NOTIFY_LOCK`, and `CB_OFFLOAD`.
- Translate callback `nfsstat4` values to Linux negative errno-style task status.
- Build `CB_COMPOUND` headers and update operation counts after appending callback operations.
- For NFSv4.1+, prepend `CB_SEQUENCE`, validate session ID, slot ID, sequence number, and target highest slot in replies.
- Create RPC clients for NFSv4.0 callbacks and NFSv4.1 backchannel callbacks.
- Queue, requeue, probe, shut down, and destroy callback work.
- Maintain callback channel state: unknown, up, down, fault, kill/update flags, callback inflight count, and callback session slot ownership.

Important entry points and exports:
- `nfsd_net_cb_init()` / `nfsd_net_cb_shutdown()` allocate and release the per-netns callback RPC program, version table, proc table counts, and stats.
- `nfsd4_init_cb()` initializes an individual `struct nfsd4_callback` with its client, RPC procinfo, operation callbacks, work item, flags, status fields, held slot, and referring-call list.
- `nfsd4_run_cb()` increments callback inflight accounting and queues callback work on the client callback workqueue.
- `nfsd4_probe_callback()` and `nfsd4_probe_callback_sync()` mark callback state unknown, request callback parameter update, and run the null probe.
- `nfsd4_change_callback()` updates stored callback connection data under `cl_lock`.
- `nfsd4_shutdown_callback()` marks the client kill bit, queues callback shutdown processing, flushes the callback workqueue, and waits for inflight callbacks to finish.
- `nfsd41_cb_referring_call()` and `nfsd41_cb_destroy_referring_call_list()` manage NFSv4.1 referring-call metadata carried in `CB_SEQUENCE`.

Core control flow:
- `nfsd4_run_cb()` queues `cb_work`; `nfsd4_run_cb_work()` serializes execution on `cl_callback_wq`.
- Before sending a callback, `nfsd4_run_cb_work()` processes pending callback updates, recreating or destroying the RPC client as needed via `nfsd4_process_cb_update()` and `setup_callback_client()`.
- For NFSv4.1 callbacks, `nfsd4_cb_prepare()` reserves a backchannel slot using `nfsd41_cb_get_slot()` before starting the RPC.
- Decode functions process `CB_COMPOUND` reply, then `CB_SEQUENCE` reply, then operation-specific status/payload.
- `nfsd4_cb_done()` handles v4.0 connection signal requeue, v4.1 sequence completion, operation status propagation, operation-specific done callbacks, and callback channel down/fault marking.
- `nfsd4_cb_release()` either requeues or destroys the callback.
- `nfsd41_destroy_cb()` releases held callback slots, clears running flags, calls operation-specific release handlers, and decrements inflight accounting.

State and synchronization:
- The client callback workqueue is relied on to serialize callback client recreation and access to `cl_cb_client`.
- `cl_lock` protects callback connection updates and backchannel session/connection lookup.
- Session `se_lock` protects callback slot bitmap, highest slot, and callback sequence numbers.
- `cl_cb_inflight` is an atomic counter with wakeup support for shutdown waits.
- Callback flags include running, wake, requeue, client update, and client kill semantics.
- NFSv4.1 callback slots are acquired before RPC start and released after sequence completion or callback destruction.
- Referring-call lists are caller-serialized, dynamically allocated, and explicitly destroyed by callback users such as offload callbacks.

Dependencies and integration:
- Uses SUNRPC client APIs: `rpc_create`, `rpc_shutdown_client`, `rpc_call_async`, `rpc_restart_call_prepare`, `rpc_delay`, wait queues, and procinfo tables.
- Uses NFSD state objects from `state.h`, XDR helpers from `xdr4cb.h`, `xdr4.h`, and generated `nfs4xdr_gen.h`.
- Interacts with pNFS layout recall code through `CB_LAYOUTRECALL`.
- Interacts with server-side copy through `CB_OFFLOAD`.
- Uses tracepoints throughout for callback setup, queueing, sequence status, errors, and release.
- Uses credentials from either machine credentials for NFSv4.0 or session callback security uid/gid for NFSv4.1+.

Error handling and notable risks:
- XDR encoding assumes reservations succeed in many helper paths and uses `WARN_ON_ONCE` or direct dereference after `xdr_reserve_space`; this is typical kernel XDR style but makes size estimates important.
- Callback errors can mark the channel down or faulty; NFSv4.1 sequence ambiguity can force session recovery.
- Slot sequencing is delicate: bad sequence, bad slot, or misordered sequence can intentionally leak/retire a slot and requeue.
- Callback client recreation depends on serialized workqueue execution; external code must preserve that assumption.
- `setup_callback_client()` has different credential and transport paths for v4.0 and v4.1+, including GSS principal validation for v4.0.
- Shutdown must wait for both queued work and async RPC release paths; inflight accounting is central to avoiding teardown races.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4idmap.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4idmap.c

This file implements NFSD NFSv4 owner/group idmapping between wire-format owner strings and kernel UID/GID values. It maintains per-network-namespace SUNRPC cache details for both ID-to-name and name-to-ID directions, performs upcalls to user space idmap handling, and provides exported mapping helpers used by NFSv4 XDR encode/decode paths.

Primary responsibilities:
- Maintain `nfs4.idtoname` cache for local numeric uid/gid plus auth domain to NFSv4 owner/group names.
- Maintain `nfs4.nametoid` cache for NFSv4 owner/group names plus auth domain to local numeric ids.
- Register/unregister per-netns idmapping cache instances.
- Encode UID/GID attributes as NFSv4 owner strings.
- Decode owner strings into kernel `kuid_t` / `kgid_t`.
- Support numeric owner strings for `AUTH_SYS` when `nfs4_disable_idmapping` is enabled.

Important entry points and exports:
- `nfsd_idmap_init()` creates and registers per-netns `idtoname_cache` and `nametoid_cache`.
- `nfsd_idmap_shutdown()` unregisters and destroys both per-netns caches.
- `nfsd_map_name_to_uid()` maps wire owner names to `kuid_t`.
- `nfsd_map_name_to_gid()` maps wire group names to `kgid_t`.
- `nfsd4_encode_user()` converts a kernel uid through the request namespace and encodes an NFSv4 owner value into XDR.
- `nfsd4_encode_group()` does the same for gid values.

Core structures and cache behavior:
- `struct ent` is the cache item: `cache_head`, type user/group, numeric id, mapped name, auth domain name, and RCU head.
- `ent_init()` copies cache item fields for insert/update.
- `ent_put()` frees entries using `kfree_rcu()`.
- `idtoname_hash()` combines auth domain, id, and user/group type.
- `nametoid_hash()` hashes the name string; matching additionally checks type and auth domain.
- Cache request format is qword-based and includes auth domain, type, and either id or name.
- Parse functions consume user-space replies, set expiry, mark negative entries for misses, and update the SUNRPC cache.

Control flow:
- A mapping helper creates a stack `struct ent` key with type, auth domain from `rqst_authname()`, and either name or id.
- `idmap_lookup()` performs cache lookup and `cache_check()`, retrying if a timeout raced with a cache replacement.
- Name-to-id maps `-ENOENT` to `nfserr_badowner`; other errors go through `nfserrno()`.
- ID-to-name falls back to numeric ASCII encoding on `-ENOENT`.
- When `nfs4_disable_idmapping` is true and the request auth flavor is below `RPC_AUTH_GSS`, name-to-id first accepts numeric strings directly and id-to-name always emits ASCII ids.

State and synchronization:
- Per-netns cache pointers live in `struct nfsd_net`.
- Cache lifetime is managed through `cache_create_net`, `cache_register_net`, `cache_unregister_net`, and `cache_destroy_net`.
- Cache entries are RCU-freed via `kfree_rcu`.
- Mapping calls rely on the SUNRPC cache and request cache handle for upcall deferral/waiting.

Dependencies and integration:
- Uses SUNRPC cache APIs and qword parsing/encoding.
- Uses `rqstp->rq_gssclient` or `rqstp->rq_client` auth domains to partition mappings by authentication context.
- Uses `nfsd_user_namespace()` to convert between kernel namespace ids and on-wire numeric ids.
- Called by NFSv4 attribute encode/decode in NFSD XDR paths.
- Warns if idmapping fails because idmapd is absent or has died.

Error handling and notable risks:
- Public mapping functions warn that `RQ_USEDEFERRAL` must be clear before idmap lookup because NFSv4 compounds must not be dropped; callers rely on compound setup to clear it.
- Name and auth strings are bounded by `IDMAP_NAMESZ`; overlong values become `nfserr_badowner` or parse failures.
- `simple_strtoul()` is used in one cache parser for id replies, while public numeric-name parsing uses `kstrtouint()`.
- Negative cache entries are valid behavior and directly affect owner resolution.
- Numeric fallback for `AUTH_SYS` is compatibility-sensitive and controlled by module parameter.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4layouts.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4layouts.c

This file implements NFSD pNFS layout state management. It tracks device ID mappings, layout stateids, granted layout segments, layout recalls, lease integration, and fencing behavior when clients do not return recalled layouts.

Primary responsibilities:
- Maintain a global pNFS device-id-to-export-fsid map.
- Determine which pNFS layout types an export supports.
- Allocate, validate, and free layout stateids.
- Insert, merge, return, and free layout segments for a stateid/client/file.
- Recall conflicting layouts and schedule callback work.
- Integrate layout state with kernel file leases so local file access can trigger layout recall.
- Fence clients when layout recall times out and the layout driver supports fencing.
- Initialize/destroy pNFS layout slab caches and device-id maps.

Important entry points and exports:
- `nfsd4_init_pnfs()` initializes device hash buckets and slab caches.
- `nfsd4_exit_pnfs()` destroys slab caches and frees device-id maps.
- `nfsd4_setup_layout_type()` sets per-export supported layout type bits based on config and exportfs block layout capabilities.
- `nfsd4_set_deviceid()` assigns a device id for an export/device generation.
- `nfsd4_find_devid_map()` looks up a device-id map by index.
- `nfsd4_preprocess_layout_stateid()` validates an existing layout stateid or creates one from open/lock/delegation state.
- `nfsd4_insert_layout()` records a newly granted layout segment and updates the layout stateid generation.
- `nfsd4_return_file_layouts()`, `nfsd4_return_client_layouts()`, `nfsd4_return_all_client_layouts()`, and `nfsd4_return_all_file_layouts()` process explicit or forced layout returns.
- `nfsd4_close_layout()` tears down the lease/file reference associated with a layout stateid.

Core data structures:
- `struct nfs4_layout` represents one granted layout segment attached to a layout stateid.
- `struct nfs4_layout_stateid` is allocated through the generic NFSv4 stateid allocator and tracks layouts per client and per file.
- `nfsd4_layout_ops[]` dispatches layout-type-specific behavior for flex-files, block, and SCSI layouts when enabled.
- `nfsd4_deviceid_map` ties a generated fsid index to export fsid bytes.

Control flow:
- `LAYOUTGET` processing in `nfs4proc.c` calls `nfsd4_preprocess_layout_stateid()`, then layout-type driver `proc_layoutget()`, then `nfsd4_insert_layout()`.
- On insertion, this file recalls conflicting layouts from other layout stateids on the same file before recording a new segment.
- Segment insertion attempts to merge adjacent/overlapping segments with identical iomode; otherwise allocates a new `nfs4_layout`.
- `LAYOUTRETURN` can return file, fsid, or all layouts. File returns may shrink or remove segments; split returns are not fully supported and retain the whole segment.
- Recall uses `nfsd4_recall_file_layout()` to mark a stateid recalled, increment per-file recall count, take a stateid reference, and run `CB_LAYOUTRECALL`.
- Callback completion frees returned layouts or fences the client if recall does not complete.
- Lease break callbacks trigger layout recall and may schedule fencing on timeout.

State and synchronization:
- `nfsd_devid_lock` protects global device-id map creation and sequence allocation; lookups use RCU list traversal.
- `cl_lock` protects client layout state lists.
- `fi_lock` protects per-file layout state lists and conflict checks.
- `ls_lock` protects a layout stateid’s layout segment list, recalled/fenced flags, and fence work checks.
- `ls_mutex` serializes layout operation processing on a layout stateid.
- Layout segment references hold a stateid reference; freeing segments drops those references.
- Delayed fence work takes an extra stateid reference while running.

Dependencies and integration:
- Uses layout-type operations from `pnfs.h`: flex-files, block, SCSI.
- Uses NFSv4 callback framework from `nfs4callback.c` for `CB_LAYOUTRECALL`.
- Uses kernel lease infrastructure through `lease_manager_operations`.
- Uses exportfs layout capability helpers for block layout support.
- Uses usermode helper `/sbin/nfsd-recall-failed` as fallback fencing notification when driver-specific fencing is absent.
- Emits pNFS tracepoints for allocation, recall, return, unhash, and failure cases.

Error handling and notable risks:
- Fencing retries indefinitely with exponential backoff up to `MAX_FENCE_DELAY` to avoid data corruption; administrator intervention may be required.
- Lease timeout handling carefully avoids duplicate fence-worker references by checking delayed-work state and rearming pending work.
- Layout return split handling is intentionally limited; a middle split logs and retains the full segment.
- `BUG_ON` assertions enforce assumptions such as successful file association and lease unlock arguments.
- Device-id maps are global and freed at pNFS shutdown; export `ex_devid_map` sharing relies on stable fsid matching.
- Recall conflict returns `nfserr_recallconflict` after initiating recalls of other layout stateids.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4layouts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4proc.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4proc.c

This file is the main NFSv4 server procedure dispatcher and operation implementation table for NFSD. It handles NFSv4 COMPOUND execution, filehandle operations, create/open/read/write metadata operations, server-side copy/offload, pNFS operation glue, xattrs, reply size estimation, operation ordering rules, and the exported NFSv4 `svc_version`.

Primary responsibilities:
- Implement many NFSv4 operation handlers used by the operation table.
- Enforce NFSv4.0/NFSv4.1 COMPOUND ordering and filehandle rules.
- Manage current and saved filehandles and current/saved stateids.
- Handle NFSv4 OPEN create/lookup semantics, including exclusive create verifier behavior.
- Validate writable/supported attributes, ACL/security-label support, and create/setattr attribute masks.
- Invoke lower NFSD VFS helpers for read, write, commit, create, remove, rename, link, readdir, readlink, xattr, fallocate, clone, copy, seek, and setattr.
- Manage server-side synchronous and asynchronous COPY, including inter-server copy support when enabled.
- Bridge pNFS protocol operations to layout drivers and layout state management.
- Compute maximum reply sizes for preflight response-space checks.
- Provide the NFSv4 procedure table and `nfsd_version4`.

Important entry points and exports:
- `nfsd4_proc_null()` handles NFSv4 NULL.
- `nfsd4_proc_compound()` is the central COMPOUND executor.
- `OPDESC()`, `nfsd4_cache_this_op()`, `nfsd4_max_reply()`, and `warn_on_nonidempotent_op()` are helper interfaces for operation metadata and encode safety.
- `nfsd4_spo_must_allow()` checks whether a compound includes a machine-credential-allowed operation.
- `nfsd4_has_active_async_copies()`, `nfsd4_async_copy_reaper()`, `nfsd4_shutdown_copy()`, and `nfsd4_cancel_copy_by_sb()` manage async COPY lifetime outside normal request execution.
- `nfsd_version4` exposes the NFSv4 service version with NULL and COMPOUND procedures.

Core COMPOUND flow:
- `nfsd4_proc_compound()` initializes response stream state, current/save filehandles, minor version, and disables request deferral.
- It rejects unsupported minor versions before other checks.
- `nfs41_check_op_ordering()` enforces NFSv4.1+ requirements for first operation/session context.
- For each decoded op, it honors decoder-preset status, validates filehandle presence, migrated exports, and response space for non-idempotent operations.
- It imports current stateid when configured, calls the operation handler, exports current stateid on success, clears stateid for operations flagged `OP_CLEAR_STATEID`, and performs wrongsec checks after putfh-like operations when required.
- It encodes either replay data or the operation result, increments per-op stats, clears replay state, and stops on first failing status.
- Current and saved filehandles are released at completion.

Open/create behavior:
- `nfsd4_open()` validates open/create combinations, reclaim rules, sessions, seqid/replay state, grace-period behavior, and open claims.
- `do_open_lookup()` performs regular path lookup or create, verifies the resulting object is regular, stores open-owner replay filehandle for v4.0, checks permissions, and sets change info.
- `nfsd4_create_file()` implements unchecked, guarded, exclusive, and exclusive4_1 create semantics with verifier stored via atime/mtime, ACL/security label handling, and post-create setattr.
- `do_open_fhandle()` handles claim-by-current-filehandle paths and delegation-current-filehandle behavior.
- `nfsd4_open_omfg()` handles decode-time seqid-mutating OPEN errors so v4.0 open-owner sequence state is still advanced correctly.

Major operation groups:
- Filehandle operations: `GETFH`, `PUTFH`, `PUTROOTFH`, `PUTPUBFH`, `SAVEFH`, `RESTOREFH`, and parent lookup.
- Metadata/data operations: `ACCESS`, `GETATTR`, `SETATTR`, `VERIFY`, `NVERIFY`, `READ`, `READ_PLUS`, `WRITE`, `COMMIT`, `READDIR`, `READLINK`, `CREATE`, `LINK`, `REMOVE`, `RENAME`, `SECINFO`, `SECINFO_NO_NAME`.
- State operations delegated to state code through the operation table: `CLOSE`, `LOCK`, `LOCKT`, `LOCKU`, `OPEN_CONFIRM`, `OPEN_DOWNGRADE`, `DELEGRETURN`, `RENEW`, client/session operations, `TEST_STATEID`, `FREE_STATEID`, and reclaim completion.
- NFSv4.2 operations: `ALLOCATE`, `DEALLOCATE`, `CLONE`, `COPY`, `COPY_NOTIFY`, `OFFLOAD_STATUS`, `OFFLOAD_CANCEL`, `SEEK`, and xattr operations.
- pNFS operations when enabled: `GETDEVICEINFO`, `LAYOUTGET`, `LAYOUTCOMMIT`, `LAYOUTRETURN`.

COPY/offload behavior:
- `nfsd4_verify_copy()` validates saved source and current destination stateids and ensures both files are regular.
- `nfsd4_setup_intra_ssc()` handles same-server copy setup.
- `nfsd4_setup_inter_ssc()` and related helpers handle inter-server source mounts when `CONFIG_NFSD_V4_2_INTER_SSC` is enabled.
- `nfsd4_copy()` dispatches synchronous or asynchronous copy. Async copies allocate a persistent copy object, create copy state, cap pending copies by server thread count, enqueue on the client async list, and start a kthread.
- `nfsd4_do_async_copy()` performs copy work, handles inter-server open/cleanup, records final status, updates cmtime for no-cmtime files, decrements pending async count, and sends `CB_OFFLOAD`.
- `nfsd4_offload_status()` reports active/completed async copy state.
- `nfsd4_offload_cancel()` cancels async copy or manages completed notification state.
- Reaper/shutdown/cancel-by-superblock paths prevent stale async copies from blocking client or filesystem teardown.

pNFS integration:
- `nfsd4_layout_verify()` checks export support and layout type bounds.
- `nfsd4_getdeviceinfo()` maps device IDs back to exports, calls layout driver `proc_getdeviceinfo`, and masks supported notification types.
- `nfsd4_layoutget()` validates iomode, permissions, ranges, layout stateid, recall conflicts, calls the layout driver, and records the granted layout.
- `nfsd4_layoutcommit()` validates size changes, grace/reclaim rules, layout stateid, calls driver commit, and marks delegation-written state.
- `nfsd4_layoutreturn()` validates iomode and return type, then delegates to layout-return helpers in `nfs4layouts.c`.

State and synchronization:
- Uses `struct nfsd4_compound_state` to track minor version, client/session, slot, current/save filehandles, current/save stateids, replay owner, and SPO machine-credential result.
- Async copy lists are protected by `clp->async_lock`; client hash/LRU scans use `nn->client_lock`.
- Pending async copy count is atomic per netns.
- Server-side inter-SSC mount list uses `nn->nfsd_ssc_lock` and wait queue coordination for busy mount entries.
- Filehandle pre/post attributes are cleared before each op and filled by VFS helpers for change-info replies.
- Non-idempotent ops are preflighted for response space to avoid performing mutations whose successful reply cannot be encoded.

Dependencies and integration:
- Calls extensive NFSD VFS helpers from `vfs.h`, state helpers from `state.h`, ACL helpers, idmap/XDR helpers, pNFS helpers, and tracepoints.
- Uses Linux VFS APIs for create, xattr, fallocate, llseek, fsync, mount, and file range copy.
- Uses kthreads for asynchronous copy and callback framework for `CB_OFFLOAD`.
- Uses SUNRPC request/transport constraints for payload sizing and response encoding.
- Uses NFSv4 stateid current-state hooks declared in operation descriptors.

Error handling and notable risks:
- COMPOUND execution stops on first failing op status but must still encode the failing operation correctly.
- Decoder-preset OPEN errors require special handling to preserve seqid semantics.
- Non-idempotent operations rely on reply-size estimates; underestimates risk warnings or protocol-visible failures after mutation.
- Async copy has multiple lifetime owners: client list, kthread, callback, reaper, cancel path, and filesystem teardown path.
- Inter-server copy is gated by module parameter and config; failures map to offload-denied/notsupp style protocol errors.
- pNFS layout operations must coordinate with layout recall state to avoid granting conflicting layouts.
- Several operations are grace-period sensitive and return `nfserr_grace` or `nfserr_no_grace` depending on reclaim state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4recover.c -->
# File Research: sources/os/linux/linux/fs/nfsd/nfs4recover.c

This file implements NFSD NFSv4 client recovery tracking. It abstracts multiple stable-storage tracking backends, loads reclaimable clients at server startup, records/removes stable client records, verifies reclaim eligibility during the grace period, and registers rpc_pipefs notifications for `nfsdcld` communication.

Primary responsibilities:
- Define the `nfsd4_client_tracking_ops` backend interface.
- Support modern `nfsdcld` rpc_pipefs client tracking, including v1 and v2 message formats.
- Support older `nfsdcld` v0 behavior.
- Optionally support legacy recovery directory tracking and usermode-helper `nfsdcltrack` when configured.
- Maintain per-netns reclaim hash tables used during grace/reclaim.
- Create, remove, and check stable client records.
- End grace periods and purge/release reclaim records.
- Register/unregister rpc_pipefs notifier hooks so the `cld` pipe appears as rpc_pipefs mounts come and go.

Backend abstraction:
- `struct nfsd4_client_tracking_ops` has `init`, `exit`, `create`, `remove`, `check`, `grace_done`, `version`, and `msglen`.
- `nfsd4_client_tracking_init()` selects a backend: modern `nfsdcld`, old `nfsdcld`, then legacy methods if enabled.
- Public wrappers dispatch through the selected backend:
  - `nfsd4_client_record_create()`
  - `nfsd4_client_record_remove()`
  - `nfsd4_client_record_check()`
  - `nfsd4_record_grace_done()`
  - `nfsd4_client_tracking_exit()`

Modern `nfsdcld` rpc_pipefs path:
- `struct cld_net` stores the rpc pipe, lock, outstanding upcall list, xid counter, and optional legacy-detected flag.
- `struct cld_upcall` tracks one in-flight upcall and completion.
- `__nfsd4_init_cld_pipe()` allocates pipe data, initializes state, and registers the pipe under `nfsd/cld` in rpc_pipefs.
- `alloc_cld_upcall()` assigns a unique xid and links the upcall under `cn_lock`.
- `cld_pipe_upcall()` queues the message and waits for userspace completion, retrying `-EAGAIN`.
- `cld_pipe_downcall()` matches userspace replies by xid, supports `-EINPROGRESS` grace-start streaming records, copies final replies, and completes waiters.
- `nfsd4_cld_get_version()` negotiates userspace protocol version and switches to v2 ops when available.
- `nfsd4_cld_grace_start()` asks userspace to stream reclaim records into NFSD.
- `nfsd4_cld_create()`, `nfsd4_cld_create_v2()`, and `nfsd4_cld_remove()` update stable records.
- `nfsd4_cld_check()`, `nfsd4_cld_check_v2()`, and `nfsd4_cld_check_v0()` verify reclaim eligibility.
- `nfsd4_cld_grace_done()` notifies userspace and releases in-kernel reclaim records.

v2 principal handling:
- v2 create messages include a SHA-256 hash of the raw principal or principal string when present.
- v2 check verifies the reclaim record’s principal hash against the reconnecting client’s principal before allowing reclaim.
- This tightens recovery identity matching beyond the client-provided opaque client name.

Legacy recovery directory path when enabled:
- Uses `/var/lib/nfs/v4recovery` by default, configurable through `nfs4_reset_recoverydir()`.
- Client records are directories named by MD5 hash of the NFSv4 client owner string.
- `nfsd4_create_clid_dir()` creates a hashed directory and fsyncs the recovery directory.
- `nfsd4_remove_clid_dir()` removes the directory and updates in-grace reclaim records.
- `nfsd4_recdir_load()` scans existing directory names into reclaim records at startup.
- `nfsd4_recdir_purge_old()` removes entries not reclaimed by the end of grace.
- Legacy filesystem operations override credentials to global root while accessing the recovery directory.
- Legacy tracking is rejected for non-init network namespaces.

Usermode-helper `nfsdcltrack` path when enabled:
- Uses module parameter `cltrack_prog`, default `/sbin/nfsdcltrack`.
- Supports `init`, `create`, `remove`, `check`, and `gracedone` commands.
- Passes environment values for legacy topdir/recovery dir, whether the client has a session, and grace start time.
- Serializes per-client upcalls with `NFSD4_CLIENT_UPCALL_LOCK`.
- Disables the helper path by blanking `cltrack_prog` on `-ENOENT` or `-EACCES`.

State and synchronization:
- Reclaim hash tables live in `struct nfsd_net` and are allocated by `nfs4_cld_state_init()` or legacy state init.
- `track_reclaim_completes` and `nr_reclaim_complete` are initialized for cld tracking.
- `cn_lock` protects in-flight cld upcalls and xid allocation.
- Completions wake blocked kernel upcall senders after userspace downcalls.
- Legacy directory operations use mount write counts and fsync to make stable record updates durable.
- rpc_pipefs notifier callbacks take a module reference while registering/unlinking pipes on mount/umount events.

Dependencies and integration:
- Uses crypto MD5 for legacy directory names and SHA-256 for v2 principal hashes.
- Uses rpc_pipefs and SUNRPC pipe APIs for `nfsdcld`.
- Uses NFSD reclaim helpers such as `nfs4_client_to_reclaim`, `nfsd4_find_reclaim_client`, `nfs4_remove_reclaim_record`, `nfs4_release_reclaim`, and `nfs4_has_reclaimed_state`.
- Uses Linux VFS APIs for directory scanning, mkdir/rmdir, fsync, path lookup, and credential override.
- Called by NFSv4 state management during client create, reclaim, client expiry, grace completion, and server startup/shutdown.

Error handling and notable risks:
- `nfsd4_client_tracking_init()` warns and disables tracking if all backends fail; without tracking, reclaim support is unavailable.
- Modern cld init waits briefly for userspace to open the pipe to avoid 30-second pipe upcall timeouts.
- Downcall matching depends on xid uniqueness and userspace returning exact message sizes.
- `-EINPROGRESS` downcalls stream reclaim records during grace start and do not complete the original upcall.
- v2 principal mismatch denies reclaim even if the client name matches.
- Legacy recovery directory names are MD5 hashes for compatibility, not collision-resistant identity proofs.
- Usermode helper execution is unavailable in non-init netns and can be permanently disabled until reset if the helper is missing or not executable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfsd/nfs4recover.c -->