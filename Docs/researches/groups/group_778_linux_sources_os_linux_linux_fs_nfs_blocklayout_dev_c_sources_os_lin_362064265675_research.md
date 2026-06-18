# Group Research: group_778_linux_sources_os_linux_linux_fs_nfs_blocklayout_dev_c_sources_os_lin_362064265675

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/dev.c -->
# File Research: sources/os/linux/linux/fs/nfs/blocklayout/dev.c

## Purpose
Implements pNFS block layout device-id decoding and device mapping. It turns XDR-encoded pNFS block volume descriptions into `pnfs_block_dev` trees backed by local block devices, including simple, sliced, concatenated, striped, and SCSI persistent-reservation-capable volumes.

## Main Responsibilities
- Decode pNFS block volume records from `GETDEVICEINFO` XDR payloads.
- Resolve simple volumes through the blocklayout userspace pipefs helper.
- Resolve SCSI volumes through stable `/dev/disk/by-id/` names.
- Open block devices for read/write access and attach them to device-id nodes.
- Build recursive device trees for slices, concatenations, and stripes.
- Register/unregister SCSI persistent reservation keys where required.
- Map logical block-layout offsets to underlying block devices and disk offsets.

## Key Functions
- `bl_register_dev()` recursively registers leaf SCSI devices with persistent reservations and unwinds partial success on failure.
- `bl_free_deviceid_node()` frees an NFS device-id node, recursively unregistering reservations, releasing child arrays, and `fput()`ing block-device files.
- `nfs4_block_decode_volume()` decodes one volume descriptor and validates counts, signature lengths, designator lengths, and volume type.
- `bl_map_simple()`, `bl_map_concat()`, and `bl_map_stripe()` implement the logical-to-physical mapping callbacks stored in each parsed device.
- `bl_parse_simple()` asks userspace to resolve a simple signature volume to `dev_t`, then opens the block device by device number.
- `bl_parse_scsi()` validates SCSI designators, opens by-id paths, stores the PR key, and verifies the device supports reservation operations.
- `bl_parse_slice()`, `bl_parse_concat()`, and `bl_parse_stripe()` recursively assemble derived devices from earlier decoded volume indices.
- `bl_alloc_deviceid_node()` is the top-level allocator/parser used by pNFS device-id cache code.

## Control Flow
`bl_alloc_deviceid_node()` allocates an XDR scratch folio, decodes the volume count, allocates an array of `pnfs_block_volume`, decodes each volume, allocates the top `pnfs_block_dev`, and parses the last volume as the root device. The resulting `nfs4_deviceid_node` is initialized even if parsing fails; on failure it is marked unavailable.

## Data and Ownership
- `pnfs_block_dev` owns child arrays for compound devices and a `struct file *bdev_file` for leaf devices.
- Device-id nodes are freed via RCU with `kfree_rcu()`.
- Leaf block devices are released with `fput()`.
- SCSI PR registration state is tracked with `PNFS_BDEV_REGISTERED`.

## Dependencies
Uses Linux block layer APIs (`bdev_file_open_by_dev`, `bdev_file_open_by_path`, `file_bdev`, `bdev_nr_bytes`), SUNRPC XDR helpers, pNFS device-id infrastructure, and tracepoints from `nfs4trace.h`.

## Notable Details
- Simple volume decoding preserves a byte length used later by `rpc_pipefs.c` to re-encode the volume for userspace.
- SCSI resolution tries `dm-uuid-mpath-0x`, then `wwn-0x`, then `nvme-eui.` path prefixes.
- SCSI designator support is deliberately narrow: EUI64 and NAA binary designators are accepted; T10 and NAME are rejected.
- Stripe mapping computes the child index from logical chunk number and child count, then maps through the child.

## Risks and Edge Cases
- Recursive parse failures in concat/stripe can leave partially initialized children, but final device free paths can clean recursively once attached.
- Stripe parsing does not validate `chunk_size` for zero before use; correctness depends on server-provided layout validity.
- `nr_volumes` is used for allocation and indexing without an explicit upper bound at the top level; individual child lists are bounded by `PNFS_BLOCK_MAX_DEVICES`.
- SCSI PR support is mandatory for SCSI layouts; devices without `pr_ops` fail parsing.

## Integration Points
This file is used by the pNFS block layout driver’s device-id cache and layout I/O path. `bl_resolve_deviceid()` is implemented in `rpc_pipefs.c`, while extent-to-device mapping is consumed by the block layout read/write path outside this file.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/extent_tree.c -->
# File Research: sources/os/linux/linux/fs/nfs/blocklayout/extent_tree.c

## Purpose
Manages pNFS block layout extent state in red-black trees. It tracks read-only and read/write extents, performs insertion/removal/splitting/merging, marks written extents, and encodes layoutcommit updates back to the NFS server.

## Main Responsibilities
- Store block extents in two interval-like rbtrees: read-only and read/write.
- Merge adjacent compatible extents.
- Remove or split extents over recalled or overwritten ranges.
- Look up extents for I/O mapping.
- Track invalid extents that have been written and need layoutcommit.
- Encode block or SCSI layoutcommit updates into XDR buffers.
- Update extent state after layoutcommit succeeds or fails.

## Key Functions
- `ext_tree_insert()` inserts a new extent into the correct tree, trimming or splitting around overlaps.
- `ext_tree_lookup()` finds an extent covering a sector, preferring read-only only when `rw` is false, then checking read/write extents.
- `ext_tree_remove()` removes a range from read-only and optionally read/write trees.
- `ext_tree_mark_written()` removes conflicting COW/hole ranges and marks written invalid extents as `EXTENT_WRITTEN`.
- `ext_tree_prepare_commit()` allocates layoutupdate storage and encodes all or as many written extents as fit.
- `ext_tree_mark_committed()` converts committing invalid extents to read/write extents on success or back to written on failure.
- Internal helpers handle rbtree search, insert, remove, split, and left/right merge.

## Control Flow
Extent insertion chooses `bl_ext_rw` for `READWRITE_DATA` and `INVALID_DATA`, and `bl_ext_ro` for `READ_DATA` and `NONE_DATA`. It searches for overlap under `bl_ext_lock`, inserts directly when no overlap exists, drops fully covered extents, trims partially covered extents, or duplicates/splits new extents as necessary.

Layoutcommit preparation first tries a single page. If that cannot fit all written extents, it allocates a larger vmalloc buffer sized to the server write size and encodes a partial set if still necessary.

## Data and Ownership
- Each `pnfs_block_extent` owns a reference to its `be_device`.
- Merging or deleting extents releases device references with `nfs4_put_deviceid_node()`.
- Removed extents are staged on a temporary list while under spinlock, then freed after unlock.
- Commit data may use a single page or a vmalloc-backed page array; `ext_tree_free_commitdata()` frees either representation.

## Locking
`bl->bl_ext_lock` protects both extent trees and `bl_lwb`. Allocation inside locked paths uses `GFP_ATOMIC` where needed. Freeing removed extents is deferred until after the spinlock is released.

## Encoding Behavior
- Block layouts encode deviceid, file offset, length, zero storage offset, and `PNFS_BLOCK_READWRITE_DATA`.
- SCSI layouts encode only offset and length ranges.
- `lastbytewritten` is `bl_lwb - 1` when all pending extents fit; for partial commits it is the last byte covered by the last encoded extent.

## Notable Details
- `PNFS_BLOCK_NONE_DATA` extents can merge without virtual-offset continuity.
- `PNFS_BLOCK_INVALID_DATA` extents also require matching `be_tag` to merge.
- `ext_tree_mark_written()` only marks invalid extents with tag `0`; already tagged extents are skipped.
- On layoutcommit failure, committing extents return to `EXTENT_WRITTEN` for retry.

## Risks and Edge Cases
- `ext_tree_encode_commit()` uses `be_prev` when the buffer fills; this assumes at least one extent was encoded before `-ENOSPC`.
- Some error paths convert allocation failure to `-EINVAL` in `ext_tree_insert()` split handling.
- The rbtree implementation assumes non-overlap invariants; unexpected overlap in raw insert triggers `BUG()`.
- Sector-to-byte shifts must remain consistent with protocol sizes.

## Integration Points
This file backs pNFS block layout I/O, recall handling, and `LAYOUTCOMMIT`. It depends on `blocklayout.h` structures and NFS layoutcommit argument structures from core NFSv4 code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/extent_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/rpc_pipefs.c -->
# File Research: sources/os/linux/linux/fs/nfs/blocklayout/rpc_pipefs.c

## Purpose
Provides the rpc_pipefs userspace upcall path for pNFS blocklayout simple-volume device resolution. Kernel code sends encoded block volume signatures to a userspace daemon and receives major/minor device numbers in response.

## Main Responsibilities
- Encode simple block volume signatures for userspace.
- Queue blocklayout device-mount requests on an rpc_pipefs pipe.
- Wait for userspace downcall replies.
- Expose per-network-namespace blocklayout pipe entries under rpc_pipefs.
- Register/unregister pipefs mount event notifiers.

## Key Functions
- `nfs4_encode_simple()` encodes one simple volume and its signatures into XDR-style data.
- `bl_resolve_deviceid()` serializes a `BL_DEVICE_MOUNT` request, queues it to the pipe, waits, and returns `dev_t`.
- `bl_pipe_downcall()` copies a `bl_dev_msg` reply from userspace into per-net state and wakes waiters.
- `bl_pipe_destroy_msg()` wakes the waiter if the upcall is destroyed with an error.
- `nfs4blocklayout_register_sb()` creates the `blocklayout` pipe dentry.
- `rpc_pipefs_event()` handles pipefs mount/unmount by linking or unlinking the pipe.
- `nfs4blocklayout_net_init()` and `_exit()` allocate/destroy per-net pipe data.
- `bl_init_pipefs()` and `bl_cleanup_pipefs()` manage global notifier and pernet registration.

## Control Flow
`bl_resolve_deviceid()` locks `nn->bl_mutex`, builds a pipe message, queues it, sleeps uninterruptibly on `nn->bl_wq`, then validates that userspace returned `BL_DEVICE_REQUEST_PROC`. On success it constructs `MKDEV(reply->major, reply->minor)`.

## Data and Ownership
- Per-net state stores `bl_device_pipe`, `bl_wq`, `bl_mutex`, and `bl_mount_reply`.
- Upcall message data is heap-allocated per request and freed before unlock.
- The single mutex serializes blocklayout device resolution per network namespace.

## Dependencies
Uses SUNRPC rpc_pipefs APIs, net namespace NFS state, blocklayout private message structures, and kernel wait queues.

## Notable Details
- `b->simple.len` is incremented by four bytes to account for a single-volume wrapper before the upcall is built.
- Requests larger than `PAGE_SIZE` are rejected.
- The wait is uninterruptible and has no local timeout; progress depends on userspace or pipe destruction waking the waitqueue.
- Pipe registration is lazy per rpc_pipefs mount and per net namespace.

## Risks and Edge Cases
- One global per-net reply slot means the mutex is essential; any future parallelization must preserve reply association.
- The uninterruptible sleep can hang if neither userspace nor pipe destruction responds.
- `bl_pipe_downcall()` accepts only exact `struct bl_dev_msg` size replies.
- `rpc_pipefs_event()` uses module references to avoid unload during mount/umount notification.

## Integration Points
Called by `dev.c` through `bl_resolve_deviceid()`. The userspace daemon is part of the pNFS blocklayout ecosystem and must understand the `BL_DEVICE_MOUNT` message format.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/blocklayout/rpc_pipefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/cache_lib.c -->
# File Research: sources/os/linux/linux/fs/nfs/cache_lib.c

## Purpose
Provides shared helper routines for NFS client cache upcalls and cache pipefs registration. It supports synchronous userspace cache lookup helpers and deferred cache request completion.

## Main Responsibilities
- Invoke `/sbin/nfs_cache_getent` or a configured helper for cache misses.
- Disable broken helper execution after `ENOENT` or `EACCES`.
- Allocate, reference, complete, and free deferred cache requests.
- Register and unregister NFS cache details with rpc_pipefs per superblock or per network namespace.

## Key Functions
- `nfs_cache_upcall()` calls the configured helper with cache name and entry name.
- `nfs_cache_defer_req_alloc()` allocates and initializes a deferred cache request with completion and refcount.
- `nfs_cache_wait_for_upcall()` waits for completion up to `cache_getent_timeout`.
- `nfs_cache_register_sb()` registers a `cache_detail` under the `cache` rpc_pipefs directory.
- `nfs_cache_register_net()` initializes cache detail and registers it if rpc_pipefs is mounted.
- `nfs_cache_unregister_net()` unregisters pipefs state and destroys cache detail.

## Control Flow
A cache miss can allocate `nfs_cache_defer_req`, install its defer callback, trigger a userspace upcall, and wait for `nfs_dns_cache_revisit()` to complete the request. Pipefs registration uses `rpc_get_sb_net()` to register only when an rpc_pipefs superblock exists for the net namespace.

## Data and Ownership
- `nfs_cache_defer_req` is refcounted.
- Deferred request revisit completes the waiter and drops the defer reference.
- `sunrpc_init_cache_detail()` and `sunrpc_destroy_cache_detail()` bracket cache-detail lifetime.

## Configuration
- `cache_getent` module parameter controls helper path.
- `cache_getent_timeout` controls wait duration in seconds.
- Default helper path is `/sbin/nfs_cache_getent`.
- Default timeout is 15 seconds.

## Risks and Edge Cases
- Helper path is disabled in memory after `ENOENT` or `EACCES`, requiring admin reset through module parameters.
- `nfs_cache_register_net()` returns success if rpc_pipefs is not mounted, so consumers must tolerate delayed registration.
- Waiting callers see `-ETIMEDOUT` if completion does not arrive before the configured timeout.

## Integration Points
Used by NFS client cache implementations that rely on SUNRPC cache infrastructure and rpc_pipefs exposure.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/cache_lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/cache_lib.h -->
# File Research: sources/os/linux/linux/fs/nfs/cache_lib.h

## Purpose
Declares shared NFS client cache helper structures and APIs implemented in `cache_lib.c`.

## Main Contents
- Defines `struct nfs_cache_defer_req`, wrapping:
  - `struct cache_req req`
  - `struct cache_deferred_req deferred_req`
  - `struct completion completion`
  - `refcount_t count`
- Declares cache upcall and deferred request helpers.
- Declares rpc_pipefs registration helpers for network namespaces and superblocks.

## Exported API
- `nfs_cache_upcall()`
- `nfs_cache_defer_req_alloc()`
- `nfs_cache_defer_req_put()`
- `nfs_cache_wait_for_upcall()`
- `nfs_cache_register_net()`
- `nfs_cache_unregister_net()`
- `nfs_cache_register_sb()`
- `nfs_cache_unregister_sb()`

## Dependencies
Includes Linux completion, SUNRPC cache, and atomic/refcount headers.

## Integration Points
Included by NFS cache implementations needing deferred upcall behavior or pipefs cache registration.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/cache_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback.c -->
# File Research: sources/os/linux/linux/fs/nfs/callback.c

## Purpose
Creates, starts, authenticates, and tears down the NFSv4 callback RPC service. This is the server-side service inside the NFS client that receives callbacks from NFSv4 servers.

## Main Responsibilities
- Maintain callback service instances by NFSv4 minor version.
- Create TCP callback listeners for NFSv4.0.
- Enable RPC backchannel service for NFSv4.1+ sessions.
- Start and stop callback service threads.
- Track per-network-namespace callback users.
- Authenticate callback RPC requests.
- Define the NFSv4 callback RPC program.

## Key Functions
- `nfs_callback_up()` creates or reuses the callback service, binds per-net transport/backchannel state, starts service threads, and increments user counts.
- `nfs_callback_down()` decrements users, destroys per-net transports, stops service threads, and clears backchannel service pointers when no users remain.
- `nfs4_callback_svc()` is the callback service thread loop using `svc_recv()`.
- `nfs4_callback_up_net()` creates IPv4 and optionally IPv6 TCP listener sockets for v4.0 callbacks.
- `nfs_callback_up_net()` binds the service to a net namespace and either starts v4.0 listeners or enables v4.1+ backchannel support.
- `check_gss_callback_principal()` validates RPCSEC_GSS callback principals for NFSv4.0.
- `nfs_callback_authenticate()` enforces basic auth flavor rules before XDR-level client lookup.

## Control Flow
`nfs_callback_up()` is serialized by `nfs_callback_mutex`. It creates a `svc_serv` if needed, initializes per-net callback state, then ensures the service has at least `NFS4_MIN_NR_CALLBACK_THREADS` threads. Error paths undo per-net setup and destroy the service if there are no users.

## Data and Ownership
- `nfs_callback_info[minorversion]` stores service pointer and global user count.
- Per-net `nn->cb_users[minorversion]` tracks network namespace use.
- For v4.1+, `xprt->bc_serv` stores the service for backchannel initialization.

## Authentication Behavior
- `RPC_AUTH_NULL` is accepted only for `CB_NULL`.
- `RPC_AUTH_GSS` is denied on backchannel callbacks.
- Detailed NFSv4.0 client/principal validation is deferred to compound processing after the callback identifier resolves to an `nfs_client`.

## Notable Details
- IPv6 listener failure is ignored only for `-EAFNOSUPPORT`.
- Callback thread count is module-configurable but clamped to at least one.
- v4.1 callback concurrency is effectively constrained by backchannel slot constants in `callback.h`.

## Risks and Edge Cases
- `nfs_callback_down()` assumes matching up/down calls; underflow of user counts would be serious.
- GSS principal fallback compares `nfs@hostname` to `cl_hostname`, which can fail for non-canonical mount names.
- v4.1+ GSS callback support is explicitly absent.

## Integration Points
Uses callback procedure versions from `callback_xdr.c`, client records from `client.c`, and NFS net namespace state from `netns.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback.h -->
# File Research: sources/os/linux/linux/fs/nfs/callback.h

## Purpose
Defines NFSv4 callback protocol constants, argument/result structures, callback processing state, and public callback function prototypes.

## Main Contents
- Callback RPC program number and buffer sizes.
- Callback procedure numbers: `CB_NULL` and `CB_COMPOUND`.
- `struct cb_process_state`, carrying resolved client, session slot, net namespace, minor version, DRC status, and referring-call count.
- Argument/result structures for callback operations:
  - `CB_GETATTR`
  - `CB_RECALL`
  - `CB_SEQUENCE`
  - `CB_RECALL_ANY`
  - `CB_RECALL_SLOT`
  - `CB_LAYOUTRECALL`
  - `CB_NOTIFY_DEVICEID`
  - `CB_NOTIFY_LOCK`
  - `CB_OFFLOAD` when NFSv4.2 is enabled.
- Recall-any type mask constants.
- Callback service lifecycle declarations.

## Important Constants
- `NFS4_CALLBACK`
- `NFS4_CALLBACK_XDRSIZE`
- `NFS4_CALLBACK_BUFSIZE`
- `NFS41_BC_MIN_CALLBACKS`
- `NFS41_BC_MAX_CALLBACKS`
- `NFS4_MIN_NR_CALLBACK_THREADS`

## Integration Points
Included by `callback.c`, `callback_proc.c`, and `callback_xdr.c`. It also exposes callback up/down functions to NFSv4 client setup code.

## Notable Details
- `cb_process_state.clp` is always set directly for v4.0 and set by `CB_SEQUENCE` for v4.1+.
- The callback DRC status field is used to propagate replay/cache errors through later operations in a compound.
- Backchannel concurrency constants document the current single-slot callback model.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback_proc.c -->
# File Research: sources/os/linux/linux/fs/nfs/callback_proc.c

## Purpose
Implements the semantic handlers for decoded NFSv4 callback operations. It updates delegation, layout, device-id, slot/session, lock, and NFSv4.2 offload-copy state after `callback_xdr.c` decodes the wire data.

## Main Responsibilities
- Answer `CB_GETATTR` from delegated inode state.
- Process delegation recalls through asynchronous delegation return.
- Process layout recalls for files, FSIDs, or all layouts.
- Process pNFS device notifications by deleting cached device IDs.
- Validate and advance NFSv4.1+ backchannel sequence slots.
- Process recall-any and recall-slot pressure signals.
- Wake waiters for server lock notifications.
- Record NFSv4.2 server-side-copy offload completion callbacks.

## Key Functions
- `nfs4_callback_getattr()` finds a delegated inode and returns requested size/change/time attributes for write delegations.
- `nfs4_callback_recall()` finds a delegated inode and schedules delegation return.
- `nfs4_callback_layoutrecall()` dispatches to file or bulk pNFS layout draining.
- `nfs4_callback_devicenotify()` deletes matching pNFS device IDs using the relevant layout driver.
- `nfs4_callback_sequence()` resolves the callback session, validates slot/sequence/cache rules, handles referring calls, and locks the backchannel slot.
- `nfs4_callback_recallany()` expires matching unused delegations and triggers layout recalls or flexfile recall-any state.
- `nfs4_callback_recallslot()` lowers target forechannel slot limits and notifies the state manager.
- `nfs4_callback_notify_lock()` wakes lock waiters when decoded owner data is valid.
- `nfs4_callback_offload()` records asynchronous copy completion by matching or queueing a copy state.

## Layout Recall Flow
File layout recall first locates an inode by layout stateid, falling back to filehandle. It commits layout data, validates callback stateid sequencing, checks for bulk recall conflicts, updates the layout stateid, marks matching layout segments for return, frees matching lsegs, and kicks commit cleanup. Bulk recall destroys layouts by FSID or client ID.

## Sequence Handling
`nfs4_callback_sequence()`:
- Finds the client/session from session ID and source address.
- Rejects missing sessions or sessions without backchannel.
- Rejects draining sessions with `DELAY` or `BADSESSION`.
- Validates slot ID and sequence ID.
- Rejects cached-reply requests because the client does not implement a duplicate reply cache.
- Waits briefly on referring forechannel calls before allowing dependent callbacks.
- Stores the slot in `cb_process_state` for later release by XDR compound cleanup.

## Data and Ownership
- `CB_SEQUENCE` frees referring-call allocations after processing.
- `CB_DEVICE_NOTIFY` frees decoded device notification arrays.
- Inode references acquired through delegation/layout lookup are released with `nfs_iput_and_deactive()`.
- Layout headers are refcounted with `pnfs_get_layout_hdr()`/`pnfs_put_layout_hdr()`.

## Status Mapping
Handlers return NFS protocol status values in big-endian form. Common mappings include:
- Missing session/client: `NFS4ERR_OP_NOT_IN_SESSION` or `NFS4ERR_BADSESSION`.
- Missing delegation inode: `NFS4ERR_BADHANDLE`, `NFS4ERR_DELAY`, or `NFS4ERR_BAD_STATEID`.
- Layout stateid mismatch: `NFS4ERR_BAD_STATEID`, `NFS4ERR_OLD_STATEID`, `NFS4ERR_DELAY`, or `NFS4ERR_NOMATCHING_LAYOUT`.
- Successful callbacks return `NFS4_OK`.

## Risks and Edge Cases
- `referring_call_exists()` drops and reacquires the slot-table lock while waiting, so callers must tolerate state changes.
- Layout recall sequencing depends on referring-call count to decide whether a future stateid should be trusted.
- `CB_GETATTR` only supplies attributes when a valid write delegation exists.
- Offload callback stores unmatched completions in `pending_cb_stateids`; cleanup is handled elsewhere.

## Integration Points
This file ties callbacks to delegation management (`delegation.c`), pNFS layout management, NFSv4 session slot code, lock wait queues, copy offload state, and NFS tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback_xdr.c -->
# File Research: sources/os/linux/linux/fs/nfs/callback_xdr.c

## Purpose
Implements NFSv4 callback XDR decoding, result encoding, operation admission, and COMPOUND dispatch. It is the protocol glue between SUNRPC service requests and semantic handlers in `callback_proc.c`.

## Main Responsibilities
- Decode callback COMPOUND headers and per-operation arguments.
- Encode callback COMPOUND headers and operation results.
- Enforce which callback operations are legal for NFSv4.0, v4.1, and v4.2.
- Enforce `CB_SEQUENCE` position rules for v4.1+.
- Dispatch decoded operations through a callback operation table.
- Define callback RPC procedures and service versions.

## Key Decode Functions
- `decode_compound_hdr_arg()` decodes tag, minor version, callback identifier, and operation count.
- `decode_fh()`, `decode_bitmap()`, and `decode_stateid()` decode shared protocol structures.
- `decode_getattr_args()` and `decode_recall_args()` decode v4.0 delegation callbacks.
- `decode_layoutrecall_args()` decodes file, FSID, and all-layout recalls.
- `decode_devicenotify_args()` decodes and validates pNFS device notifications.
- `decode_cb_sequence_args()` decodes session ID, sequence fields, cache flag, and referring-call lists.
- `decode_notify_lock_args()` decodes filehandle and lock owner.
- `decode_offload_args()` decodes NFSv4.2 offload completion callbacks.

## Key Encode Functions
- `encode_compound_hdr_res()` reserves status and operation-count slots and echoes the tag.
- `encode_op_hdr()` writes operation number and status.
- `encode_getattr_res()` encodes requested delegated attributes.
- `encode_cb_sequence_res()` encodes session ID, sequence ID, slot ID, highest slot ID, and target highest slot ID.
- Attribute helpers encode change, size, and time fields only when present in the response bitmap.

## Dispatch Flow
`nfs4_callback_compound()` decodes the header, resolves and authenticates v4.0 clients by callback identifier, initializes `cb_process_state`, writes the compound response header, then loops over operations with `process_op()`. After the loop it writes compound status and operation count, releases any callback slot, and drops the client reference.

## Operation Admission
- NFSv4.0 accepts only `OP_CB_GETATTR` and `OP_CB_RECALL`.
- NFSv4.1 requires `OP_CB_SEQUENCE` as the first operation and rejects later operations without it.
- NFSv4.1 accepts sequence, delegation, layout, device, recall-any, recall-slot, and notify-lock callbacks.
- NFSv4.2 additionally accepts `OP_CB_OFFLOAD` when compiled with `CONFIG_NFS_V4_2`.
- Unsupported known operations return `NFS4ERR_NOTSUPP`; unknown operations return `NFS4ERR_OP_ILLEGAL`.

## Data and Ownership
- Decoders allocate device notification arrays and referring-call lists; semantic handlers or error paths free them.
- `nfs4_cb_free_slot()` frees a locked backchannel slot after compound processing.
- v4.0 client references are acquired through `nfs4_find_client_ident()` and released at compound exit.

## Notable Details
- Uses `NFS4ERR_RESOURCE_HDR` internally to distinguish header encode/decode buffer exhaustion.
- `svc_process_common()` requires an encoder, so `nfs4_encode_void()` exists even for callback responses already encoded by the procedure.
- For invalid v4.0 credentials, the code sets `rq_auth_stat = rpc_autherr_badcred` and returns an RPC-level success accept status.
- Backchannel timeout values are copied from the resolved client RPC timeout after processing.

## Risks and Edge Cases
- `decode_bitmap()` accepts more than three bitmap words but only stores the first three after consuming all words.
- `decode_devicenotify_args()` compares `cbd_layout_type` to `NOTIFY_DEVICEID4_CHANGE` in one branch where the decoded field appears semantically to be layout type; this is a subtle area worth checking against protocol definitions.
- Response buffer admission checks `maxlen > 0 && maxlen < PAGE_SIZE`, coupling operation execution to available XDR response space.
- Many decode failures map to resource or bad XDR statuses, so callers depend on exact status semantics.

## Integration Points
Exports `nfs4_callback_version1` and `nfs4_callback_version4` consumed by `callback.c`’s `svc_program`. Dispatch entries call handlers declared in `callback.h` and implemented in `callback_proc.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/callback_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/client.c -->
# File Research: sources/os/linux/linux/fs/nfs/client.c

## Purpose
Manages shared NFS client records, per-mount server records, RPC clients, NFS version registration, server probing, network namespace NFS client lists, and `/proc` reporting for mounted NFS servers and volumes.

## Main Responsibilities
- Register and find NFS protocol version modules.
- Allocate, share, initialize, reference, and destroy `nfs_client` objects.
- Create base RPC clients and per-server cloned RPC clients.
- Initialize NFSv2/v3 server records from mount context.
- Probe FSINFO/PATHCONF and derive server capabilities and I/O sizes.
- Start lockd for NFSv2/v3 when needed.
- Allocate, insert, remove, clone, and free `nfs_server` records.
- Initialize and destroy per-network-namespace NFS client state.
- Expose `/proc/fs/nfsfs` and `/proc/net/nfsfs` server/volume listings.

## Key Functions
- `find_nfs_version()`, `register_nfs_version()`, and `unregister_nfs_version()` manage NFS version modules and RPC version tables.
- `nfs_alloc_client()` initializes a shared client with address, hostname, version ops, transport settings, net namespace, and localio state.
- `nfs_get_client()` finds an existing matching client or allocates/inserts/initializes a new one.
- `nfs_put_client()` drops references and destroys clients when the count reaches zero.
- `nfs_create_rpc_client()` creates the base SUNRPC client using mount transport/security settings.
- `nfs_init_server_rpcclient()` clones the base client with selected auth flavor for a mounted server.
- `nfs_init_server()` initializes NFSv2/v3 mount server data.
- `nfs_probe_fsinfo()` performs capability, FSINFO, PATHCONF, and trunking discovery.
- `nfs_create_server()` creates a root server record for a mount.
- `nfs_clone_server()` creates a server record for referrals/submounts.
- `nfs_clients_init()` and `nfs_clients_exit()` manage per-net lists and callback IDR state.

## Client Sharing Rules
`nfs_match_client()` matches on protocol version ops, transport protocol, NFSv4 minor version, data-server flag, address or xprt-switch address, and transport security policy/cert identities. Clients still initializing are waited on before reuse.

## Server Initialization Flow
`nfs_create_server()` allocates `nfs_server`, gets credentials, allocates fattr storage, initializes the server/client/RPC state from mount context, probes FSINFO, sets NFSv2/v3 name and readdirplus caps, fetches attributes if needed, stores FSID, inserts the server into global lists, and returns the mounted server record.

## FSINFO Behavior
`nfs_server_set_fsinfo()` derives read/write sizes, page counts, write multipliers, directory transfer size, max file size, change attribute type, clone block size, socket buffers, and NFSv4.2 xattr sizes/capability. Mount options clamp or override many of these values.

## Data and Ownership
- `nfs_client` is refcounted and freed via version-specific `free_client`.
- `nfs_server` is RCU-freed after RPC clients, credentials, sysfs state, and client refs are released.
- Net namespace lists are protected by `nn->nfs_client_lock`.
- Server-to-client list membership uses RCU for callback/layout/delegation iteration.

## Notable Details
- `nfs_mark_client_ready()` uses memory barriers around `cl_cons_state` and wakes waiters.
- NFSv2/v3 lockd is skipped when both local flock and local fcntl are requested.
- NFSv4 capability initialization is delegated to minor-version ops and then adjusted for mount flags and transport constraints.
- Localio support initializes client UUID/boot state and schedules asynchronous probing when enabled.
- `/proc` server and volume views print transport address, port, refcount, hostname, device, FSID, and fscache state.

## Risks and Edge Cases
- Matching clients while another thread initializes requires careful wait/retry behavior to avoid duplicate clients or use of failed clients.
- Error paths in server creation must avoid double-putting partially initialized RPC clients and client refs.
- FSINFO sizes are bounded by RPC payload and NFS max I/O constants; incorrect server values are clamped.
- `nfs_alloc_server()` frees `server` directly if iostat allocation fails but does not free the allocated sysfs ID in that path, which is worth verifying against surrounding code expectations.

## Integration Points
This is central NFS client infrastructure used by NFSv2/v3/v4 mount code, callback lookup, delegation/layout iteration, pNFS, lockd, SUNRPC, sysfs, fscache, localio, and procfs reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/delegation.c -->
# File Research: sources/os/linux/linux/fs/nfs/delegation.c

## Purpose
Implements NFSv4 file and directory delegation lifecycle management. It tracks delegated state per inode, validates delegation availability, handles recalls/returns/revocation, maintains delegation LRU/return queues, supports reboot/reclaim handling, and exposes helpers for using delegation stateids.

## Main Responsibilities
- Allocate, attach, update, detach, revoke, and free `nfs_delegation` objects.
- Check read/write/time delegation availability.
- Return delegations synchronously or asynchronously.
- Reclaim delegated open and lock state during delegation return.
- Maintain per-server delegation hash tables and lists.
- Expire unused, unreferenced, revoked, or unclaimed delegations.
- Handle server reboot/lease-expiry delegation validation.
- Copy or refresh delegation stateids for NFS operations.
- Enforce a delegation watermark with LRU-based return.

## Key Functions
- `nfs_inode_set_delegation()` attaches a new delegation or updates/replaces an existing one.
- `nfs_inode_reclaim_delegation()` updates delegation state after reclaim.
- `nfs4_have_delegation()` and `nfs4_check_delegation()` test delegation presence with optional reference marking.
- `nfs_async_inode_return_delegation()` marks a matching delegation for state-manager return after callback recall.
- `nfs4_inode_return_delegation()` synchronously returns a delegation and flushes dirty regular-file data.
- `nfs4_inode_set_return_delegation_on_close()` and `_on_close()` defer return until open files close.
- `nfs_client_return_marked_delegations()` drains return queues from the state manager.
- `nfs_delegation_find_inode()` locates an inode by filehandle for callback recall.
- `nfs_remove_bad_delegation()`, `nfs_delegation_mark_returned()`, and `nfs_revoke_delegation()` handle invalid or returned stateids.
- `nfs_delegation_mark_reclaim()` and `nfs_delegation_reap_unclaimed()` support reboot recovery.
- `nfs_reap_expired_delegations()` tests and frees delegations after lease-expiry suspicion.
- `nfs4_copy_delegation_stateid()` and `nfs4_refresh_delegation_stateid()` provide stateid helpers to operation paths.

## Delegation Attachment Flow
`nfs_inode_set_delegation()` allocates a delegation, initializes stateid/type/cred/change attribute/flags, then under `cl_lock` either attaches it to inode/server/hash lists, updates an existing delegation with the same stateid identity, rejects a duplicate, or replaces an older delegation. It also invalidates cached inode attributes when change data was not revalidated.

## Delegation Return Flow
Return begins with `nfs_start_delegation_return()`, which grabs a valid delegation and sets `NFS_DELEGATION_RETURNING`. `nfs_end_delegation_return()` breaks leases, claims delegated opens and locks for regular files, waits for recovery if synchronous, then sends `DELEGRETURN`. Delayed returns are requeued and marked with `NFS4CLNT_DELEGRETURN_DELAYED`.

## Lists and Hashes
- `server->delegations` tracks attached delegations.
- `server->delegations_return` queues delegations to return.
- `server->delegations_lru` tracks closed delegations for pressure return.
- `server->delegations_delayed` holds delayed returns.
- `server->delegation_hash_table` maps filehandles to delegations for callback lookup.

## Locking and Lifetime
- `clp->cl_lock` protects inode delegation pointer attach/detach.
- `server->delegations_lock` protects return/LRU/delayed queues.
- Each delegation has its own spinlock for inode pointer, stateid, cred, and flags-sensitive updates.
- Delegations are refcounted and freed with `kfree_rcu()`.
- Lookup paths use RCU and `igrab()`/`nfs_sb_active()` to safely return inodes.

## Notable Details
- Directory delegations are enabled by default via module parameter.
- `delegation_watermark` defaults to 5000 and drives LRU return pressure.
- Delegated time attributes are tracked through `NFS_DELEGATION_DELEGTIME`.
- Revocation marks stateid invalid, decrements active delegation count, and may clear delegated verifier state.
- If the server reboots during expired-delegation testing, the code re-marks work and returns `-EAGAIN`.

## Risks and Edge Cases
- Delegation replacement handles broken servers that hand out duplicate delegations; write upgrades are specially tolerated.
- Stateid sequence comparisons decide whether revocation/returned notifications apply, so stale callback data is ignored.
- Some return paths cannot flush dirty data because they run in the state manager and could deadlock during recovery.
- Delegation queue reference counts must stay balanced when moving between list states.

## Integration Points
Used by callback recall/getattr handlers, NFSv4 open/lock recovery code, inode attribute delegation helpers, state manager recovery, pNFS recall-any paths, and NFS operation code that wants to use delegation stateids.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/delegation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nfs/delegation.h -->
# File Research: sources/os/linux/linux/fs/nfs/delegation.h

## Purpose
Declares NFSv4 delegation data structures, flags, and public APIs for delegation management and delegated attribute checks.

## Main Contents
- `struct nfs_delegation` definition:
  - hash/list membership
  - credential pointer
  - inode pointer
  - delegation stateid
  - delegation type
  - page modification limit
  - change attribute
  - test generation
  - flags
  - refcount
  - spinlock
  - RCU head
- Delegation flag enum:
  - reclaim needed
  - return-if-closed
  - referenced
  - returning
  - revoked
  - test-expired
  - delegated time support
- Public delegation lifecycle, recall, expiration, reclaim, and stateid helper declarations.

## Inline Helpers
- `nfs_have_read_or_write_delegation()`
- `nfs_have_write_delegation()`
- `nfs_have_delegated_attributes()`
- `nfs_have_delegated_atime()`
- `nfs_have_delegated_mtime()`
- `nfs_request_directory_delegation()`
- `nfs_have_directory_delegation()`

## Configuration
Declares `directory_delegations`, implemented as a module parameter in `delegation.c`.

## Integration Points
Included by NFS inode, callback, open, lock, state recovery, and attribute paths that need to test or manipulate NFSv4 delegated state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nfs/delegation.h -->