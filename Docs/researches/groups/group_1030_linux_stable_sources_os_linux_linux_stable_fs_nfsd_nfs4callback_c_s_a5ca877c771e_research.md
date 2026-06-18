# Group Research: group_1030_linux_stable_sources_os_linux_linux_stable_fs_nfsd_nfs4callback_c_s_a5ca877c771e

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4callback.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4callback.c

Purpose: implements the NFSD server-side NFSv4 callback RPC client. It builds and sends backchannel callbacks to NFSv4 clients for delegation recall, callback getattr, layout recall, lock notification, copy offload completion, and recall-any pressure.

Key structures and state:
- `nfs4_cb_compound_hdr` tracks CB_COMPOUND encoding state: minor version, callback ident, op count pointer, and decoded status.
- Per-net callback program resources are owned by `struct nfsd_net_cb`, initialized by `nfsd_net_cb_init()` and released by `nfsd_net_cb_shutdown()`.
- Callback execution is carried by `struct nfsd4_callback`, tied to `struct nfs4_client`, an RPC message, optional operation callbacks, flags, held backchannel slot, and referring-call lists.
- NFSv4.1+ callback slot state lives in `nfsd4_session`: `se_cb_slot_avail`, `se_cb_highest_slot`, and `se_cb_seq_nr`.

Major logic:
- XDR helpers encode/decode callback primitives: stateids, filehandles, sessionids, bitmaps, empty arrays, attributes, CB_COMPOUND headers, and operation statuses.
- Callback operation encoders cover `CB_GETATTR`, `CB_RECALL`, `CB_RECALL_ANY`, optional `CB_LAYOUTRECALL`, `CB_NOTIFY_LOCK`, and `CB_OFFLOAD`.
- Callback decoders validate CB_COMPOUND, optional `CB_SEQUENCE`, and the expected callback op result, then map NFS status codes to Linux errno-style values with `nfs_cb_stat_to_errno()`.
- `encode_cb_sequence4args()` and `decode_cb_sequence4resok()` implement the NFSv4.1 backchannel sequencing contract, including session ID, sequence number, slot ID, and target highest slot updates.
- `nfsd4_cb_sequence_done()` decides whether to advance sequence numbers, retry, requeue, mark the backchannel faulty, or leak a bad slot after protocol synchronization errors.
- `setup_callback_client()` constructs the RPC client differently for v4.0 callback addresses versus v4.1+ backchannel transports and credentials.
- `nfsd4_process_cb_update()` serializes callback transport updates, shuts down stale clients, finds a backchannel connection, and creates a new callback RPC client.
- `nfsd4_run_cb_work()` is the workqueue entry point: refreshes callback channel state, prepares operation-specific data, and launches the asynchronous RPC call.

Concurrency and lifetime:
- Callback work is serialized by `cl_callback_wq`; comments explicitly rely on no two callback work items running concurrently for one client.
- Backchannel slots are protected by `ses->se_lock`; waiters sleep on `cl_cb_waitq`.
- In-flight callback accounting uses `cl_cb_inflight` and `wait_var_event()` so shutdown can wait for all callbacks to drain.
- Referring-call list entries are dynamically allocated and must be destroyed with `nfsd41_cb_destroy_referring_call_list()`.
- Callback release either requeues a callback or destroys it, releasing slots, waking waiters, invoking operation release hooks, and decrementing in-flight count.

Important dependencies:
- Uses SunRPC client APIs: `rpc_create`, `rpc_call_async`, `rpc_restart_call_prepare`, `rpc_sleep_on`, and `rpc_shutdown_client`.
- Integrates with NFSD state objects from `state.h`, per-net state from `netns.h`, callback XDR size definitions from `xdr4cb.h`, generated XDR helpers from `nfs4xdr_gen.h`, and tracing from `trace.h`.
- Optional pNFS callback support is gated by `CONFIG_NFSD_PNFS`.

Risk/edge cases:
- CB_SEQUENCE mismatches are treated as serious backchannel faults because the server cannot trust client slot state.
- RPC-level failure leaves `cb_seq_status` at sentinel value `1`, causing conservative recovery behavior.
- `max_cb_time()` assumes the NFSv4 lease is at most one hour and warns if that invariant changes.
- For NFSv4.1+ callbacks, missing backchannel transport or session rejects callback client setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4idmap.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4idmap.c

Purpose: implements NFSD NFSv4 owner/group ID mapping between local numeric UID/GID values and protocol names. It provides bidirectional SunRPC cache-backed upcalls to userspace idmapd, with numeric fallback for AUTH_SYS when configured.

Key structures and state:
- `struct ent` is the common cache entry for both directions. It stores cache metadata, user/group type, numeric ID, mapped name, authentication domain name, and RCU free state.
- Two per-net cache instances are created from templates:
  - `nfs4.idtoname`: local numeric ID plus auth domain to NFSv4 owner/group name.
  - `nfs4.nametoid`: NFSv4 owner/group name plus auth domain to local numeric ID.
- Module parameter `nfs4_disable_idmapping` defaults true and disables idmapping for `sec=sys` when numeric owner strings can be used.

Major logic:
- Common cache operations allocate, initialize, update, and free `struct ent` entries via SunRPC cache infrastructure.
- `idtoname_request()` and `nametoid_request()` format pipe upcall requests to userspace with qword-escaped fields.
- `idtoname_parse()` and `nametoid_parse()` parse userspace downcalls, validate field lengths, set expiry times, support negative entries, and update cache entries.
- `nfsd_idmap_init()` creates and registers both per-net caches; shutdown unregisters and destroys them in reverse.
- `idmap_lookup()` wraps cache lookup/check behavior and retries if a timed-out item is replaced.
- `rqst_authname()` selects the GSS client auth domain when present, otherwise the normal RPC client domain.
- `idmap_name_to_id()` maps incoming owner/group strings to local IDs and returns `nfserr_badowner` for missing mappings.
- `idmap_id_to_name()` maps local IDs to protocol names and falls back to ASCII numeric strings if id-to-name mapping is absent.
- Public APIs `nfsd_map_name_to_uid()`, `nfsd_map_name_to_gid()`, `nfsd4_encode_user()`, and `nfsd4_encode_group()` bridge protocol XDR and kernel user namespace IDs.

Concurrency and lifetime:
- Cache entries are freed with `kfree_rcu()`.
- Per-net cache lifetimes are owned by `nfsd_net`.
- Name/ID mapping upcalls explicitly require `RQ_USEDEFERRAL` to be clear, because NFSv4 compounds cannot safely be dropped or deferred.

Important dependencies:
- Uses SunRPC cache APIs, qword parsing, and cache pipe upcalls.
- Uses `nfsd_user_namespace()` to translate through the server request’s user namespace.
- Uses `nfserrno()`/NFS status conversion and XDR stream encoding for owner/group attributes.

Risk/edge cases:
- Names longer than `IDMAP_NAMESZ - 1` are rejected as bad owners.
- Numeric fallback accepts only valid unsigned decimal strings that fit in a 32-bit ID.
- Empty names are invalid for incoming owner/group mapping.
- `sec=sys` behavior differs from RPCSEC_GSS because numeric strings are preferred when idmapping is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4layouts.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4layouts.c

Purpose: implements NFSD pNFS layout state management, device ID mapping, layout grant/return bookkeeping, layout recall callbacks, and fencing behavior for layout-capable exports.

Key structures and state:
- `struct nfs4_layout` records one granted layout segment and links it to a layout stateid.
- `struct nfs4_layout_stateid` objects are allocated from `nfs4_layout_stateid_cache` and track per-client/per-file layout state, granted segments, recall callback, lease, fencing work, and layout type.
- `nfsd4_layout_ops[]` dispatches layout-type-specific operations for flexfile, block, and SCSI layouts depending on config.
- Device IDs are mapped to export fsids by `struct nfsd4_deviceid_map` entries in an RCU-protected hash table guarded by `nfsd_devid_lock`.

Major logic:
- `nfsd4_setup_layout_type()` enables export layout types based on export flags and filesystem export operations.
- `nfsd4_set_deviceid()` allocates or reuses an export fsid-to-device-ID mapping and stores generation data in the protocol deviceid.
- `nfsd4_alloc_layout_stateid()` creates a layout stateid from an open/lock/delegation stateid, finds an associated `nfsd_file`, installs a layout lease unless recalls are disabled, and links the state to client and file lists.
- `nfsd4_preprocess_layout_stateid()` validates layout stateids, creates one if allowed, checks filehandle match, layout type consistency, and stateid generation ordering.
- Segment helpers compute layout end offsets, merge compatible adjacent/overlapping segments, detect overlap, and update lengths safely with `NFS4_MAX_UINT64`.
- `nfsd4_insert_layout()` recalls conflicting layout states for other clients, merges or allocates a segment, and updates the layout stateid returned to the client.
- Layout return paths handle file-specific, fsid, all-client, all-file, and all-client cleanup by moving segments to reap lists and dropping stateid references.
- Recall logic uses `nfsd4_recall_file_layout()` to mark a layout recalled, increment file recall counters, and run `CB_LAYOUTRECALL`.
- Recall completion polls for layout return until two lease periods, then fences the client using layout driver support or `/sbin/nfsd-recall-failed`.
- Lease manager hooks convert VFS lease breaks into layout recalls and schedule fencing on timeout.

Concurrency and lifetime:
- Client layout lists are protected by `cl_lock`; file layout lists by `fi_lock`; per-layout segment lists by `ls_lock`; stateid operations serialize with `ls_mutex`.
- Layout segments hold references on their layout stateids and are freed via reap lists outside lock-heavy paths.
- Delayed fencing work holds a stateid reference while it runs and re-arms itself to prevent duplicate timeout references.
- Layout stateid freeing cancels pending fence work, unlinks from client/file lists, closes the layout lease, adjusts recall counters, and frees cache memory.

Important dependencies:
- Uses callback infrastructure from `nfs4callback.c` for `CB_LAYOUTRECALL`.
- Uses VFS lease APIs (`kernel_setlease`, `lease_modify`) to integrate pNFS recalls with local file access conflicts.
- Delegates layout-type-specific behavior to `proc_getdeviceinfo`, `proc_layoutget`, `proc_layoutcommit`, and optional `fence_client`.

Risk/edge cases:
- Split layout returns are not supported; the code retains the whole segment when a return would split it.
- Fencing retries indefinitely with exponential backoff to avoid data corruption if client fencing fails.
- Device ID mappings are freed at pNFS exit without RCU grace waiting in this file; callers must respect module/global teardown assumptions.
- Layout conflict handling recalls all other layout states on the same file before granting a new layout.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4layouts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4proc.c

Purpose: implements the NFSD NFSv4 server procedure layer: the NULL and COMPOUND RPC procedures, most NFSv4 operation handlers, NFSv4.2 server-side copy/offload support, pNFS operation glue, reply size estimation, operation ordering checks, and the operation descriptor table.

Key structures and state:
- The central runtime object is `struct nfsd4_compound_state`, populated for each COMPOUND with current/saved filehandles, current/saved stateids, client/session state, and replay state.
- Operation handlers consume `union nfsd4_op_u` fields decoded by XDR code and return NFS status codes.
- `nfsd4_ops[]` maps each NFSv4 op number to handler, release hook, flags, reply size estimator, stateid getter/setter hooks, and operation name.
- Async NFSv4.2 COPY state is managed by `struct nfsd4_copy` entries on per-client `async_copies`, with flags for completed/stopped/offload callback state.

Major logic:
- Attribute validation is centralized in `check_attr_support()`, including ACL, POSIX ACL, security label, writable-mask, and `MODE_UMASK` conflict checks.
- OPEN handling implements NFSv4 create/open claim semantics, sequence/replay behavior, grace-period checks, reclaim checks, exclusive verifier handling, permission checks, delegation claim handling, and final state creation via state-layer helpers.
- Filehandle ops (`PUTFH`, `PUTROOTFH`, `SAVEFH`, `RESTOREFH`, `GETFH`, lookup variants) maintain current/saved handles and preserve current stateid where required.
- VFS-backed ops include access, commit, create, getattr, link, read, readdir, readlink, remove, rename, setattr, write, verify/nverify, xattrs, allocate/deallocate, clone, seek, and read-plus dispatch through read.
- SETATTR handles size changes and delegated attribute updates with stateid validation; delegated time attributes are vetted against delegation timestamps and current inode time.
- WRITE validates offset bounds, preprocesses write stateid, marks write-attrs delegations as written, calls `nfsd_vfs_write()`, and returns verifier/stability data.
- NFSv4.2 COPY supports intra-server copy and optional inter-server server-side copy. Async copy uses a kernel thread, per-net pending limits, callback stateid allocation, `CB_OFFLOAD`, offload status, and offload cancel.
- Inter-server copy support mounts the source server internally via NFS when `CONFIG_NFSD_V4_2_INTER_SSC` is enabled and the module parameter allows it.
- pNFS handlers validate layout type support, handle `GETDEVICEINFO`, `LAYOUTGET`, `LAYOUTCOMMIT`, and `LAYOUTRETURN`, and call layout driver operations plus `nfs4layouts.c` bookkeeping.
- `nfsd4_proc_compound()` drives execution: initializes response, validates minor version and NFSv4.1 operation ordering, clears deferral, iterates operations, checks filehandle/migration/wrongsec constraints, preflights reply size for non-idempotent operations, invokes handlers, updates current stateid, encodes replies, handles replay, and updates stats.
- Reply size helpers estimate maximum encoded response space for each op so mutating operations are not executed if their success reply cannot be encoded.
- `nfsd_version4` exposes the RPC version with NULL and COMPOUND procedures.

Concurrency and lifetime:
- Async copy lifecycle is protected by `clp->async_lock`, per-net client locks during cancellation scans, reference counts on copy objects, and explicit `nfsd_file` references.
- COMPOUND processing clears `RQ_USEDEFERRAL` to avoid non-idempotency problems.
- Operation release hooks release per-op resources such as read file references, lock denial owners, secinfo exports, layout buffers, and getdeviceinfo buffers.
- Client shutdown and superblock teardown can cancel active async copies safely.

Important dependencies:
- Delegates stateful open/lock/session/clientid operations to `nfs4state.c` through externally declared handlers referenced in `nfsd4_ops[]`.
- Uses `nfs4idmap.c` indirectly through attribute encode/decode paths for owner/group names.
- Uses `nfs4layouts.c` for pNFS layout state and `nfs4callback.c` for async offload callbacks.
- Uses VFS helper layer from `vfs.h`, ACL conversion from `acl.h`, current-stateid helpers, tracepoints, and per-net NFSD state.

Risk/edge cases:
- OPEN is specially handled when XDR decoding fails with a seqid-mutating error so the openowner seqid can still be advanced.
- Non-idempotent operations are guarded by reply size preflight; failures here prevent performing changes whose success could not be encoded.
- COPY async error handling intentionally reports success if bytes were written and lets clients query completion/error state later.
- Inter-server copy can mark saved source filehandles as foreign to tolerate stale local verification for COPY compounds.
- Grace-period checks differ for opens, locks/layout commits, and reclaim paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4recover.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4recover.c

Purpose: implements NFSv4 client recovery tracking for NFSD. It records clients on stable storage, reloads reclaimable clients after reboot, validates reclaim attempts during grace, and supports multiple tracking backends: `nfsdcld` rpc_pipefs, older nfsdcld protocol, usermode-helper `nfsdcltrack`, and optional legacy recovery directories.

Key structures and state:
- `struct nfsd4_client_tracking_ops` abstracts backend operations: init, exit, create, remove, check, grace_done, version, and message length.
- Legacy tracking stores MD5-hashed client-name directories under `/var/lib/nfs/v4recovery` by default.
- `struct cld_net` owns the rpc_pipefs pipe, outstanding upcall list, XID allocator, and legacy-detection flag.
- `struct cld_upcall` represents one synchronous nfsdcld upcall/downcall transaction.
- Reclaimable clients are loaded into `nn->reclaim_str_hashtbl`, shared with state recovery logic.

Major logic:
- Legacy directory mode overrides credentials to root, opens the recovery directory, creates/removes per-client directories, fsyncs stable storage, loads existing directory names into reclaim records, and purges non-reclaimed records after grace.
- Legacy client names are MD5 hex digests with fixed `HEXDIR_LEN`; v2 cld principal protection uses SHA-256 of the authenticated principal when available.
- rpc_pipefs mode creates an `nfsd/cld` pipe, queues upcalls, waits for completions, handles pipe reopen `-EAGAIN`, and processes downcalls by XID.
- `__cld_pipe_inprogress_downcall()` handles `Cld_GraceStart` streaming downcalls that populate reclaim records while the daemon is still processing startup.
- nfsdcld v0 checks each client directly; newer nfsdcld versions slurp clients at grace start and then check the in-kernel reclaim hash.
- v2 nfsdcld create/check includes principal hash data, preventing a client name alone from authorizing reclaim when a principal hash is recorded.
- Grace completion notifies the selected backend and releases in-kernel reclaim records when appropriate.
- UMH `nfsdcltrack` backend formats command arguments and environment variables for init/create/remove/check/gracedone, including legacy conversion paths and whether the client has sessions.
- `nfsd4_client_tracking_init()` chooses a backend: modern nfsdcld, older nfsdcld v0 fallback, then optional UMH/legacy methods if configured.
- Public wrappers `nfsd4_client_record_create/remove/check()` and `nfsd4_record_grace_done()` dispatch through the selected backend.
- rpc_pipefs mount/umount notifier registers or unlinks the cld pipe when rpc_pipefs instances appear or disappear.

Concurrency and lifetime:
- cld upcall lists and XID allocation are protected by `cn_lock`.
- Upcalls wait on completions; failed queued pipe messages complete waiters in `cld_pipe_destroy_msg()`.
- UMH client tracking serializes per-client create/remove/check with `NFSD4_CLIENT_UPCALL_LOCK`.
- Legacy directory iteration first builds an in-memory namelist to avoid mutating a directory while iterating it directly.
- Backend init/shutdown owns reclaim hash allocation and pipe or directory references per network namespace.

Important dependencies:
- Uses crypto MD5 and SHA-256 helpers for stable client identifiers and principal hashes.
- Uses rpc_pipefs APIs for nfsdcld communication and usermodehelper APIs for `nfsdcltrack`.
- Integrates with NFSD state recovery via `nfs4_client_to_reclaim()`, `nfsd4_find_reclaim_client()`, `nfs4_release_reclaim()`, and `nfs4_has_reclaimed_state()`.

Risk/edge cases:
- Legacy and UMH backends are rejected in non-init network namespaces.
- Missing or non-executable `nfsdcltrack` disables the UMH program path until an admin re-enables it.
- nfsdcld startup waits briefly for pipe readers/writers to avoid 30-second upcall timeouts during backend probing.
- Principal-hash mismatch in v2 tracking rejects reclaim even if the client name matches.
- If recovery tracking cannot initialize, NFSD warns that `nfsdcld` may not be running or legacy tracking may need enabling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4recover.c -->