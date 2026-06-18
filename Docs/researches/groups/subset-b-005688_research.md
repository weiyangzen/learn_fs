# subset-b-005688 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/dev.c -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/dev.c

## Purpose
This file decodes pNFS block layout deviceid payloads into a `pnfs_block_dev` tree that can map logical file extents onto Linux block devices. It supports simple, slice, concat, stripe, and SCSI volume encodings, opens the referenced block devices, validates SCSI persistent-reservation capability, and releases device resources through the deviceid node lifecycle.

## Important APIs, types, and functions
The public entry points are `bl_alloc_deviceid_node()`, `bl_free_deviceid_node()`, and `bl_register_dev()`. `bl_alloc_deviceid_node()` decodes a `struct pnfs_device`, allocates `struct pnfs_block_volume` records, parses the top-level volume into a `struct pnfs_block_dev`, initializes the embedded `nfs4_deviceid_node`, and marks it unavailable if parsing failed. `bl_free_deviceid_node()` tears down nested device trees and frees the node with RCU. `bl_register_dev()` recursively registers SCSI PR keys for leaf devices, rolling back already-registered children on failure.

Internal mapping functions implement layout geometry: `bl_map_simple()` maps directly to one block device, `bl_map_concat()` finds the child range containing an offset, and `bl_map_stripe()` selects a child by stripe chunk and adjusts both file and disk offsets. Parser functions mirror the volume types: `nfs4_block_decode_volume()`, `bl_parse_simple()`, `bl_parse_scsi()`, `bl_parse_slice()`, `bl_parse_concat()`, and `bl_parse_stripe()`.

## Control flow
Device setup begins in `bl_alloc_deviceid_node()`: allocate an XDR scratch folio, read volume count, decode each volume, allocate the top device, and parse the final volume as the top-level mapping. Simple legacy volumes resolve a kernel `dev_t` through `bl_resolve_deviceid()` in `rpc_pipefs.c`; SCSI volumes validate code-set/designator combinations, open known `/dev/disk/by-id/` naming schemes, and require `pr_ops`. Composite volumes recursively parse referenced child indices and install the appropriate `map` callback.

## State and persistence behavior
Device state is in memory and tied to NFS deviceid cache lifetime. Leaf devices hold `struct file *bdev_file` references and SCSI leaves store a PR key plus registration flag. Composite devices own child arrays. No durable state is written by this file; externally visible persistence comes from opened block-device references and SCSI persistent reservations.

## Dependencies and integration points
The file depends on `blocklayout.h` types, Linux block APIs (`bdev_file_open_by_dev`, `bdev_file_open_by_path`, `bdev_nr_bytes`), XDR decode helpers, pNFS deviceid cache APIs, SCSI PR operations, and blocklayout tracepoints. It integrates with `rpc_pipefs.c` for legacy simple-volume device resolution and with extent/data-path code through the `pnfs_block_dev_map` callbacks.

## Risks and test signals
Key risks are malformed XDR, bad child indices, zero/unsupported devices, missing persistent-reservation operations, PR registration rollback, and stripe math overflow or divide-by-zero if a server supplies invalid counts or chunk sizes. Useful test signals include mount attempts using simple, SCSI, concat, slice, and stripe devices; unavailable deviceid marking on decode/open failures; PR register/unregister traces; and I/O path checks that mapped offsets land on expected block devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/extent_tree.c -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/extent_tree.c

## Purpose
This file maintains the pNFS block layout extent trees. It stores read-only and read-write extents in red-black trees, supports overlap-safe insertion/removal/splitting/merging, tracks written invalid extents, and encodes layoutcommit updates for block and SCSI layouts.

## Important APIs, types, and functions
External entry points are `ext_tree_insert()`, `ext_tree_lookup()`, `ext_tree_remove()`, `ext_tree_mark_written()`, `ext_tree_prepare_commit()`, and `ext_tree_mark_committed()`. The code manipulates `struct pnfs_block_layout` roots `bl_ext_ro` and `bl_ext_rw`, `struct pnfs_block_extent` nodes, and `bl_lwb` last-written-byte state.

Important helpers include `__ext_tree_search()`, `__ext_tree_insert()`, `__ext_tree_remove()`, `ext_tree_split()`, `ext_can_merge()`, `ext_try_to_merge_left()`, and `ext_try_to_merge_right()`. Commit encoding is handled by `ext_tree_try_encode_commit()`, `ext_tree_encode_commit()`, `encode_block_extent()`, and `encode_scsi_range()`.

## Control flow
Insertion chooses the RO or RW tree based on extent state, locks `bl_ext_lock`, searches for overlap, and inserts only uncovered ranges while trimming or splitting the new extent around existing nodes. Removal searches the first covered node, trims left and/or right remnants, moves fully removed nodes to a temporary list, then drops deviceid references after the spinlock is released.

When writes complete, `ext_tree_mark_written()` removes COW/hole extents from the RO tree, splits invalid RW extents to the exact written range, tags them `EXTENT_WRITTEN`, merges adjacent compatible ranges, and advances `bl_lwb`. Layoutcommit preparation first tries a page-sized buffer that must fit all written extents. If it cannot, it allocates up to `server->wsize` and encodes as many extents as possible, tagging them `EXTENT_COMMITTING`. `ext_tree_mark_committed()` either reverts committing extents to written on RPC failure or promotes them to read-write data on success.

## State and persistence behavior
All state is volatile in the layout header. The durable server-visible transition happens through encoded layoutcommit payloads. Extents hold deviceid references and must drop them when removed or merged away. Commit state tags implement a small state machine: invalid and uncommitted, written, committing, then read-write data after successful layoutcommit.

## Dependencies and integration points
The file depends on Linux rbtree/list/vmalloc/page APIs, NFS layoutcommit structures, blocklayout-private types, XDR encoding, and pNFS deviceid reference helpers. It integrates with the block layout read/write path for lookup and write completion, and with NFS layoutcommit RPC assembly through `nfs4_layoutcommit_args`.

## Risks and test signals
Main risks are off-by-one sector ranges, failing to adjust virtual offsets during splits, leaking or over-dropping deviceid references, commit buffer overflow, and invalid `lastbytewritten` when partial commits are encoded. Test signals should include overlapping layout segments, adjacent merge cases, hole/COW removal, partial commit under small `wsize`, RPC-failure retry paths, and lockdep/KASAN coverage around spinlocked tree mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/extent_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/rpc_pipefs.c -->
# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/rpc_pipefs.c

## Purpose
This file provides the rpc_pipefs upcall channel used by the pNFS block layout driver to resolve legacy simple block-volume signatures into local block device major/minor numbers. It creates a per-network-namespace pipe, handles pipefs mount/unmount notifications, sends mount requests to userspace, and receives downcall replies.

## Important APIs, types, and functions
The public lifecycle functions are `bl_init_pipefs()` and `bl_cleanup_pipefs()`. Device resolution is exposed as `bl_resolve_deviceid()`. Per-net operations are implemented by `nfs4blocklayout_net_init()` and `nfs4blocklayout_net_exit()`, while pipefs event handling uses `rpc_pipefs_event()`.

`bl_pipe_downcall()` copies a `struct bl_dev_msg` reply from userspace into `nn->bl_mount_reply`; `bl_pipe_destroy_msg()` wakes the waiter if an upcall is destroyed with an error. `nfs4_encode_simple()` builds the XDR-like simple volume payload placed after `struct bl_msg_hdr`.

## Control flow
At module initialization, the file registers a pipefs notifier and pernet subsystem. Each network namespace initializes `bl_mutex`, `bl_wq`, creates pipe data with `bl_upcall_ops`, and registers `nfs/blocklayout` in rpc_pipefs if pipefs is already mounted. Later mount/unmount events create or unlink the dentry.

`bl_resolve_deviceid()` serializes requests with `nn->bl_mutex`, appends a single-volume wrapper length, allocates an upcall buffer, queues it through `rpc_queue_upcall()`, sleeps uninterruptibly on `bl_wq`, and inspects `nn->bl_mount_reply`. A successful reply returns `MKDEV(reply->major, reply->minor)`.

## State and persistence behavior
State is per-net in `struct nfs_net`: `bl_device_pipe`, `bl_mutex`, `bl_wq`, and the most recent `bl_mount_reply`. There is no persisted kernel state, but the userspace helper's device choice influences subsequent block-device opens in `dev.c`.

## Dependencies and integration points
The file depends on SUNRPC rpc_pipefs, pernet operations, NFS netns storage, and blocklayout message structures. It integrates with `dev.c` through `bl_resolve_deviceid()` and with userspace through the `nfs/blocklayout` rpc_pipefs node.

## Risks and test signals
Risks include uninterruptible wait hangs if userspace never replies and pipe destruction does not fire, serialized request bottlenecks, stale shared reply storage, PAGE_SIZE request limits, and module/netns lifetime races around pipefs events. Tests should exercise pipefs mounted before and after module load, userspace success and malformed downcall sizes, queue failure wakeups, netns teardown, and simple-volume mount failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/blocklayout/rpc_pipefs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/cache_lib.c -->
# sources/distributed-fs/ceph-client/fs/nfs/cache_lib.c

## Purpose
This file contains shared helpers for NFS client cache upcalls and cache registration in rpc_pipefs. It launches the configured userspace cache helper, supports deferred cache requests with completion/refcount handling, and registers `struct cache_detail` objects for a superblock or network namespace.

## Important APIs, types, and functions
Exports include `nfs_cache_upcall()`, `nfs_cache_defer_req_alloc()`, `nfs_cache_defer_req_put()`, `nfs_cache_wait_for_upcall()`, `nfs_cache_register_net()`, `nfs_cache_unregister_net()`, `nfs_cache_register_sb()`, and `nfs_cache_unregister_sb()`. Module parameters `cache_getent` and `cache_getent_timeout` control the userspace helper path and wait timeout.

Deferred request plumbing is implemented by `nfs_dns_cache_defer()` and `nfs_dns_cache_revisit()`, which connect SUNRPC cache deferral callbacks to `struct completion`.

## Control flow
`nfs_cache_upcall()` constructs argv as helper path, cache name, and entry name, then calls `call_usermodehelper()` with `UMH_WAIT_EXEC`. If the helper is missing or denied, it clears the helper path to disable further upcalls until the admin resets the module parameter.

For deferred cache misses, callers allocate `struct nfs_cache_defer_req`, pass its embedded `cache_req`, and wait in `nfs_cache_wait_for_upcall()`. The cache subsystem calls the defer hook, which increments the refcount and returns the embedded deferred request. Revisit completes the waiter and drops that extra reference.

## State and persistence behavior
The helper path and timeout are module-wide tunables. Deferred request state is heap allocated and released by refcount. Cache registration state lives in SUNRPC cache/rpc_pipefs infrastructure; this file initializes/destroys `cache_detail` objects around registration.

## Dependencies and integration points
Dependencies include Linux kmod/usermodehelper APIs, completions, refcounts, SUNRPC cache APIs, rpc_pipefs superblock lookup, and network namespace handling. NFS DNS or ID-mapping style client caches use this library rather than duplicating upcall and pipefs registration code.

## Risks and test signals
Risks include disabled upcalls after transient `ENOENT`/`EACCES`, timeout tuning that is too short for slow helpers, refcount leaks in deferred paths, and missing pipefs superblocks causing registration to be skipped. Tests should cover helper success/failure, timeout, revisit completion, unregister after partial register failure, and per-net pipefs availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/cache_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/cache_lib.h -->
# sources/distributed-fs/ceph-client/fs/nfs/cache_lib.h

## Purpose
This header declares the shared NFS client cache helper interface and defines the deferred request wrapper used by `cache_lib.c`.

## Important APIs, types, and functions
`struct nfs_cache_defer_req` embeds `struct cache_req`, `struct cache_deferred_req`, a `completion`, and a `refcount_t`. The declarations expose helper launching, deferred request allocation/release/waiting, and cache registration/unregistration for both network namespaces and rpc_pipefs superblocks.

## Control flow
Users allocate a deferred request, submit or attach it to SUNRPC cache handling through the embedded `cache_req`, then wait on completion and release their reference. Registration callers pass a prepared `struct cache_detail` to the net or superblock helpers.

## State and persistence behavior
The header defines only transient in-kernel state. Lifetime is explicit through refcounting, and completion state represents one outstanding cache upcall wait.

## Dependencies and integration points
It depends on Linux completion, SUNRPC cache, and atomic/refcount headers. It is consumed by NFS client cache implementations that need rpc_pipefs-visible cache_detail entries and userspace upcalls.

## Risks and test signals
The main risk is misuse of the embedded objects: callers must not free the wrapper before the cache subsystem releases deferred references. Compile coverage should verify all users include the proper net/superblock forward declarations; runtime tests should exercise deferred request completion and timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/cache_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback.c -->
# sources/distributed-fs/ceph-client/fs/nfs/callback.c

## Purpose
This file owns the NFSv4 callback service lifecycle and authentication policy. It creates and shares SUNRPC callback services per NFS minor version, binds per-network-namespace callback transports, starts/stops svc threads, wires v4.1+ backchannel transports, and validates callback credentials.

## Important APIs, types, and functions
The exported lifecycle entry points are `nfs_callback_up()` and `nfs_callback_down()`. Authentication support is provided by `check_gss_callback_principal()` and the program-level `nfs_callback_authenticate()`. `nfs_callback_info[]` tracks users and `svc_serv` pointers per minor version under `nfs_callback_mutex`.

Important helpers include `nfs_callback_create_svc()`, `nfs_callback_up_net()`, `nfs_callback_down_net()`, `nfs_callback_start_svc()`, `nfs_callback_bc_serv()`, and the svc-thread function `nfs4_callback_svc()`.

## Control flow
`nfs_callback_up()` serializes with a global mutex, creates the `svc_serv` if needed, increments per-net callback use by binding the service, creates TCP/IPv4 and TCP/IPv6 listeners for NFSv4.0, enables backchannel service for minor versions with `bc_setup`, starts the configured number of svc threads, and increments global users. Error paths unwind per-net users, threads, and the service if no users remain.

`nfs_callback_down()` decrements per-net users, destroys transports for that net when the last user leaves, decrements global users, and destroys the service/backchannel binding when the minor-version user count reaches zero.

## State and persistence behavior
State is runtime-only: global per-minor callback service refs, per-net `cb_users[]`, callback TCP ports, and backchannel `bc_serv`. No durable state is written. Service lifetime is tied to mounted NFS clients and their transports.

## Dependencies and integration points
The file depends on SUNRPC svc and socket layers, backchannel transport support, netns storage, GSS auth helpers, module parameters declared elsewhere, and callback XDR service versions from `callback_xdr.c`. It integrates with NFSv4 client setup/teardown and with session backchannel creation.

## Risks and test signals
Risks include reference-count imbalance across minor versions/net namespaces, IPv6 listener partial failure handling, unsupported backchannel transports, GSS principal mismatch, and callback thread count changes. Test signals include v4.0 callback listener port publication, v4.1 session backchannel setup, mount/unmount reference churn across netns, AUTH_NULL only for `CB_NULL`, and GSS callback acceptance/rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback.h -->
# sources/distributed-fs/ceph-client/fs/nfs/callback.h

## Purpose
This header defines the NFSv4 callback ABI used between callback XDR decoding, callback procedure handlers, and the callback service. It provides procedure numbers, buffer sizing, compound state, operation argument/result structures, and callback function prototypes.

## Important APIs, types, and functions
Core definitions include `NFS4_CALLBACK`, `NFS4_CALLBACK_XDRSIZE`, `NFS4_CALLBACK_BUFSIZE`, `enum nfs4_callback_procnum`, and `struct cb_process_state`. Operation structures cover `CB_GETATTR`, `CB_RECALL`, `CB_SEQUENCE`, `CB_RECALL_ANY`, `CB_RECALL_SLOT`, `CB_LAYOUTRECALL`, `CB_NOTIFY_DEVICEID`, `CB_NOTIFY_LOCK`, and optional v4.2 `CB_OFFLOAD`.

The header declares procedure handlers such as `nfs4_callback_getattr()`, `nfs4_callback_recall()`, `nfs4_callback_sequence()`, `nfs4_callback_layoutrecall()`, `nfs4_callback_devicenotify()`, and service lifecycle functions `nfs_callback_up()`/`nfs_callback_down()`.

## Control flow
The structures here are populated by `callback_xdr.c`, consumed by `callback_proc.c`, and referenced by `callback.c` service setup. `cb_process_state` is the per-compound carrier for the matched `nfs_client`, backchannel slot, network namespace, minor version, duplicate-reply-cache status, and referring-call count.

## State and persistence behavior
The header defines transient RPC argument/result and per-compound state only. Constants such as callback slot limits shape runtime session/backchannel behavior but do not persist.

## Dependencies and integration points
It depends on SUNRPC svc types and NFS/pNFS state types pulled indirectly through NFS headers. It is the shared contract among callback service, XDR, procedure, delegation, pNFS, and NFSv4.2 copy-offload code.

## Risks and test signals
Risks are ABI drift between decode structures and procedure handlers, incorrect callback buffer sizing, and conditional compilation mismatches for v4.2 offload. Compile-time coverage across `CONFIG_NFS_V4` and `CONFIG_NFS_V4_2` plus callback operation interoperability tests are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback_proc.c -->
# sources/distributed-fs/ceph-client/fs/nfs/callback_proc.c

## Purpose
This file implements NFSv4 callback operations after XDR decoding. It handles delegation GETATTR/RECALL, pNFS layout recall and device notifications, v4.1 backchannel sequencing, recall-any and recall-slot requests, lock notifications, and optional v4.2 server-side copy offload completion.

## Important APIs, types, and functions
Exported procedure handlers include `nfs4_callback_getattr()`, `nfs4_callback_recall()`, `nfs4_callback_layoutrecall()`, `nfs4_callback_devicenotify()`, `nfs4_callback_sequence()`, `nfs4_callback_recallany()`, `nfs4_callback_recallslot()`, `nfs4_callback_notify_lock()`, and optional `nfs4_callback_offload()`.

Important helpers include inode lookup by delegation filehandle, layout lookup by stateid or filehandle, `pnfs_check_callback_stateid()`, `initiate_file_draining()`, `initiate_bulk_draining()`, `validate_seqid()`, and `referring_call_exists()`.

## Control flow
Delegation callbacks locate the target inode through the client delegation hash. GETATTR returns change, size, and delegated time attributes only for valid write delegations. RECALL schedules asynchronous delegation return and maps local errors to NFSv4 statuses.

Layout recall locates a layout by stateid or filehandle, commits pending layout data, validates recall sequencing, updates layout stateid, marks matching layout segments for return, and frees commit bucket lsegs. Bulk recalls destroy layouts by fsid or client id. Device notifications iterate decoded notifications, find matching layout drivers, and delete deviceids.

`nfs4_callback_sequence()` validates the session id, backchannel flag, slot id, slot sequence id, cachethis policy, and referring calls before locking the backchannel slot and setting `cps->clp`. Later compound processing frees the slot. Recall-any expires delegation types or triggers pNFS layout recall/state-manager work. Recall-slot lowers the forechannel target slot id.

## State and persistence behavior
The file mutates in-memory NFS client state: delegation return queues, inode attributes, pNFS layout flags and stateids, deviceid cache entries, session slot tables, client state bits, lock wait queues, and copy-offload completion lists. Persistence is protocol-level only: actions schedule RPC state-manager work or complete pending client operations.

## Dependencies and integration points
Dependencies include delegation management, pNFS layout APIs, NFSv4 session slot tables, NFS state manager, tracepoints, lock wait queues, and optional NFSv4.2 copy state. It is invoked exclusively by `callback_xdr.c` after operation decode/preprocessing.

## Risks and test signals
Risks include callback processing without a valid `cps->clp`, slot sequence bugs causing replay/misorder behavior, layout recall races with layoutcommit and bulk recall, wrong stateid comparisons, and memory ownership for decoded device/referring-call arrays. Tests should include v4.0 delegation recalls, v4.1 compound ordering with `CB_SEQUENCE`, layout file/bulk recalls, deviceid delete/change notifications, recall-any type masks, and offload callback matching plus pending-state fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback_xdr.c -->
# sources/distributed-fs/ceph-client/fs/nfs/callback_xdr.c

## Purpose
This file is the XDR dispatch layer for the NFSv4 callback RPC program. It decodes callback COMPOUND headers and operation arguments, enforces minor-version operation rules, dispatches to callback procedure handlers, encodes operation and compound results, and defines the callback RPC service versions.

## Important APIs, types, and functions
The central dispatch path is `nfs4_callback_compound()` -> `process_op()` -> callback operation table entries. `struct callback_op` binds `decode_args`, `process_op`, `encode_res`, and response-size accounting for each supported operation. Service version objects `nfs4_callback_version1` and `nfs4_callback_version4` are exported for `callback.c`.

Decode helpers include `decode_string()`, `decode_fh()`, `decode_bitmap()`, `decode_stateid()`, `decode_layoutrecall_args()`, `decode_devicenotify_args()`, `decode_cb_sequence_args()`, `decode_recallany_args()`, `decode_notify_lock_args()`, and optional `decode_offload_args()`. Encode helpers cover compound/op headers, GETATTR attributes, and CB_SEQUENCE results.

## Control flow
The COMPOUND handler decodes tag, minor version, callback identifier, and op count. For v4.0 it resolves the client by callback ident and validates GSS principal. It writes a placeholder compound response header, then loops operations until an error or all ops are processed.

`process_op()` decodes the opcode, applies minor-version preprocessing, decodes arguments only when enough response buffer remains, calls the operation handler, writes the per-op status, and encodes operation-specific results on success. v4.1+ preprocessing requires `CB_SEQUENCE` first and rejects non-session operations before sequence. v4.2 preprocessing adds `CB_OFFLOAD` when configured.

## State and persistence behavior
The file owns per-request decode allocations for device notification arrays and referring-call lists, but persistent state changes occur in the procedure handlers. It sets request backchannel timeouts after a successful matched client and stores DRC-related status in `cb_process_state`.

## Dependencies and integration points
Dependencies include SUNRPC svc/xdr streams, NFSv4 protocol constants, backchannel transport helpers, callback procedure prototypes, NFS client lookup, and tracepoints. It integrates with `callback.c` through service version tables and with `callback_proc.c` through the operation table.

## Risks and test signals
Risks include XDR length validation mistakes, memory leaks on partial decode failure, incorrect operation legality by minor version, response buffer overflow, invalid credential handling for v4.0, and optional v4.2 table coverage. Tests should fuzz callback XDR, verify rejected illegal op sequences, exercise resource-header overflow mapping, run GSS principal acceptance/rejection, and use KASAN/KMEMLEAK around device/referring-call decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/callback_xdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/client.c -->
# sources/distributed-fs/ceph-client/fs/nfs/client.c

## Purpose
This file manages shared NFS clients and mounted NFS server records. It registers NFS protocol subversions, allocates and shares `struct nfs_client` objects, creates RPC clients, initializes v2/v3 server records, probes filesystem information, manages server lists and procfs output, and handles per-net NFS client state.

## Important APIs, types, and functions
Protocol registration APIs are `register_nfs_version()`, `unregister_nfs_version()`, `find_nfs_version()`, `get_nfs_version()`, and `put_nfs_version()`. Client lifecycle APIs include `nfs_alloc_client()`, `nfs_get_client()`, `nfs_init_client()`, `nfs_put_client()`, `nfs_free_client()`, `nfs_mark_client_ready()`, and `nfs_wait_client_init_complete()`.

Server lifecycle and setup APIs include `nfs_alloc_server()`, `nfs_create_server()`, `nfs_clone_server()`, `nfs_free_server()`, `nfs_init_server_rpcclient()`, `nfs_server_set_init_caps()`, `nfs_probe_server()`, `nfs_server_insert_lists()`, and `nfs_server_remove_lists()`. Net/proc hooks include `nfs_clients_init()`, `nfs_clients_exit()`, `nfs_fs_proc_net_init()`, `nfs_fs_proc_net_exit()`, `nfs_fs_proc_init()`, and `nfs_fs_proc_exit()`.

## Control flow
Mount setup calls into `nfs_create_server()`, which allocates a server, initializes a shared client through `nfs_init_server()`, probes fsinfo/pathconf, sets FSID and capability state, inserts the server into client/net lists, and returns a mounted server record. `nfs_get_client()` searches the per-net client list under lock, waits for in-progress client initialization when needed, or allocates and inserts a new client before invoking version-specific init.

RPC setup starts from `nfs_init_timeout_values()` and `nfs_create_rpc_client()`, then `nfs_init_server_rpcclient()` clones the shared client with mount-selected auth. v2/v3 setup starts lockd unless local flock/fcntl options avoid it. Probe logic uses version-specific `set_capabilities`, `fsinfo`, `pathconf`, and optional trunking discovery.

## State and persistence behavior
Persistent kernel runtime state includes per-net client and volume lists, client refcounts and construction state, RPC clients, sysfs/procfs visibility, server flags/sizes/cache timers/capabilities, lockd host state, pNFS wait queues, delegation lists, and fscache/proc output. State is released with RCU for clients and servers.

## Dependencies and integration points
The file integrates with SUNRPC transports and auth, NFS version modules, lockd, fs_context mount parsing, sysfs, procfs, fscache, pNFS, NFS localio, NFSv4 callback IDR state, and net namespaces. It is central glue between mount-time configuration and protocol-specific NFS operations.

## Risks and test signals
Risks include client-sharing mismatches across address/xprtsec/minor version, waiting races during client initialization, refcount/list imbalance, error unwinding after partially initialized lockd/RPC/sysfs state, and procfs iteration over live lists. Tests should cover concurrent mounts to the same and different endpoints, TLS xprtsec matching, failed RPC creation, v2/v3 lockd setup, fsinfo bounds on I/O sizes, clone server cleanup, netns teardown warnings, and procfs server/volume output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/delegation.c -->
# sources/distributed-fs/ceph-client/fs/nfs/delegation.c

## Purpose
This file implements NFSv4 delegation lifecycle management. It installs and updates delegations on inodes, checks and copies delegation stateids for I/O, returns delegations synchronously or asynchronously, handles recalls/revocation/reclaim after recovery, expires unused delegations, and maintains per-server delegation hash/LRU/return lists.

## Important APIs, types, and functions
Important external APIs include `nfs_inode_set_delegation()`, `nfs_inode_reclaim_delegation()`, `nfs4_have_delegation()`, `nfs4_get_valid_delegation()`, `nfs4_copy_delegation_stateid()`, `nfs4_refresh_delegation_stateid()`, `nfs_async_inode_return_delegation()`, `nfs4_inode_return_delegation()`, `nfs4_inode_return_delegation_on_close()`, `nfs_inode_evict_delegation()`, `nfs_delegation_find_inode()`, `nfs_client_return_marked_delegations()`, `nfs_expire_all_delegations()`, `nfs_expire_unused_delegation_types()`, `nfs_expire_unreferenced_delegations()`, `nfs_delegation_mark_reclaim()`, `nfs_delegation_reap_unclaimed()`, `nfs_test_expired_all_delegations()`, `nfs_reap_expired_delegations()`, and `nfs4_delegation_hash_alloc()`.

## Control flow
Setting a delegation allocates and initializes `struct nfs_delegation`, then under `cl_lock` either attaches it to the inode/server hash/list, updates an existing matching delegation, or handles duplicate delegations by allowing write-upgrades and returning/revoking the old delegation. Reclaim updates existing delegation state after recovery and clears reclaim/revoked markers.

Return begins by marking `NFS_DELEGATION_RETURNING`, clearing delegated verifiers, breaking leases, flushing writeback when synchronous, reclaiming delegated opens and locks, and sending `nfs4_proc_delegreturn()`. Async returns move delegations to `server->delegations_return` and set client state-manager bits. Close paths either return immediately when no opens remain or place delegations on LRU for later pressure-based return.

Revocation and bad delegation handling mark stateids invalid, decrement active counts, detach from inode/hash/list when appropriate, and schedule state recovery. Expired delegation handling marks candidates, calls minor-version `test_and_free_expired()`, and restarts if server reboot/session-reset state appears.

## State and persistence behavior
Delegation state is stored in `struct nfs_delegation` under RCU plus per-delegation spinlock: stateid, cred, inode pointer, type, pagemod limit, change attr, flags, refcount, and list/hash membership. Per-server state includes delegation hash table, `delegations`, `delegations_return`, `delegations_lru`, `delegations_delayed`, active count, generation, and delegation flags. Durable protocol effects are delegation return/free-stateid/test-expired RPCs and state recovery scheduling.

## Dependencies and integration points
The file depends on NFSv4 state/open/lock recovery, inode cache validity, writeback, leases, state manager scheduling, minor-version ops, server lists from `client.c`, and callback recall paths from `callback_proc.c`. Directory delegation behavior is controlled by the `directory_delegations` module parameter; pressure is controlled by `delegation_watermark`.

## Risks and test signals
Risks include RCU/refcount/list lifetime bugs, deadlocks while reclaiming opens/locks, duplicate delegation server behavior, forgetting to clear RETURNING after delayed failure, active-count imbalance on revoke/reclaim, and recovery loops during server reboot. Tests should cover read/write delegation grant, upgrade, recall, close-triggered return, LRU pressure return, expired/revoked stateids, recovery reclaim/reap, directory delegation disablement, and lock/open reclaim under delegation recall.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/delegation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/delegation.h -->
# sources/distributed-fs/ceph-client/fs/nfs/delegation.h

## Purpose
This header declares NFSv4 delegation data structures, flags, lifecycle APIs, and convenience helpers for checking delegated attributes and times. It is the shared interface between NFS open/I/O paths, callback recall handling, state recovery, and delegation implementation.

## Important APIs, types, and functions
`struct nfs_delegation` contains hash/list links, credential, inode pointer, stateid, type, pagemod limit, change attr, generation, flags, refcount, spinlock, return/LRU list entry, and RCU head. Flag bits cover reclaim, return-on-close, referenced, returning, revoked, test-expired, and delegated-time support.

The header declares delegation install/reclaim/return/evict/find/expire/recover APIs, NFSv4 delegation RPC helpers, stateid copy/refresh helpers, and `nfs4_delegation_hash_alloc()`. Inline helpers include `nfs_have_read_or_write_delegation()`, `nfs_have_write_delegation()`, delegated attribute/time checks, and directory delegation request/status helpers.

## Control flow
Callers use inline checks through `NFS_PROTO(inode)->have_delegation()` on hot paths, while more complex lifecycle events call the exported functions implemented in `delegation.c`. Callback code uses `nfs_delegation_find_inode()` and async return APIs; recovery code uses reclaim/reap/test-expired APIs.

## State and persistence behavior
The header defines in-memory delegation state and module-visible flags. It does not persist data, but its stateid and credential fields are used for protocol RPCs that return, test, or reclaim delegation state on the server.

## Dependencies and integration points
It is enabled for the main delegation structures only under `CONFIG_NFS_V4`, while generic delegated timestamp helper declarations remain available. It integrates with `nfs_fs`, NFS protocol ops, VFS inode mode checks, NFSv4 stateids, and module parameter `directory_delegations`.

## Risks and test signals
Risks include callers assuming delegation APIs exist outside `CONFIG_NFS_V4`, misuse of inline delegation checks for directories, and state structure changes not reflected in locking/refcount rules. Compile tests across NFSv4 enabled/disabled configs and runtime tests of delegated atime/mtime helpers are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/delegation.h -->
