# Research: subset-b-001053

Grouped research for DRBD core internal declarations, interval-tree helpers, and main module/lifecycle implementation under `sources/distributed-fs/ceph-client/drivers/block/drbd`. Each section is source-tree aligned for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_int.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_int.h

## Purpose
`drbd_int.h` is the private integration header for the in-kernel DRBD block driver. It defines the shared runtime objects for resources, connections, peer devices, local devices, requests, peer requests, activity-log and bitmap metadata, worker queues, counters, and state helpers. It is the contract used by `drbd_main.c`, request handling, receiver/worker code, activity-log code, bitmap code, netlink administration, proc/debugfs reporting, and protocol send/receive logic.

## Important APIs, Types, And Functions
Important types include `struct drbd_resource`, `struct drbd_connection`, `struct drbd_device`, `struct drbd_peer_device`, `struct drbd_request`, `struct drbd_peer_request`, `struct drbd_epoch`, `struct drbd_thread`, `struct drbd_work_queue`, `struct drbd_socket`, `struct drbd_md`, `struct drbd_backing_dev`, `struct drbd_md_io`, `struct bm_io_work`, `struct bm_xfer_ctx`, `struct bm_extent`, and `struct drbd_config_context`. Key enums and flags cover fault injection, thread state, transfer-log epochs, peer-request flags, per-device work bits, bitmap lock modes, per-connection flags, device-size decisions, sync-bit update mode, and force-detach reasons.

The header declares the major DRBD service surface: thread lifecycle (`drbd_thread_start`, `_drbd_thread_stop`), protocol sends (`drbd_send_*`, `conn_send_*`), transfer-log control (`tl_release`, `tl_clear`), metadata I/O and UUID mutation (`drbd_md_read`, `drbd_md_sync`, `drbd_uuid_*`, `drbd_md_*_flag`), bitmap I/O (`drbd_bm_*`, `drbd_bitmap_io`, `drbd_queue_bitmap_io`), resource/connection/device lifecycle (`drbd_create_resource`, `conn_create`, `drbd_create_device`, destroy/delete helpers), block request entry (`drbd_submit_bio`, `__drbd_make_request`), worker/receiver callbacks, activity-log and resync helpers, and notification hooks.

Inline helpers are central to correctness: `minor_to_device`, `first_peer_device`, `conn_peer_device`, `drbd_read_state`, metadata layout helpers (`drbd_md_first_sector`, `drbd_md_last_sector`, `drbd_md_ss`, `drbd_get_max_capacity`), work queue helpers, ping/wakeup helpers, request counters (`inc_ap_pending`, `dec_ap_pending`, `inc_rs_pending`, `inc_unacked`), local disk reference management (`get_ldev`, `put_ldev`), application I/O admission (`may_inc_ap_bio`, `inc_ap_bio`, `dec_ap_bio`), sync-state predicates, and `drbd_chk_io_error`.

## Control Flow
The file is declarative, but it encodes DRBD's main control paths. Application bios enter through `drbd_submit_bio` and become `struct drbd_request` objects tracked by `drbd_interval`, pending-completion lists, transfer-log lists, local-disk state, and network acknowledgement counters. Peer requests enter through receiver code as `struct drbd_peer_request`, run local I/O or resync paths, and complete through worker callbacks and acknowledgement sends. Resource-level `req_lock` protects request state, interval trees, counters, and many state transitions.

Connection control is split across three kernel threads stored in `struct drbd_connection`: receiver, worker, and ack receiver. The sender side uses `struct drbd_work_queue` and device-posted work bits. Protocol messages use two sockets (`data` and `meta`) with preallocated send/receive buffers and per-socket mutexes. State changes and administrative operations flow through resource/connection/device objects, RCU-protected configuration pointers, idr maps, and netlink notification declarations.

Bitmap and activity-log flow is also expressed here: bitmap bits represent 4 KiB blocks, bitmap extents represent 16 MiB, and activity-log extents represent 4 MiB. Application write admission increments `ap_bio_cnt`; if bitmap I/O is pending, `dec_ap_bio` queues `bm_io_work` once in-flight application I/O reaches zero. Resync helpers manage `resync` LRU elements, pending resync counters, and sync-bit transitions.

## State And Persistence
Persistent in-memory state is structured in three layers. `drbd_resource` owns the resource name, devices idr, connections list, resource options, suspension flags, CPU mask, write ordering, and the main request lock. `drbd_connection` owns protocol state, network configuration, sockets, crypto transforms, transfer log, epoch tracking, sender work queue, thread objects, and cached oldest-request pointers. `drbd_device` owns the virtual disk, local backing device, metadata state, timers, request interval trees, pending completion lists, bitmap, activity log, resync state, peer request lists, counters, capacity, UUID exposure, and per-device work.

Persistent on-disk behavior is represented through `struct drbd_md` and constants for internal, flexible internal, flexible external, and old fixed metadata layouts. The header defines bitmap granularity, maximum supported sizes, metadata sector calculations, and activity-log transaction sizing. `MD_DIRTY`, `MDF_*` flags, UUID fields, and bitmap locks are the bridge between volatile state and metadata stored on backing or external metadata devices.

Reference and lifetime state is explicit: resources, connections, and devices use `kref`; local disk access uses `local_cnt` plus `get_ldev`/`put_ldev`; application and network in-flight work is tracked by atomics such as `ap_bio_cnt`, `ap_pending_cnt`, `rs_pending_cnt`, `unacked_cnt`, `pp_in_use`, and `ap_in_flight`.

## Dependencies
The header depends on Linux block, bio, idr, list, rbtree, timer, waitqueue, socket, crypto hash, ratelimit, TCP, slab, lru-cache, RCU, and cpumask APIs. It includes DRBD public UAPI/config/protocol/state/string headers and `drbd_interval.h`. It assumes many symbols are implemented by sibling files: `drbd_main.c`, `drbd_req.c`, `drbd_receiver.c`, `drbd_worker.c`, `drbd_actlog.c`, `drbd_bitmap.c`, `drbd_nl.c`, and `drbd_proc.c`.

## Integration Points
This header is the integration point for nearly every DRBD subsystem. Block-layer entry uses `drbd_submit_bio` and `drbd_ops` from main code. Network code consumes `drbd_send_*` declarations and socket structures. Receiver and worker code consume peer-request flags and callbacks. Activity-log code consumes `struct drbd_interval`, AL constants, and bitmap/resync APIs. Netlink administration uses `drbd_config_context`, resource/connection/device constructors, state setters, and notification prototypes. Debugfs and proc reporting read resource, connection, device, and timing state.

## Risks
The main risk is shared-state coupling: layout or locking mistakes in this header propagate across all DRBD objects. `first_peer_device(device)` is used by many helpers and assumes at least one peer device exists; misuse during partial construction or teardown can crash. RCU-protected `net_conf` and `disk_conf` fields must only be dereferenced under the right read-side protection or update mutex. `get_ldev` and `put_ldev` combine state checks, reference counts, and worker-posted disk-destroy operations; missing a `put_ldev` leaks detach progress, while using `ldev` without a reference risks use-after-free. Application I/O throttling relies on `req_lock`, `ap_bio_cnt`, `BITMAP_IO`, stable state checks, and wait queues staying consistent.

Metadata constants are compatibility-sensitive: bitmap granularity, activity-log extent sizing, maximum sectors, and metadata offsets must match userspace tools such as `drbdmeta`. Several helpers call `first_peer_device(device)->connection` inline, so future multi-peer or partial-object changes need careful audit. Fault injection and forced detach paths intentionally change I/O outcomes and must stay gated by config and state.

## Test Signals
Useful signals include full DRBD build coverage with sparse/lockdep, attach/detach tests for all metadata layouts, local disk failure and forced-detach tests, application I/O under suspend/resume and bitmap I/O, transfer-log and barrier acknowledgement tests, resync and online-grow tests, multi-resource CPU mask assignment, netlink create/delete resource/connection/device tests, protocol-version matrix tests, and fault-injection runs covering data, metadata, bitmap, resync, allocation, and receive corruption paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.c

## Purpose
`drbd_interval.c` implements DRBD's augmented red-black interval tree helpers. DRBD uses these trees to track in-flight local and peer I/O ranges, detect overlapping requests, and wait/restart conflicting operations without scanning every request.

## Important APIs, Types, And Functions
The file implements `drbd_insert_interval`, `drbd_contains_interval`, `drbd_remove_interval`, `drbd_find_overlap`, and `drbd_next_overlap`. Internal helpers are `interval_end`, `NODE_END`, and `RB_DECLARE_CALLBACKS_MAX`-generated `augment_callbacks`. The implementation operates on `struct drbd_interval` from `drbd_interval.h`, where `sector` is the start sector, `size` is bytes, and `end` caches the maximum end sector in a subtree.

## Control Flow
`drbd_insert_interval` verifies 512-byte alignment, walks the tree by start sector, and uses pointer address ordering to break ties when multiple intervals start at the same sector. During descent it opportunistically raises ancestor `end` values to include the new interval end, then links and rebalances the node with augmented rbtree callbacks. If the exact same interval node is already present, it returns `false`.

`drbd_contains_interval` searches by the caller-supplied sector and pointer ordering. It is intentionally safe for membership checks where the interval pointer may be invalid or stale: it does not dereference the interval argument unless the tree search has proven identity by pointer comparison. `drbd_remove_interval` ignores already-cleared nodes to avoid repeated erase loops and otherwise calls `rb_erase_augmented`.

`drbd_find_overlap` searches for the first interval overlapping `[sector, sector + size)`. It first follows a left subtree if that subtree's augmented maximum end could overlap the query. Otherwise it checks the current node, then moves right if the query starts at or after the current node's sector. When it finds an overlap, the returned node is the lowest-start overlapping interval; other overlaps can be found via `drbd_next_overlap`. `drbd_next_overlap` walks `rb_next` until it reaches the query end or finds another interval whose end exceeds the query start.

## State And Persistence
The file owns no global state and performs no persistence. It mutates only the passed `rb_root` and the embedded `rb_node`/`end` fields inside `struct drbd_interval`. Tree lifetime, synchronization, and interval ownership are controlled by callers, typically under DRBD's request lock. `end` is derived state and must stay synchronized with `sector` and `size`.

## Dependencies
It depends on Linux rbtree augmented callbacks, sector types, alignment macros, `BUG_ON`, and `drbd_interval.h`. It assumes sizes are 512-byte aligned because all interval math converts bytes to sectors with `size >> 9`.

## Integration Points
`drbd_device` embeds separate `read_requests` and `write_requests` rb roots, and `struct drbd_request` and `struct drbd_peer_request` embed `struct drbd_interval`. Activity-log and request paths use overlap detection to prevent conflicting local/remote writes, coordinate two-primary conflict handling, and decide when requests must wait on `device->misc_wait`.

## Risks
The interval tree relies on strict invariants: callers must initialize nodes with `drbd_clear_interval`, must not mutate `sector` or `size` while inserted, must not insert unaligned sizes, and must erase before freeing an interval owner. Pointer-order tie breaking is deterministic only within one kernel lifetime and is suitable for in-memory identity, not persisted ordering. `drbd_remove_interval` does not clear the node after erase; callers that need `drbd_interval_empty` to become true must clear it themselves. Missing caller-side locking can corrupt the rb tree or the augmented `end` values. Integer overflow in `sector + (size >> 9)` is not guarded here and is expected to be prevented by upper-layer block-size limits.

## Test Signals
Focused tests should insert overlapping and non-overlapping intervals, duplicate start-sector intervals, exact duplicate nodes, left-subtree-only overlaps, removal/reinsertion sequences, and `drbd_for_each_overlap` iteration order. Stress signals include concurrent DRBD request workloads under lockdep, two-primary conflict tests, activity-log wait/retry tests, and boundary cases near maximum bio size and high sector numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.h -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.h

## Purpose
`drbd_interval.h` declares the interval node used by DRBD request and peer-request tracking, plus the public helpers for insertion, removal, membership checks, overlap lookup, and overlap iteration. It is the small data-structure contract behind DRBD's in-flight range conflict detection.

## Important APIs, Types, And Functions
`struct drbd_interval` contains an embedded `rb_node`, start `sector`, augmented subtree `end`, byte `size`, bitfields for `local`, `waiting`, and `completed`, and `partially_in_al_next_enr` for resuming partially successful activity-log admission. Inline helpers are `drbd_clear_interval`, which clears rb-node membership state, and `drbd_interval_empty`, which tests `RB_EMPTY_NODE`. Exported functions are `drbd_insert_interval`, `drbd_contains_interval`, `drbd_remove_interval`, `drbd_find_overlap`, and `drbd_next_overlap`. `drbd_for_each_overlap` wraps the find/next sequence.

## Control Flow
The header does not implement the search algorithms beyond inlines and the iteration macro. Callers initialize an interval, fill `sector` and `size`, insert it into a selected rb root, and later use `drbd_for_each_overlap` to scan conflicting intervals for a target range. The `waiting` flag lets code mark intervals whose owner is sleeping for progress, and `completed` lets conflict detection ignore requests that have already completed but may still be present for cleanup or accounting.

## State And Persistence
Intervals are transient in-memory state embedded in higher-level request objects. `sector` and `size` describe the range, `end` is maintained by the augmented tree implementation, and flags describe request-local conflict/wait status. There is no on-disk persistence in this file, but interval state influences when activity-log updates and replicated writes can proceed.

## Dependencies
The header depends on Linux `types.h` and `rbtree.h`. It is included by `drbd_int.h` so that `struct drbd_request`, `struct drbd_peer_request`, activity-log code, and request code can embed and manipulate intervals.

## Integration Points
The interval API integrates with `drbd_device.read_requests` and `drbd_device.write_requests`, request submission, peer request handling, activity-log functions (`drbd_al_begin_io*`, `drbd_al_complete_io`), and `drbd_wait_misc`. The `partially_in_al_next_enr` field is specifically tied to resuming `drbd_al_begin_io_nonblock` after partial progress.

## Risks
Because this structure is embedded in live I/O objects, caller ordering is critical: the rb node must be cleared before first use, inserted only once, removed before owner free, and protected by the appropriate DRBD lock. `size` is bytes while `sector` and `end` are sectors, so callers must keep 512-byte alignment. The flags are compact bitfields, which is convenient but can hide concurrency assumptions; simultaneous updates without the request lock would be unsafe.

## Test Signals
Build coverage catches struct/API mismatches. Runtime signals include activity-log conflict tests, read/write overlap tests, two-primary conflict tests, request restart behavior after waits, and assertions that interval nodes are empty after completion and teardown. Unit-style interval tests should validate the macro iterates all and only overlapping intervals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_main.c -->
# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_main.c

## Purpose
`drbd_main.c` is the core implementation file for DRBD module initialization, block-device registration, resource/connection/device lifecycle, kernel thread management, protocol packet construction and sending, transfer-log handling, socket cleanup, bitmap transfer orchestration, metadata superblock I/O, UUID management, bitmap I/O scheduling, workqueue flushing, and fault injection. It turns the contracts in `drbd_int.h` into the primary runtime objects and exported functions used by the rest of the driver.

## Important APIs, Types, And Functions
Module/global state includes module parameters (`minor_count`, `usermode_helper`, `proc_details`, `allow_oos`, `disable_sendpage`, and optional fault-injection parameters), `drbd_devices`, `drbd_resources`, `resources_mutex`, slab caches, mempools, bio sets, and `drbd_ratelimit_state`. `drbd_ops` exposes `submit_bio`, `open`, and `release` to the block layer.

Important lifecycle functions are `drbd_init`, `drbd_cleanup`, `drbd_create_mempools`, `drbd_destroy_mempools`, `drbd_create_resource`, `drbd_free_resource`, `drbd_destroy_resource`, `conn_create`, `drbd_destroy_connection`, `drbd_create_device`, `drbd_delete_device`, `drbd_destroy_device`, `drbd_device_cleanup`, `drbd_init_set_defaults`, and `drbd_set_my_capacity`. Thread functions include `drbd_thread_start`, `_drbd_thread_stop`, `drbd_thread_setup`, `drbd_thread_init`, and `drbd_thread_current_set_cpu`.

Protocol send APIs include `drbd_header_size`, `conn_prepare_command`, `drbd_prepare_command`, `conn_send_command`, `drbd_send_command`, `drbd_send_ping`, `drbd_send_ping_ack`, `drbd_send_sync_param`, `drbd_send_protocol`, `drbd_send_uuids`, `drbd_send_sizes`, `drbd_send_state`, `drbd_send_state_req`, `drbd_send_sr_reply`, `drbd_send_bitmap`, `drbd_send_ack*`, `drbd_send_drequest*`, `drbd_send_block`, `drbd_send_dblock`, `drbd_send_out_of_sync`, `drbd_send`, and `drbd_send_all`. Transfer-log and retry APIs include `tl_release`, `tl_restart`, `tl_clear`, `tl_abort_disk_io`, `drbd_restart_request`, and the retry worker.

Metadata/bitmap APIs include `drbd_md_write`, `drbd_md_sync`, `drbd_md_read`, `drbd_md_mark_dirty`, `drbd_uuid_move_history`, `drbd_uuid_set`, `drbd_uuid_new_current`, `drbd_uuid_set_bm`, `drbd_bmio_set_n_write`, `drbd_bmio_clear_n_write`, `drbd_queue_bitmap_io`, `drbd_bitmap_io`, `drbd_md_set_flag`, `drbd_md_clear_flag`, and `drbd_md_test_flag`.

## Control Flow
Module initialization validates `minor_count`, registers the DRBD block major, initializes global idr/list/mutex state, registers generic netlink, creates slab/mempool/bio resources, creates `/proc/drbd`, starts the global retry workqueue, initializes debugfs, and logs version/build information. Cleanup removes proc first, stops retry work, unregisters netlink, deletes all devices, frees all resources/connections, tears down debugfs and pools, unregisters the block major, and destroys the global idr.

Resource creation allocates a `drbd_resource`, copies the name, initializes idr/list/locks/options/CPU mask, links it into `drbd_resources`, and creates debugfs entries. Connection creation allocates sockets and current epoch, creates a resource, initializes transfer-log and epoch state, work queue, socket mutexes, connection threads, idr, cstate, wait queue, options, resource references, list linkage, and debugfs. Device creation allocates a `drbd_device`, inherits its resource, initializes defaults, allocates a `gendisk`, metadata page, bitmap, request interval trees, global/resource idr entries, per-connection peer devices, submitter workqueue, and the block disk. Teardown removes idr entries, debugfs, gendisk, peer devices, bitmaps, metadata pages, workqueues, local backing state, and references in a carefully staged order with RCU synchronization.

Thread control starts DRBD receiver, worker, and ack-receiver kthreads with module/resource/connection references. `_drbd_thread_stop` transitions running threads to `EXITING` or `RESTARTING`, signals them with `DRBD_SIGKILL`, and optionally waits for completion. `drbd_thread_setup` runs the thread callback, handles restart loops, publishes `NONE`, completes waiters, and drops references.

Protocol sends follow a common pattern: lock a socket mutex via `conn_prepare_command` or `drbd_prepare_command`, write the payload behind the negotiated header area, call `drbd_send_command`/`conn_send_command`, and unlock. Header format changes by negotiated protocol version: protocol 100 uses volume-aware headers; protocol 95 supports larger payload lengths; older peers use the legacy header. Data sends may use copy-based sending, page-based zero-copy-style sending with `MSG_SPLICE_PAGES`, or plain sends depending on protocol acknowledgements, data integrity, and page suitability. Send timeout handling either pings on the meta socket or requests connection state changes to timeout/broken-pipe.

Transfer-log flow tracks write epochs and barrier acknowledgements. `tl_release` validates the barrier number and expected write count against the oldest pending epoch, then applies `BARRIER_ACKED` to each request in that epoch. Mismatches are protocol errors. `tl_clear` and `tl_restart` apply connection-loss or restart events to all transfer-log requests. The retry worker reinserts postponed bios through `__drbd_make_request` after dropping the queued completion reference and reacquiring application I/O admission.

Bitmap transfer tries RLE/VLI compression first when supported and enabled, falling back to plaintext bitmap words when compression is ineffective. Metadata flow reads and writes a 4 KiB superblock, validates magic, clean activity-log state, bitmap bytes-per-bit, activity-log striping, offsets, metadata capacity, and supported bitmap coverage. Dirty metadata is batched through `MD_DIRTY` and a five-second timer that posts `MD_SYNC` work.

## State And Persistence
Persistent kernel state includes the global device idr/resource list, per-resource idrs and lists, per-connection sockets/threads/crypto/transfer-log/epoch state, and per-device virtual disk, bitmap, local backing device, counters, timers, peer devices, request interval trees, and pending work lists. Module parameters configure device count, helper path, proc detail level, sendpage behavior, unsafe secondary open allowance, and optional fault injection.

On-disk state is the DRBD metadata superblock described by `struct meta_data_on_disk`: last agreed size, UUID set, device UUID, flags, magic, metadata size, activity-log offset/count/stripe geometry, bitmap offset and bytes-per-bit, and last peer max bio size. `drbd_md_sync` writes this state only when `MD_DIRTY` is set and a local disk reference is available. UUID helpers rotate current/bitmap/history UUID slots and update the exposed data UUID. Bitmap I/O can set or clear all bits and then persist the bitmap; `MDF_FULL_SYNC` is used to preserve full-sync intent across failures.

## Dependencies
The file depends heavily on Linux module, block, gendisk, bio, socket, TCP, kthread, workqueue, procfs, debugfs, RCU, idr, crypto, mempool, slab, page, random, timer, waitqueue, and endian APIs. DRBD-specific dependencies include `drbd_int.h`, `drbd_protocol.h`, `drbd_req.h`, `drbd_vli.h`, `drbd_debugfs.h`, bitmap/activity-log functions, receiver/worker callbacks, netlink registration, state-change functions, and protocol constants.

## Integration Points
The block layer calls `drbd_submit_bio`, `drbd_open`, and `drbd_release` through `drbd_ops`. Netlink administration calls resource/connection/device constructors, delete paths, option updates, and metadata helpers. Receiver and worker threads use send helpers, transfer-log functions, socket cleanup, bitmap scheduling, metadata sync, and retry logic. Activity-log and bitmap subsystems call the metadata and bitmap I/O wrappers. Debugfs/proc uses lifecycle hooks and `cmdname`. Crypto configuration integrates through per-connection shash transforms and digest buffers.

## Risks
The highest risks are lifecycle and concurrency ordering. Device creation takes multiple references in global idrs, resource idrs, peer-device lists, gendisk state, and RCU-visible lists; failures and deletion must drop them in exactly the reverse-safe order. Several paths assume `first_peer_device(device)` exists, so partial construction or teardown must avoid helper calls before peer-device setup or after peer-device cleanup. Socket send paths hold per-socket mutexes and may trigger state changes on timeouts; lock ordering with state changes and worker callbacks must remain stable.

Protocol compatibility is sensitive: header selection, max bio size, feature flags, flush/FUA/discard/zeroes mapping, RLE bitmap encoding, and state-change packet selection all depend on negotiated protocol version and features. Data integrity mode intentionally copies payloads to avoid digest races; changing sendpage behavior can reintroduce buffer lifetime hazards. Metadata validation protects against corrupt or incompatible on-disk layouts; relaxing checks can cause out-of-range metadata I/O or mismatches with userspace `drbdmeta`. Bitmap I/O freezes application I/O depending on lock flags, so incorrect flags can corrupt sync state or deadlock progress.

Fault injection changes I/O behavior by design and must stay confined to configured devices and fault classes. `drbd_open` enforces primary/write access and secondary read behavior; the `allow_oos` override is explicitly unsafe. `drbd_wait_misc` drops and reacquires `req_lock` while sleeping, so callers must handle changed state after wakeup.

## Test Signals
Relevant tests include module load/unload, block major registration, create/delete resource/connection/device via netlink, attach/detach with internal/flexible/external metadata, metadata read/write and unclean metadata handling, UUID rotation and full-sync flag persistence, open behavior for primary/secondary/read/write modes, protocol-version matrix tests for headers and packet sizes, bitmap send compression/fallback interoperability, data send with and without integrity and sendpage, timeout/broken-pipe handling, barrier acknowledgement mismatch tests, transfer-log clearing on disconnect, retry of postponed requests, bitmap I/O freeze/unfreeze behavior, debugfs/proc presence, lockdep/sparse coverage, and fault-injection campaigns across metadata/data/resync/bitmap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_main.c -->
