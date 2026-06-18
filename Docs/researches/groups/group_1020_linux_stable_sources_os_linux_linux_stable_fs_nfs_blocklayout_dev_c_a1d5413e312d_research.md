# Group Research: group_1020_linux_stable_sources_os_linux_linux_stable_fs_nfs_blocklayout_dev_c_a1d5413e312d

Scope: `Docs/research_subset_a.md`

This grouped report covers the requested Linux stable NFS client and pNFS blocklayout files. Each file section is wrapped in the exact markers requested for later source-tree-aligned splitting.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/dev.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/dev.c

## Purpose

`dev.c` builds and tears down pNFS blocklayout device-id nodes. It decodes the server's block volume XDR description, resolves the volume graph into usable Linux block devices, maps logical layout offsets to device offsets, and manages SCSI persistent-reservation registration for SCSI-backed volumes.

## Main Responsibilities

- Decode `pnfs_block_volume` records for simple, slice, concat, stripe, and SCSI volume types.
- Resolve simple device signatures through the blocklayout userspace pipefs helper via `bl_resolve_deviceid()`.
- Resolve SCSI volumes through `/dev/disk/by-id/` paths using dm-mpath, `wwn-0x`, and `nvme-eui.` naming conventions.
- Construct recursive `pnfs_block_dev` trees for slices, concatenations, and stripes.
- Provide map callbacks (`bl_map_simple`, `bl_map_concat`, `bl_map_stripe`) that translate logical offsets to `struct block_device`, disk offset, and range length.
- Allocate and initialize `nfs4_deviceid_node` objects for the pNFS device cache.
- Free device-id nodes, close block-device files, and unregister SCSI persistent-reservation keys.

## Key Functions

- `bl_alloc_deviceid_node()` is the entry point from the pNFS device cache. It allocates a scratch folio, decodes all volumes from `pnfs_device` XDR pages, parses the last decoded volume as the top-level device, initializes the `nfs4_deviceid_node`, and marks it unavailable if parsing failed.
- `nfs4_block_decode_volume()` performs type-specific XDR decoding and bounds checks signature counts, signature lengths, volume counts, and SCSI designator lengths.
- `bl_parse_deviceid()` dispatches by volume type to simple, slice, concat, stripe, or SCSI parsing.
- `bl_parse_simple()` calls the pipefs/userspace resolver, opens the returned `dev_t`, records device length, and installs simple mapping.
- `bl_parse_scsi()` validates binary EUI64/NAA designators, opens a by-id path, validates nonzero length and persistent-reservation support, then stores the PR key.
- `bl_register_dev()` and `bl_unregister_dev()` recurse through device trees and register/unregister persistent-reservation keys only for leaf SCSI devices.
- `bl_free_deviceid_node()` tears down the recursive device tree and releases the enclosing cache node with RCU.

## Control Flow and State

The server supplies a flat array of volumes, where composite volumes reference earlier entries by index. `bl_alloc_deviceid_node()` decodes the array, then calls `bl_parse_deviceid()` on `nr_volumes - 1`, treating the final volume as the root. Composite parsers allocate child arrays, recursively parse referenced child volumes, and accumulate length/start metadata. The map callbacks later walk this tree to answer I/O mapping requests.

SCSI registration state is tracked with `PNFS_BDEV_REGISTERED` in `pnfs_block_dev::flags`. Registration is idempotent through `test_and_set_bit()`, and failure during recursive registration unwinds already registered children.

## Integration Points

- Uses `blocklayout.h` data structures and constants for volume/device layout.
- Calls `bl_resolve_deviceid()` from `rpc_pipefs.c` for simple signature-to-device resolution.
- Uses the NFS device-id cache through `nfs4_init_deviceid_node()`, `nfs4_mark_deviceid_unavailable()`, and RCU node freeing.
- Emits pNFS blocklayout tracepoints such as PR key registration/unregistration events.
- Uses block-layer APIs `bdev_file_open_by_dev()`, `bdev_file_open_by_path()`, `file_bdev()`, and persistent-reservation `pr_ops`.

## Concurrency and Lifetime

The file relies on the device-id cache for publication and RCU lifetime. Leaf devices own `struct file *bdev_file` references and release them with `fput()`. Composite devices own child arrays. Persistent-reservation registration is tracked per leaf device and unwound during free. Parsing failure may still return an initialized device-id node marked unavailable, allowing the cache to represent negative availability.

## Risks and Edge Cases

- Composite volume parsing assumes referenced indexes are valid; this file bounds volume counts but does not visibly validate every reference index against `nr_volumes`.
- `bl_parse_concat()` and `bl_parse_stripe()` return immediately on child parse failure without locally freeing previously parsed children; cleanup depends on top-level device destruction paths if the partially built tree is retained.
- `bl_map_stripe()` sets `map->len` to the stripe chunk size after child mapping, so callers must still clip to requested I/O ranges and device boundaries.
- SCSI path resolution is distribution- and udev-name-dependent; the fallback sequence is explicit and may fail if by-id links are unavailable.
- Persistent reservations require block-device support for `pr_ops`; unsupported devices are rejected.

## Testing Focus

Useful tests or review cases include malformed XDR for each volume type, invalid SCSI designator lengths/types, composite volumes with boundary index/count values, stripe offset mapping across child boundaries, PR registration unwind on partial failure, and unavailable-device cache behavior after parse failures.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/dev.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/extent_tree.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/extent_tree.c

## Purpose

`extent_tree.c` manages pNFS blocklayout extents in red-black trees. It stores read-only and read-write layout extents, performs overlap insertion/removal/splitting/merging, tracks written invalid extents, and encodes layoutcommit updates for block and SCSI layouts.

## Main Responsibilities

- Maintain two extent trees in `struct pnfs_block_layout`: read-only (`bl_ext_ro`) and read-write (`bl_ext_rw`).
- Insert extents while trimming or splitting overlaps against existing ranges.
- Remove ranges from one or both trees, splitting extents when removal cuts through the middle.
- Lookup the extent covering a file-sector offset, preferring read-only extents for non-write lookups and falling back to read-write extents.
- Mark written ranges by converting matching invalid extents from unwritten to written state and removing conflicting COW/hole extents.
- Encode written extents into NFS layoutcommit layoutupdate buffers.
- Transition committing extents to committed read-write data on success or back to written on failure.

## Key Functions

- `ext_tree_insert()` chooses the target tree based on `be_state`, resolves overlaps, splits new extents when needed, and merges adjacent compatible extents.
- `ext_tree_remove()` removes a `[start, end)` sector range from read-only extents and optionally read-write extents.
- `ext_tree_lookup()` copies the matching extent into caller storage under `bl_ext_lock`.
- `ext_tree_mark_written()` removes read-only COW/hole coverage for a written range and marks matching untagged `PNFS_BLOCK_INVALID_DATA` extents as `EXTENT_WRITTEN`.
- `ext_tree_prepare_commit()` allocates a layoutupdate buffer, first trying a single page, then falling back to a vmalloc buffer sized by server `wsize` if needed.
- `ext_tree_try_encode_commit()` is all-or-nothing for a single-page buffer.
- `ext_tree_encode_commit()` encodes as many written extents as fit in the larger buffer and returns `-ENOSPC` when more layoutcommit work remains.
- `ext_tree_mark_committed()` frees commit buffers and updates extent state after the server replies.

## Data Structures and Invariants

Extents are ordered by `be_f_offset` and treated as half-open ranges ending at `be_f_offset + be_length`. Merge compatibility requires equal state, equal device pointer, adjacency in file offsets, contiguous volume offsets for data-bearing extents, and equal tags for invalid-data extents. `PNFS_BLOCK_NONE_DATA` extents do not require contiguous `be_v_offset`.

Device-id references are owned by extents. When extents are removed, merged away, or discarded, the code calls `nfs4_put_deviceid_node()`. When extents are split or duplicated, it increments the device-id reference with `nfs4_get_deviceid()`.

## Control Flow and State

The file uses `bl->bl_ext_lock` to serialize all rbtree mutation and lookup. Removal can detach multiple extents into a temporary list so expensive reference dropping and freeing occur after releasing the spinlock. Mark-written first removes read-only coverage in the affected range, then walks read-write invalid extents and splits/merges them to isolate the written subranges.

Layoutcommit encoding scans `bl_ext_rw` for `PNFS_BLOCK_INVALID_DATA` extents tagged `EXTENT_WRITTEN`. Encoded extents are retagged `EXTENT_COMMITTING`, and `bl_lwb` is converted into `lastbytewritten`. On commit success, committing extents become `PNFS_BLOCK_READWRITE_DATA`; on failure they return to `EXTENT_WRITTEN` for retry.

## Integration Points

- Uses `BLK_LO2EXT(NFS_I(inode)->layout)` to retrieve the blocklayout extension for layoutcommit.
- Encodes either pNFS block extents with device IDs or SCSI layout ranges depending on `bl_scsi_layout`.
- Uses `nfs4_layoutcommit_args` fields `layoutupdate_page`, `layoutupdate_pages`, `layoutupdate_len`, `start_p`, and `lastbytewritten`.
- Emits `trace_bl_ext_tree_prepare_commit()` for commit preparation.

## Risks and Edge Cases

- Several split/remove paths allocate with `GFP_ATOMIC` under a spinlock; memory pressure can produce `-ENOMEM`.
- `ext_tree_encode_commit()` uses `be_prev` when a buffer fills; the function relies on at least one extent having been encoded before the `-ENOSPC` path.
- The code uses `BUG()` if insertion sees an impossible overlap in `__ext_tree_insert()`, so callers must maintain non-overlap preconditions before raw insertion.
- Layoutcommit partial encoding intentionally commits a prefix and leaves remaining written extents for later commits.
- Sector-to-byte conversion shifts by `SECTOR_SHIFT`; callers must pass sector units consistently.

## Testing Focus

Coverage should include insertion around existing extents, middle removals that create two fragments, adjacent merge eligibility, invalid-data write marking with left/right splits, read-only versus read-write lookup ordering, single-page commit success, vmalloc fallback, partial commit `-ENOSPC`, and commit failure retry behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/extent_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/rpc_pipefs.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/blocklayout/rpc_pipefs.c

## Purpose

`rpc_pipefs.c` implements the pNFS blocklayout pipefs upcall used to resolve simple block volume signatures into Linux device major/minor numbers. It also registers the per-network-namespace `blocklayout` rpc_pipefs node used by the userspace helper.

## Main Responsibilities

- Encode a simple block volume into the blocklayout daemon message format.
- Queue an upcall to userspace via rpc_pipefs and wait for a downcall response.
- Decode the daemon's `bl_dev_msg` response into a `dev_t`.
- Provide pipe downcall and destroy callbacks.
- Create and remove `/.../nfs/blocklayout` pipefs dentries on rpc_pipefs mount/umount events.
- Manage per-net initialization and cleanup of blocklayout pipe state.

## Key Functions

- `bl_resolve_deviceid()` serializes a simple volume, queues `BL_DEVICE_MOUNT`, sleeps on `nn->bl_wq`, and returns `MKDEV(reply->major, reply->minor)` when userspace reports `BL_DEVICE_REQUEST_PROC`.
- `nfs4_encode_simple()` emits a single simple-volume XDR-like payload including signature offsets and opaque signature bytes.
- `bl_pipe_downcall()` validates response length, copies `struct bl_dev_msg` from userspace into `nn->bl_mount_reply`, and wakes the waiter.
- `bl_pipe_destroy_msg()` wakes the waiter if the queued upcall was destroyed with an error.
- `rpc_pipefs_event()` reacts to `RPC_PIPEFS_MOUNT` and `RPC_PIPEFS_UMOUNT`.
- `bl_init_pipefs()` and `bl_cleanup_pipefs()` register/unregister the notifier and pernet subsystem.

## Control Flow and State

`bl_resolve_deviceid()` serializes all blocklayout upcalls per network namespace with `nn->bl_mutex`. It temporarily increments `b->simple.len` to account for the single-volume wrapper, allocates an upcall buffer, queues it with `rpc_queue_upcall()`, sets the task state to uninterruptible, and waits for a downcall/destroy wakeup. The response is stored in the per-net `nn->bl_mount_reply`.

Per-net state consists of `bl_mutex`, `bl_wq`, and `bl_device_pipe`. The pipe is created with `rpc_mkpipe_data()` and registered into mounted pipefs superblocks when available.

## Integration Points

- Called from `dev.c` by `bl_parse_simple()`.
- Uses `struct nfs_net` fields for shared NFS per-net state.
- Uses SUNRPC pipefs helpers `rpc_mkpipe_data()`, `rpc_mkpipe_dentry()`, `rpc_queue_upcall()`, `rpc_unlink()`, and notifier registration.
- Exposes the blocklayout device resolver to a userspace daemon that knows how to map simple signatures to block devices.

## Risks and Edge Cases

- The wait is uninterruptible and has no local timeout; progress depends on userspace or message destruction.
- `b->simple.len` is incremented in place for the wrapper before message size validation, so callers should not reuse the same decoded volume assuming the original length.
- Only one outstanding simple-volume upcall per net namespace is allowed by the mutex and single reply slot.
- If rpc_pipefs is not mounted, per-net registration returns success without creating a visible pipe until a later mount event.

## Testing Focus

Important cases include absent pipefs mounts, userspace returning non-success status, malformed downcall lengths, upcall queue failure, message destruction wakeup, and concurrent simple-volume resolutions within one network namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/blocklayout/rpc_pipefs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/cache_lib.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/cache_lib.c

## Purpose

`cache_lib.c` provides helper routines for NFS client caches that use SUNRPC cache infrastructure and rpc_pipefs. It supports userspace cache upcalls, deferred request waiting, and per-net/per-superblock cache registration.

## Main Responsibilities

- Invoke the configurable `/sbin/nfs_cache_getent` helper to populate cache entries.
- Disable the helper path automatically after `ENOENT` or `EACCES` failures.
- Allocate, reference, complete, and free deferred cache requests.
- Wait for deferred cache upcalls with a configurable timeout.
- Register and unregister `cache_detail` instances under rpc_pipefs `cache/`.

## Key Functions

- `nfs_cache_upcall()` builds helper argv as `<helper> <cache-name> <entry-name>`, uses `call_usermodehelper(..., UMH_WAIT_EXEC)`, and maps positive helper returns to success.
- `nfs_cache_defer_req_alloc()` creates `struct nfs_cache_defer_req`, initializes completion and refcount, and installs the `defer` callback.
- `nfs_dns_cache_defer()` increments the deferred request refcount and returns the embedded `cache_deferred_req`.
- `nfs_dns_cache_revisit()` completes the waiting request and drops the deferred reference.
- `nfs_cache_wait_for_upcall()` waits up to `cache_getent_timeout` seconds.
- `nfs_cache_register_net()` initializes a cache detail and registers it against a mounted rpc_pipefs superblock if one exists.
- `nfs_cache_unregister_net()` unregisters from pipefs if mounted and always destroys the cache detail.

## Control Flow and State

Two module parameters control userspace behavior: `cache_getent` and `cache_getent_timeout`. Deferred requests use a completion plus refcount so a waiting kernel caller and SUNRPC cache revisit path can coordinate lifetime. The registration helpers tolerate rpc_pipefs not being mounted by initializing/destroying cache details independently from pipefs visibility.

## Integration Points

- Uses `<linux/sunrpc/cache.h>` for `cache_detail`, `cache_req`, and deferred request callbacks.
- Uses rpc_pipefs lookup and registration helpers.
- Provides shared helpers for NFS client caches such as DNS or id-mapping style caches.

## Risks and Edge Cases

- The helper path is globally disabled after missing/inaccessible executable errors until the module parameter is changed.
- Waiting is bounded by the module timeout, but the caller must still release deferred request references correctly.
- `nfs_cache_register_sb()` assumes the `cache` dentry lookup result is suitable for `sunrpc_cache_register_pipefs()` and always `dput()`s it.

## Testing Focus

Test helper success/failure path disabling, timeout behavior, revisit completion, refcount release ordering, register/unregister with and without mounted rpc_pipefs, and cache detail cleanup after registration failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/cache_lib.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/cache_lib.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/cache_lib.h

## Purpose

`cache_lib.h` declares the shared NFS client cache helper API and the deferred request container used by `cache_lib.c`.

## Main Contents

- Defines `struct nfs_cache_defer_req`, embedding:
  - `struct cache_req req`
  - `struct cache_deferred_req deferred_req`
  - `struct completion completion`
  - `refcount_t count`
- Declares userspace upcall, deferred request allocation/free/wait, and cache registration helpers.

## Integration Points

Consumers include NFS cache implementations that need to defer lookups while a userspace helper populates SUNRPC cache entries. The header depends on Linux completion, SUNRPC cache, and atomic/refcount definitions.

## API Notes

The caller owns the initial `nfs_cache_defer_req` reference returned by `nfs_cache_defer_req_alloc()` and must release it with `nfs_cache_defer_req_put()`. The deferred path takes its own reference before returning a `cache_deferred_req` to SUNRPC cache code.

## Testing Focus

Header-level review should verify all users pair allocation with `nfs_cache_defer_req_put()`, wait only on initialized requests, and unregister cache details in the same namespace/superblock context where they were registered.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/cache_lib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/callback.c

## Purpose

`callback.c` owns the NFSv4 callback service lifecycle. It creates the SUNRPC service, starts/stops callback worker threads, binds callback transports per network namespace, manages v4.0 callback sockets and v4.1+ backchannel service attachment, and authenticates callback RPC credentials at the service layer.

## Main Responsibilities

- Maintain per-minor-version callback service state in `nfs_callback_info[]`.
- Create TCP callback listeners for NFSv4.0 over IPv4 and IPv6.
- Attach the callback `svc_serv` to the RPC transport for NFSv4.1+ backchannels.
- Start a bounded number of callback service threads.
- Track per-net and global callback service users.
- Tear down transports and service threads when the last user exits.
- Validate callback authentication flavor and GSS principal constraints.
- Define the NFSv4 callback SUNRPC program and version table.

## Key Functions

- `nfs_callback_up()` is the main start path. It creates or reuses a service, brings up per-net callback resources, starts service threads, and increments usage.
- `nfs_callback_down()` decrements per-net/global usage, destroys transports, stops threads, and nullifies backchannel service references when unused.
- `nfs_callback_create_svc()` creates the SUNRPC service with `nfs4_callback_svc()` as the worker thread function.
- `nfs_callback_start_svc()` records the backchannel service on minor versions greater than zero and calls `svc_set_num_threads()`.
- `nfs_callback_up_net()` binds the service to a network namespace and selects either v4.0 socket listeners or v4.1 backchannel enablement.
- `check_gss_callback_principal()` validates v4.0 RPCSEC_GSS callbacks against the negotiated acceptor or `nfs@hostname`.
- `nfs_callback_authenticate()` rejects non-NULL auth for non-`CB_NULL` NULL-auth requests and rejects GSS on backchannel callbacks.

## Control Flow and State

All start/stop operations are serialized by `nfs_callback_mutex`. Each minor version has its own `nfs_callback_data` with user count and `svc_serv`. Each network namespace tracks callback users by minor version in `nn->cb_users[]` and stores assigned v4.0 TCP ports. The callback kernel thread repeatedly calls `svc_recv()` until the service thread is asked to stop.

## Integration Points

- Uses `callback_xdr.c` exported `nfs4_callback_version1` and `nfs4_callback_version4`.
- Called by NFSv4 client setup and teardown paths when callback support is needed.
- Uses SUNRPC service, socket, auth, and backchannel APIs.
- Uses `struct nfs_net` fields for per-net callback ports and usage.

## Risks and Edge Cases

- v4.0 requires externally reachable callback listener sockets; failures in IPv4 or non-`EAFNOSUPPORT` IPv6 creation abort callback setup.
- v4.1+ requires transport backchannel support via `xprt->ops->bc_setup`.
- GSS callback validation is intentionally limited for v4.1 backchannel, which is rejected here.
- Service destruction is tied to exact user counting; incorrect up/down pairing would leak or prematurely destroy the callback service.

## Testing Focus

Exercise v4.0 IPv4/IPv6 listener setup, v4.1 backchannel setup, module/thread count boundaries, failed service creation rollback, GSS principal validation, invalid auth flavor rejection, and multi-net namespace up/down reference behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/callback.h

## Purpose

`callback.h` defines NFSv4 callback protocol constants, callback argument/result structures, callback process state, callback operation prototypes, and helper declarations shared by callback service, XDR, and procedure implementations.

## Main Contents

- Callback program constants: `NFS4_CALLBACK`, XDR size, and service buffer size.
- Callback procedure numbers: `CB_NULL` and `CB_COMPOUND`.
- `struct cb_process_state`, which carries the matched `nfs_client`, callback slot, network namespace, minor version, duplicate-reply-cache status, and referring-call count across operations in a compound.
- Argument/result structures for `CB_GETATTR`, `CB_RECALL`, `CB_SEQUENCE`, `CB_RECALL_ANY`, `CB_RECALL_SLOT`, `CB_LAYOUTRECALL`, `CB_NOTIFY_DEVICEID`, `CB_NOTIFY_LOCK`, and v4.2 `CB_OFFLOAD`.
- Recall-any bitmap constants for delegation and pNFS layout classes.
- Callback procedure prototypes implemented in `callback_proc.c`.
- Callback service lifecycle prototypes implemented in `callback.c`.
- Backchannel callback concurrency constants.

## Integration Points

The header ties together:

- `callback.c` service lifecycle and authentication.
- `callback_xdr.c` decoding/encoding and operation dispatch.
- `callback_proc.c` callback semantics.
- pNFS and delegation code through layout recall, device notify, recall-any, and delegation recall APIs.

## State and API Notes

`cb_process_state::clp` is always available for NFSv4.0 after `cb_ident` lookup and is set for v4.1+ by `CB_SEQUENCE`. Many callback procedures return `NFS4ERR_OP_NOT_IN_SESSION` if `clp` is absent. `cb_process_state::slot` is owned by the callback compound dispatcher after successful `CB_SEQUENCE` and must be freed after compound processing.

## Testing Focus

Review all callback operation implementations against the structures declared here, especially conditional v4.2 offload fields, recall-any mask constants, and lifetime expectations for dynamically allocated arrays in sequence and device-notify arguments.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback_proc.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/callback_proc.c

## Purpose

`callback_proc.c` implements the semantics of NFSv4 callback operations after XDR decoding. It handles delegation getattr/recall, pNFS layout recall and device notifications, NFSv4.1 session sequencing, recall-any and recall-slot, lock notification, and NFSv4.2 server-side-copy offload completion callbacks.

## Main Responsibilities

- Answer callback `GETATTR` from delegated inode state.
- Process delegation recall by scheduling asynchronous delegation return.
- Locate pNFS layouts by stateid or filehandle and initiate file or bulk layout draining.
- Delete pNFS device IDs on device notify callbacks.
- Validate and advance NFSv4.1 callback sequence slots.
- Detect referring calls that are still pending on the forechannel.
- Expire unused delegations and recall pNFS layouts for `CB_RECALL_ANY`.
- Reduce forechannel slot table target for `CB_RECALL_SLOT`.
- Wake lock waiters for `CB_NOTIFY_LOCK`.
- Complete or record NFSv4.2 copy offload callback state.

## Key Functions

- `nfs4_callback_getattr()` finds a delegated inode, verifies a valid write delegation, and returns change, size, and requested time attributes.
- `nfs4_callback_recall()` finds the delegated inode and calls `nfs_async_inode_return_delegation()`, mapping kernel errors to NFS callback status codes.
- `nfs_layout_find_inode_by_stateid()` and `nfs_layout_find_inode_by_fh()` search all superblocks and layouts for a matching pNFS layout.
- `pnfs_check_callback_stateid()` enforces RFC5661 layout recall sequencing, including old, delayed, and mismatched stateid handling.
- `initiate_file_draining()` commits pending layout data, validates stateid, marks matching layout segments for return, and may call the layout driver's `return_range()`.
- `initiate_bulk_draining()` destroys layouts by FSID or client ID for bulk recall.
- `nfs4_callback_devicenotify()` finds the relevant layout driver and deletes device IDs from the cache.
- `nfs4_callback_sequence()` finds the client/session, validates slot and sequence ID, locks the backchannel slot, checks cachethis constraints, records referring-call status, and updates the slot sequence.
- `nfs4_callback_recallany()` handles delegation and layout recall masks and schedules the state manager for file-layout recall-any flags.
- `nfs4_callback_offload()` matches copy state by stateid, completes a waiting copy, or queues pending callback state if the local copy state is not present yet.

## Control Flow and State

For NFSv4.1+, `CB_SEQUENCE` must run first and populates `cps->clp`, `cps->slot`, and `cps->referring_calls`. Later operations in the same compound depend on that state. The sequence path uses the backchannel slot table lock to reject bad slots, replays, misordered sequence IDs, draining sessions, and unsupported cached replies.

Layout recall uses RCU to find candidate layouts, active-superblock references to prevent unmount races, inode references for stable processing, inode locks for layout header state, and pNFS layout reference helpers for lifetime. Delegation callbacks integrate with delegation lookup and asynchronous state manager return queues.

## Integration Points

- Delegation operations call into `delegation.c` through `nfs_delegation_find_inode()`, `nfs4_get_valid_delegation()`, and `nfs_async_inode_return_delegation()`.
- pNFS operations use layout header state, layout segment return marking, device-id deletion, layout driver lookup, and layoutcommit/commit helpers.
- Session operations use `nfs4session.h` slot-table helpers.
- v4.2 offload integrates with `struct nfs4_copy_state` lists on `nfs_server` and `nfs_client`.
- Tracepoints in `nfs4trace.h` record callback outcomes.

## Risks and Edge Cases

- `nfs_layout_find_inode_by_stateid()` is annotated `__must_hold(RCU)` but also calls `rcu_read_lock()` internally; reviewers should keep lockdep expectations in mind around this helper.
- Layout recall sequencing intentionally returns `NFS4ERR_DELAY` in several race windows, including stateid gaps without referring-call evidence and already-returning layouts.
- `referring_call_exists()` drops and reacquires the slot-table lock while waiting on forechannel sequence IDs.
- Device notify ignores unknown layout drivers and continues; this is tolerant but can leave unsupported layout driver device IDs untouched.
- Offload callback handling must handle callback-before-waiter and waiter-before-callback races.

## Testing Focus

Important coverage includes v4.1 sequence replay/misorder cases, callback compounds missing `CB_SEQUENCE`, layout recall file/stateid mismatch, bulk layout recall, device notify delete/change, recall-any masks, recall-slot target changes, lock owner wakeups, delegation getattr with and without write delegation, and v4.2 offload completion races.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback_proc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback_xdr.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/callback_xdr.c

## Purpose

`callback_xdr.c` is the NFSv4 callback XDR layer and compound dispatcher. It decodes callback RPC arguments, preprocesses operation legality by NFS minor version, invokes the semantic handlers in `callback_proc.c`, encodes per-operation and compound replies, and publishes callback service version descriptors.

## Main Responsibilities

- Decode common XDR objects: opaque strings, filehandles, bitmaps, stateids, session IDs, referring call lists, layout recall ranges, device notifications, lock owners, and v4.2 offload responses.
- Encode callback results for GETATTR and CB_SEQUENCE.
- Enforce operation legality and ordering for NFSv4.0, v4.1, and v4.2.
- Dispatch each operation in a callback compound to the appropriate decode/process/encode callbacks.
- Look up and authenticate v4.0 callback clients by `cb_ident`.
- Manage backchannel slot release after compound processing.
- Define `callback_ops[]`, callback procedure tables, and exported `svc_version` objects.

## Key Functions

- `decode_compound_hdr_arg()` decodes tag, minor version, callback identifier, and operation count, rejecting unsupported minor versions.
- `decode_op_hdr()` decodes each callback operation number and uses a special internal `NFS4ERR_RESOURCE_HDR` to distinguish header-space failures.
- `decode_getattr_args()`, `decode_recall_args()`, `decode_layoutrecall_args()`, `decode_devicenotify_args()`, `decode_cb_sequence_args()`, `decode_recallany_args()`, `decode_recallslot_args()`, `decode_notify_lock_args()`, and `decode_offload_args()` decode operation-specific arguments.
- `encode_getattr_res()` emits requested attribute bitmaps and attribute payload.
- `encode_cb_sequence_res()` emits session and slot sequencing results.
- `preprocess_nfs4_op()`, `preprocess_nfs41_op()`, and `preprocess_nfs42_op()` validate operation legality and v4.1 sequence positioning.
- `process_op()` decodes one operation, calls its handler, encodes the operation header, and encodes any successful result body.
- `nfs4_callback_compound()` decodes the compound header, resolves client/session state, loops through operations, writes compound status/count, releases callback slots, and drops the client reference.
- `nfs_callback_dispatch()` bridges SUNRPC procedure dispatch to the callback procedure table.

## Control Flow and State

The dispatcher initializes `cb_process_state` for the compound. For minor version 0, it resolves the client immediately from `cb_ident` and validates the GSS callback principal before processing operations. For minor versions 1 and 2, `CB_SEQUENCE` is required as operation zero and fills in client/session state.

Each operation follows this sequence: decode opcode, preprocess operation for the minor version, honor any duplicate-reply-cache status from `CB_SEQUENCE`, decode args into `rq_argp`, call the semantic handler into `rq_resp`, encode the operation status header, and optionally encode a response body. At compound end, the callback slot is freed and the client reference is dropped.

## Integration Points

- Calls all callback procedure functions declared in `callback.h` and implemented in `callback_proc.c`.
- Calls `check_gss_callback_principal()` from `callback.c` for v4.0 GSS callback validation.
- Uses SUNRPC server XDR streams, request argument/response buffers, and service procedure/version registration.
- Uses backchannel helpers to set callback timeout values on backchannel requests.
- Exports `nfs4_callback_version1` and `nfs4_callback_version4` for the service program in `callback.c`.

## Risks and Edge Cases

- `decode_bitmap()` reads up to three bitmap words but consumes `attrlen << 2` bytes regardless of whether more than three words are provided; only the first three are retained.
- Device notify allocation and sequence referring-call allocation must be freed on both success and decode/process error paths; this file and `callback_proc.c` split that responsibility by operation.
- `process_op()` skips operation argument decode when output buffer space is small, returning `NFS4ERR_RESOURCE`.
- `CB_SEQUENCE` duplicate uncached reply handling stores `cps->drc_status` and reports success for the sequence operation so the next operation receives the retry error.
- v4.2 support is compile-time conditional; without it, minor version 2 callbacks return minor-version mismatch.

## Testing Focus

Test malformed XDR boundaries, oversized filehandles, long tags, unsupported minor versions, illegal operations, v4.1 sequence not first, operation-not-in-session cases, device notify allocation failures, referring-call cleanup, GETATTR bitmap/result length encoding, v4.2 offload decode variants, and callback compound status/count behavior after mid-compound errors.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/callback_xdr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/client.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/client.c

## Purpose

`client.c` implements core NFS client and server-instance management. It registers NFS protocol versions, allocates and shares `nfs_client` records, creates RPC clients, initializes per-mount `nfs_server` records, probes filesystem/server capabilities, tracks servers in per-net lists, exposes `/proc` views, and tears resources down.

## Main Responsibilities

- Maintain the global NFS RPC program version table and load protocol-version modules on demand.
- Allocate, initialize, match, reference, and free shared `struct nfs_client` objects.
- Create base RPC clients with mount/session transport settings and security policy.
- Initialize v2/v3 client state and lockd integration.
- Initialize per-mount `struct nfs_server` records from `fs_context`.
- Probe FSINFO/PATHCONF and derive I/O sizes, capabilities, max file size, xattr sizes, and cache timings.
- Allocate/free server records, I/O stats, sysfs IDs, RPC clients, and lockd state.
- Clone server records for submounts/referrals.
- Maintain per-network-namespace NFS client/server lists and procfs views.

## Key Functions

- `find_nfs_version()` returns a referenced protocol module, requesting `nfsv<version>` if needed.
- `register_nfs_version()` and `unregister_nfs_version()` publish/remove protocol implementations under `nfs_version_lock`.
- `nfs_alloc_client()` initializes a shared client object, including address, hostname, version module, transport settings, net namespace reference, and optional localio state.
- `nfs_get_client()` finds a matching initialized client or allocates/inserts a new one.
- `nfs_match_client()` compares version ops, transport protocol, minor version, DS flag, address/xprt switch addresses, and transport security policy.
- `nfs_create_rpc_client()` builds `rpc_create_args` from client init data and mount flags, then stores the base RPC client.
- `nfs_init_server_rpcclient()` clones the base RPC client with the selected auth flavor for a mounted server.
- `nfs_init_server()` configures a v2/v3 server from mount context, starts lockd, creates the RPC client, sets initial caps, and records mountd options.
- `nfs_probe_fsinfo()` and `nfs_server_set_fsinfo()` fetch server FSINFO/PATHCONF and compute effective NFS I/O parameters.
- `nfs_alloc_server()` initializes all per-server lists, delegation state, pNFS queues, I/O stats, owner counters, and wait queues.
- `nfs_create_server()` creates a v2/v3 mounted server, probes FSID and attributes, inserts it into lists, and records mount time.
- `nfs_clone_server()` duplicates a server record with a new filehandle/auth flavor and probes capabilities.
- `nfs_clients_init()` and `nfs_clients_exit()` manage per-net list heads, locks, stats, v4 caches, and sysfs state.
- Procfs helpers expose `/proc/net/nfsfs/servers`, `/proc/net/nfsfs/volumes`, and compatibility symlinks under `/proc/fs/nfsfs`.

## Control Flow and State

`nfs_client` objects are shared across mounts that match transport, NFS version, minor version, DS role, server address/xprt switch, and transport security. Creation uses a two-phase pattern: allocate outside the per-net spinlock, insert while marked initializing, then run protocol-specific `init_client()`. Other callers that find an initializing client take a reference, drop the lock, and wait on `nfs_client_active_wq`.

Each mount gets an `nfs_server` with its own cloned RPC client and mount-specific flags, auth, attribute cache parameters, FSID, capabilities, sysfs identity, delegation lists, layout lists, and stats. Server records are linked into both the owning client's superblock list and the per-net volume list under `nfs_client_lock`.

## Integration Points

- Uses protocol-specific `nfs_rpc_ops` for client allocation/init, fsinfo/pathconf/getattr, capabilities, trunking discovery, and lockd callbacks.
- Integrates with SUNRPC clients, stats, metrics, xprt security, TCP/TLS/RDMA transports, and optional localio.
- Initializes pNFS server queues and delegation structures used by other files in this group.
- Exposes sysfs links through NFS sysfs helpers.
- Integrates with lockd for NFSv2/v3 advisory locking.

## Risks and Edge Cases

- Client sharing must be exact enough to avoid cross-mount security or transport-policy leaks; TLS X.509 serials are part of the match.
- Initialization failure is stored in `cl_cons_state` and must wake waiters; callers must check readiness before using clients.
- `nfs_alloc_server()` allocates a sysfs ID before I/O stats; if I/O stats allocation fails, the shown path frees the server but does not visibly free the allocated ID in that branch.
- Server list removal uses `synchronize_rcu()`, so teardown can block waiting for readers.
- Procfs iteration holds `nfs_client_lock` while formatting entries and uses RCU around peer address string access.

## Testing Focus

Test version module loading/unloading, client matching across address/xprt-switch/TLS cases, concurrent mounts racing on one initializing client, RPC client flag construction, v2/v3 lockd setup, FSINFO-derived I/O clamping, server creation error unwinds, clone server setup, per-net init/exit warnings, and procfs output with live mounts.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/client.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/delegation.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/delegation.c

## Purpose

`delegation.c` manages NFSv4 file and directory delegations. It tracks delegations per inode/server/client, validates and copies delegation stateids, handles delegation recall/return, supports reclaim after recovery, tests and removes expired delegations, limits delegation cache pressure with an LRU, and coordinates state recovery when delegations become invalid.

## Main Responsibilities

- Allocate, update, attach, detach, reference, and free `struct nfs_delegation`.
- Check whether an inode has a usable read/write/time delegation.
- Copy or refresh delegation stateids for NFS operations.
- Return delegations synchronously, asynchronously, on close, on eviction, or from state-manager queues.
- Reclaim open and lock state when returning regular-file delegations.
- Expire unused, unreferenced, or all delegations.
- Mark delegations revoked, returned, bad, needing reclaim, or needing expiry tests.
- Find delegated inodes by filehandle for callback recall.
- Reap unclaimed delegations after reboot recovery and test/free expired delegations after lease loss.
- Allocate the per-server delegation hash table.

## Key Functions

- `nfs_inode_set_delegation()` installs a new delegation or updates/replaces an existing one, handling duplicate delegation cases and write-delegation upgrades.
- `nfs_inode_reclaim_delegation()` updates an existing delegation during reclaim or installs a new one if absent.
- `nfs4_get_valid_delegation()`, `nfs4_have_delegation()`, and `nfs4_check_delegation()` validate delegation type and flags under RCU.
- `nfs_async_inode_return_delegation()` marks a matching delegation for state-manager return and breaks local leases nonblocking.
- `nfs4_inode_return_delegation()` flushes data and returns a delegation synchronously.
- `nfs4_inode_set_return_delegation_on_close()` and `nfs4_inode_return_delegation_on_close()` defer returns until the last open closes when possible.
- `nfs_end_delegation_return()` breaks leases, reclaims opens/locks as needed, waits for recovery when synchronous, and sends `DELEGRETURN`.
- `nfs_client_return_marked_delegations()` is the state-manager entry for processing return queues across all client servers.
- `nfs_delegation_find_inode()` searches per-server delegation hash tables by filehandle for callback recall.
- `nfs_remove_bad_delegation()`, `nfs_delegation_mark_returned()`, and `nfs_revoke_delegation()` handle server-reported invalid delegation stateids.
- `nfs_delegation_mark_reclaim()` and `nfs_delegation_reap_unclaimed()` support reboot recovery.
- `nfs_test_expired_all_delegations()` and `nfs_reap_expired_delegations()` drive TEST/FREE_STATEID style expiry validation.
- `nfs4_copy_delegation_stateid()` and `nfs4_refresh_delegation_stateid()` provide stateid access for other NFS operations.
- `nfs4_delegation_hash_alloc()` sizes and initializes the delegation hash table from the delegation watermark.

## Control Flow and State

Delegations are visible through three structures: an RCU pointer on `nfs_inode`, a per-server `delegations` list, and a per-server filehandle hash table. A separate `entry` list node moves delegations through return, LRU, and delayed-return queues. Active delegation count is tracked by `server->nr_active_delegations`.

The main flags are `NEED_RECLAIM`, `RETURN_IF_CLOSED`, `REFERENCED`, `RETURNING`, `REVOKED`, `TEST_EXPIRED`, and `DELEGTIME`. `RETURNING` serializes return attempts. `REVOKED` invalidates local use and decrements active count. `REFERENCED` drives LRU eviction passes. `TEST_EXPIRED` drives lease-loss validation.

Delegation return for regular files can require breaking local leases, reclaiming opens, and reclaiming locks before issuing `DELEGRETURN`. If nonblocking return hits recovery or reclaim delay, the delegation is moved to delayed/return queues and the state manager retries later.

## Integration Points

- Callback recall in `callback_proc.c` calls `nfs_delegation_find_inode()` and `nfs_async_inode_return_delegation()`.
- Callback getattr uses `nfs4_get_valid_delegation()` and delegation `change_attr`.
- NFS open/lock recovery hooks are called through `nfs4_open_delegation_recall()` and `nfs4_lock_delegation_recall()`.
- Delegation return RPCs use `nfs4_proc_delegreturn()`.
- State-manager scheduling uses `NFS4CLNT_DELEGRETURN`, delayed return flags, reclaim flags, and expiry flags on `nfs_client`.
- Attribute helpers update delegated atime/mtime through declarations in `delegation.h`.

## Concurrency and Lifetime

The code combines RCU for fast delegation lookup, `clp->cl_lock` for attach/detach against inode pointers and hash/list membership, `server->delegations_lock` for queue/LRU movement, per-delegation spinlocks for mutable fields, and refcounts for delegation lifetime. Freed delegations are released with `kfree_rcu()`. Inode references are acquired with `igrab()` before operations that leave RCU protection.

## Risks and Edge Cases

- Duplicate delegations from broken servers are tolerated only for write upgrades; otherwise the new delegation is discarded or the old one is returned.
- Directory delegations can be globally disabled by the `directory_delegations` module parameter, causing return-on-close behavior.
- Nonblocking delegation return can delay and set `NFS4CLNT_DELEGRETURN_DELAYED`; the state manager sleeps briefly to avoid hard loops.
- Expiry testing can be interrupted by server reboot/session reset and requeues work with `-EAGAIN`.
- The delegation hash bucket count is based on `nfs_delegation_watermark / 16`; very small configured watermarks should be reviewed for hash sizing behavior.

## Testing Focus

Test new delegation install, in-place stateid update, duplicate delegation rejection/upgrade, return-on-close with open-file list transitions, recall while state recovery is active, lock/open reclaim failures, LRU over-watermark returns, revoke/returned stateid paths, filehandle lookup under unmount races, reclaim marking/reaping, expired delegation testing, stateid copy/refresh, and directory delegation disabled behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/delegation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/delegation.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/delegation.h

## Purpose

`delegation.h` defines the NFSv4 delegation structure, delegation flag bits, exported delegation management APIs, delegation-related NFSv4 procedure hooks, and small inline helpers for checking delegated capabilities.

## Main Contents

- `struct nfs_delegation` fields:
  - hash/list membership for filehandle lookup and server traversal
  - credential pointer
  - associated inode pointer
  - NFSv4 stateid
  - delegation type and page-modification limit
  - delegated change attribute and expiry-test generation
  - flags, refcount, spinlock, queue entry, and RCU head
- Flag bits for reclaim, return-on-close, reference tracking, active return, revoked state, expired-test state, and delegated time attributes.
- Public APIs for setting, reclaiming, returning, evicting, finding, expiring, marking, reaping, and testing delegations.
- Procedure hooks implemented elsewhere for `DELEGRETURN`, open recall, and lock recall.
- Stateid copy/refresh helpers and delegation validity checks.
- Inline helpers for read/write delegation, delegated attributes, delegated atime/mtime, directory delegation request/check, and write flush-on-close behavior.
- Declaration of the `directory_delegations` module parameter and delegation hash allocator.

## Integration Points

This header is consumed by NFS inode, open, lock, callback, state recovery, and attribute paths. It conditionally exposes most functionality under `CONFIG_NFS_V4`, while generic delegated attribute helpers remain available to call through `NFS_PROTO(inode)->have_delegation`.

## API and State Notes

Delegation references returned by functions such as `nfs4_get_valid_delegation()` must be dropped with `nfs_put_delegation()`. Optional credential outputs from `nfs4_copy_delegation_stateid()` are returned with an acquired credential reference. `NFS_DELEGATION_FLAG_TIME` asks `have_delegation` implementations to require delegated time-attribute support.

## Testing Focus

Review callers for correct reference/credential release, correct use of read versus write delegation checks, safe directory delegation requests only on directories, and correct behavior when `CONFIG_NFS_V4` is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/delegation.h -->