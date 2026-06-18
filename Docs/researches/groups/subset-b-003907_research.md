# subset-b-003907 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/device.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/device.c

## Purpose
This file is the central RDMA/InfiniBand core device registry and lifecycle implementation. It owns allocation, naming, registration, unregister fencing, client callback dispatch, net namespace exposure, compat devices, per-port metadata, netdev association, public query helpers, event dispatch, device-op composition, sub-device management, module initialization, and cleanup for the kernel RDMA core.

## Important APIs, Types, And Functions
Global registries are held in xarrays: `devices` for named `ib_device` objects, `clients` for `ib_client` registrations, and `rdma_nets` for RDMA net namespace state. The file defines marks such as `DEVICE_REGISTERED`, `DEVICE_GID_UPDATES`, `CLIENT_REGISTERED`, and `CLIENT_DATA_REGISTERED` to represent lifecycle state without immediately removing objects from their xarrays.

Important exported device lifecycle APIs are `_ib_alloc_device()`, `ib_dealloc_device()`, `ib_register_device()`, `ib_unregister_device()`, `ib_unregister_device_and_put()`, `ib_unregister_device_queued()`, `ib_unregister_driver()`, `ib_device_get_by_index()`, and `ib_device_put()`. Client-facing APIs include `ib_register_client()`, `ib_unregister_client()`, `ib_set_client_data()`, `ib_get_client_nl_info()`, `ib_register_event_handler()`, `ib_unregister_event_handler()`, and `ib_dispatch_event_clients()`. Port and network APIs include `ib_query_port()`, `ib_device_set_netdev()`, `ib_device_get_netdev()`, `ib_query_netdev_port()`, `ib_device_get_by_netdev()`, `ib_enum_roce_netdev()`, `ib_enum_all_roce_netdevs()`, `ib_device_enable_gid_updates()`, `ib_device_disable_gid_updates()`, `ib_enum_all_devs()`, `ib_query_pkey()`, `ib_modify_device()`, `ib_modify_port()`, `ib_find_gid()`, `ib_find_pkey()`, `ib_get_net_dev_by_params()`, and `ib_dispatch_port_state_event()`.

The main internal helpers are `assign_name()`, `setup_device()`, `enable_device_and_get()`, `disable_device()`, `add_client_context()`, `remove_client_context()`, `setup_port_data()`, `add_compat_devs()`, `remove_compat_devs()`, `rdma_dev_change_netns()`, `free_netdevs()`, and `ib_netdevice_event()`. `ib_set_device_ops()` merges provider operation tables and object-size declarations into the `ib_device_ops` installed on a device.

## Control Flow
Allocation initializes core driver-model state, xarrays, locks, completions, work items, CQ pool lists, cache lock, default uverbs command mask, and net namespace ownership. Registration assigns a unique device name and index, validates mandatory kverbs provider ops, creates per-port immutable state, queries device attributes, sets up cache/sysfs/rdmacg/counters, adds the driver-model device with uevents suppressed, creates port attrs, marks the device registered, invokes optional provider enable, adds every registered client in registration order, creates compat devices for shared netns mode, unsuppresses uevents, and emits RDMA netlink register and netdev attach notifications.

Unregistration is fully fenced by `unregistration_lock`. It removes sub-devices in reverse order, clears the registered mark, removes clients in reverse registration order, cleans CQ pools, waits for the RDMA reference count to drain, removes compat devices, emits unregister notifications, drops netdev hash references, removes sysfs/device-model state, unregisters rdmacg, cleans the cache, and optionally calls provider deallocation. Asynchronous unregister queues the same path on `ib_unreg_wq`.

Client registration assigns monotonically increasing IDs so add callbacks run FIFO and remove callbacks run LIFO. Device registration and client registration are synchronized by write-locking `devices_rwsem` and `clients_rwsem`. Per-device client data is stored in a marked xarray so a client is not visible until its add callback has completed.

Net namespace handling registers pernet operations, creates compat `ib_core_device` objects in additional namespaces when shared mode is enabled, and supports moving exclusive devices between namespaces through a disable-change-enable cycle. Netdev integration hashes `net_device` pointers to `ib_port_data`, sends RDMA netlink attach/detach/rename notifications, and converts netdev carrier/IP state into iWARP `ib_port_attr` state.

Module init creates the common RDMA workqueues, registers the `infiniband` class, initializes RDMA netlink/address/MAD/SA support, installs an LSM policy notifier, registers pernet operations, initializes nldev and link-service netlink callbacks, starts RoCE GID management, and subscribes to netdevice events. Cleanup unwinds those subsystems and verifies device/client registries are empty.

## State And Persistence
All state is runtime kernel memory and driver-model/sysfs/netlink state; nothing is persisted across reboot. Device and client lifetimes are governed by reference counts, kobject references, xarray marks, and completions. Per-port state includes immutable attributes, P_Key security lists, GID cache data, netdev pointers, and netdev hash links. Namespace state is tracked in pernet `rdma_dev_net` plus the local `rdma_nets` xarray. `DEVICE_GID_UPDATES` gates whether netdevice events may drive GID cache updates during registration/teardown.

Synchronization is central to correctness. `devices_rwsem`, `clients_rwsem`, `client_data_rwsem`, `rdma_nets_rwsem`, `unregistration_lock`, `compat_devs_mutex`, `subdev_lock`, per-port `netdev_lock`, and `ndev_hash_lock` each protect a distinct lifecycle or lookup domain. RCU protects netdev hash lookup and delayed freeing of port data and devices.

## Dependencies And Integration Points
This file integrates nearly every RDMA core subsystem: address resolution, MAD, SA, cache, counters, cgroups, security, nldev, RDMA netlink, RoCE GID management, sysfs, net namespaces, netdevice notifications, workqueues, xarrays, driver core, and provider `ib_device_ops`. Upper-layer clients such as uverbs, CM/CMA, MAD agents, SA query, and counters depend on the client callback and client-data contracts. Providers depend on registration/unregistration fencing, netdev association, port immutable setup, op merging, and the exported query/modify helpers.

## Risks And Test Signals
Primary risks are lifecycle races between registration, unregistration, client registration, namespace moves, netdev unregister, and provider module unload. Mark semantics in xarrays are subtle: clearing a mark before removing an object is used as a visibility barrier, and regressions can expose half-registered or half-removed objects. Netdev reference handling must balance `dev_hold()`/`dev_put()` across legacy `get_netdev()` providers and `ib_device_set_netdev()` users. Compat namespace devices must not outlive their owner or expose hardware counters in unintended namespaces. `ib_set_device_ops()` is large and can silently omit new ops if not updated.

Useful tests include provider probe/remove stress with concurrent `ib_register_client()` and `ib_unregister_client()`, async unregister followed by `ib_unregister_driver()`, namespace move attempts in shared and exclusive modes, netdev attach/detach/rename/down/up events, RoCE GID update enable/disable ordering, sysfs/nldev enumeration while devices unregister, LSM policy-change cache refresh, sub-device add/remove, uverbs open contexts during unregister, and lockdep/KASAN/KCSAN coverage of xarray and netdev hash paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.c

## Purpose
This file implements a per-RDMA-device pool manager for FRMR handles. It lets providers cache, pin, reuse, age, and destroy fast-registration memory-region handles keyed by requested FRMR properties, reducing repeated provider allocations while bounding idle resources.

## Important APIs, Types, And Functions
The public entry points are `ib_frmr_pools_init()`, `ib_frmr_pools_cleanup()`, `ib_frmr_pools_set_aging_period()`, `ib_frmr_pools_set_pinned()`, `ib_frmr_pool_pop()`, and `ib_frmr_pool_push()`. Pools are keyed by `struct ib_frmr_key`, stored in an rb-tree under `struct ib_frmr_pools`, and implemented as `struct ib_frmr_pool` objects with active and inactive `struct frmr_queue` lists.

Important helpers are `push_handle_to_queue_locked()`, `pop_handle_from_queue_locked()`, `pop_frmr_handles_page()`, `destroy_all_handles_in_queue()`, `age_pinned_pool()`, `pool_aging_work()`, `destroy_frmr_pool()`, `compare_keys()`, `ib_frmr_pool_find()`, `create_frmr_pool()`, and `get_frmr_from_pool()`. Provider-specific allocation and destruction are abstracted through `struct ib_frmr_pool_ops` in `device->frmr_pools->pool_ops`.

## Control Flow
Initialization allocates `struct ib_frmr_pools`, initializes the rb-tree lock, stores provider operations, creates a single-thread aging workqueue, installs the default 60-second aging period, and attaches the object to `device->frmr_pools`. `ib_frmr_pool_pop()` finds or creates the pool for `mr->frmr.key`, then pulls a handle from the regular queue, the inactive queue, or provider `create_frmrs()` if no cached handle exists. The handle and pool pointer are stored back in `mr->frmr`, and `in_use`/`max_in_use` counters are updated.

`ib_frmr_pool_push()` returns an MR handle to the regular queue and schedules aging when an empty queue becomes non-empty. Aging without pinned handles destroys all handles that were already inactive, then moves the current regular queue to the inactive queue so handles survive one aging interval before destruction. With pinned handles configured, aging computes total live plus cached handles, destroys excess inactive handles first, then moves current regular handles to inactive and reschedules only if more work remains.

`ib_frmr_pools_set_pinned()` validates MR access flags, optionally lets the provider canonicalize the key through `build_key()`, finds or creates the pool, creates enough handles to reach the requested pinned count, pushes them into the regular queue, stores `pinned_handles`, and immediately schedules aging to reconcile excess resources. Cleanup cancels each pool's delayed work, destroys all queued and inactive handles through provider ops, destroys the aging workqueue, and clears `device->frmr_pools`.

## State And Persistence
Pool state is runtime-only and per `ib_device`. The rb-tree persists while `device->frmr_pools` is initialized. Each pool tracks `queue`, `inactive_queue`, `in_use`, `max_in_use`, `pinned_handles`, the canonical key, and its delayed aging work. Handles are batched into page-sized `frmr_handles_page` allocations, with queue `ci` acting as a stack index across the page list. Access to pool queues/counters is protected by `pool->lock`; rb-tree lookup uses `pools->rb_lock`.

## Dependencies And Integration Points
The implementation depends on provider `ib_frmr_pool_ops` for `create_frmrs()`, `destroy_frmrs()`, and optional `build_key()`, and on the generic RDMA MR access validator `ib_check_mr_access()`. It is integrated through `struct ib_device::frmr_pools` and `struct ib_mr::frmr`, so providers and MR users must initialize pools before pop/push and must clean up only after all handles have been returned.

## Risks And Test Signals
Important risks include queue accounting mistakes across page boundaries, failing `push_handle_to_queue_locked()` after provider handles were created, races between concurrent create/find paths, aging work running during cleanup, pinned-handle shrink/expand behavior, and handle leaks if callers fail to push all popped MRs before cleanup. `compare_keys()` intentionally treats a pool with up to less than twice the requested `num_dma_blocks` as equivalent, so tests should confirm this tolerance is intended for every provider.

Useful tests include concurrent pop/push against the same key, concurrent creation of the same pool, distinct keys differing in access flags/vendor keys/ATS/block count, pinned growth and shrink, aging period changes while pools are active, provider allocation failure injection, page-boundary queue push/pop counts, cleanup after all handles return, and warnings or leak checks when cleanup is attempted with handles still in use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.h

## Purpose
This internal header declares the FRMR pool data structures used by `frmr_pools.c` and exposes tuning helpers for pinned handles and aging period. It is the private bridge between the RDMA core pool implementation and the public FRMR pool definitions in `<rdma/frmr_pools.h>`.

## Important APIs, Types, And Functions
`NUM_HANDLES_PER_PAGE` computes the number of 32-bit FRMR handles that fit in one page after a list header. `struct frmr_handles_page` stores one page of handles. `struct frmr_queue` represents a page-list-backed stack and tracks the number of pages plus current index `ci`. `struct ib_frmr_pool` stores the rb-tree node, pool key, spinlock, regular queue, inactive queue, delayed aging work, owning device, `max_in_use`, `in_use`, and `pinned_handles`. `struct ib_frmr_pools` stores the rb-root, rb-tree lock, provider ops, aging workqueue, and aging period.

The declared APIs are `ib_frmr_pools_set_pinned()` and `ib_frmr_pools_set_aging_period()`. The init, cleanup, pop, and push entry points are declared in the public RDMA FRMR pool header rather than here.

## Control Flow
The header has no executable flow, but it defines the object graph: an `ib_device` owns one `ib_frmr_pools`; that object owns many rb-tree-indexed `ib_frmr_pool` instances; each pool owns active and inactive queues; each queue owns one or more `frmr_handles_page` allocations. Delayed work is embedded in each pool so aging can operate per key.

## State And Persistence
All state described here is in-memory and tied to the lifetime of the owning `ib_device`. Queue indexes and page lists must remain consistent under `ib_frmr_pool::lock`; rb-tree membership is protected by `ib_frmr_pools::rb_lock`.

## Dependencies And Integration Points
The header depends on RDMA FRMR public types, rb-tree type definitions, spinlocks, workqueues, page size, and integer types. It is only for RDMA core internals and should stay synchronized with provider expectations for `struct ib_frmr_key`, `struct ib_frmr_pool_ops`, and the `struct ib_mr::frmr` fields used by pop/push.

## Risks And Test Signals
Risks are mainly structural: changing queue fields or handle-page sizing can break accounting in `frmr_pools.c`, and adding fields to `ib_frmr_pool` can affect delayed-work teardown assumptions. Build tests should cover users of both this private header and `<rdma/frmr_pools.h>`. Runtime signals come from the `frmr_pools.c` tests: queue boundary behavior, aging, and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/frmr_pools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ib_core_uverbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/ib_core_uverbs.c

## Purpose
This file implements shared RDMA uverbs helpers for userspace mmap tracking, IO memory mapping, mmap-entry allocation/removal, dma-buf revocation integration, and resolving a live `ib_device` from uverbs request data. It supports hot-unplug/disassociation by tracking VMAs and preventing new mappings after driver removal.

## Important APIs, Types, And Functions
Exported APIs include `rdma_umap_priv_init()`, `rdma_user_mmap_io()`, `rdma_user_mmap_entry_get_pgoff()`, `rdma_user_mmap_entry_get()`, `rdma_user_mmap_entry_put()`, `rdma_user_mmap_entry_remove()`, `rdma_user_mmap_entry_insert_range()`, `rdma_user_mmap_entry_insert()`, and `rdma_udata_to_dev()`. The main state types are `struct rdma_umap_priv`, `struct rdma_user_mmap_entry`, `struct ib_ucontext`, `struct ib_uverbs_file`, and `struct ib_uverbs_dmabuf_file`.

## Control Flow
Drivers insert mmap entries into a ucontext xarray with `rdma_user_mmap_entry_insert_range()` or `rdma_user_mmap_entry_insert()`. The range allocator locks `ufile->umap_lock` and `ucontext->mmap_xa`, finds a contiguous free page-offset range, stores the same entry pointer in every page slot, initializes refcount/dma-buf tracking, and records `start_pgoff` and `npages`.

When userspace calls mmap, uverbs/provider code retrieves the entry by offset with `rdma_user_mmap_entry_get()` or `_get_pgoff()`, checking shared mapping flags, exact range start, entry size, `driver_removed`, and nonzero refcount. `rdma_user_mmap_io()` validates `VM_SHARED`, VMA size, and uverbs file identity, remaps the PFN range with the requested pgprot, allocates `rdma_umap_priv`, and links the VMA to the entry and the file's `umaps` list. `rdma_umap_priv_init()` takes an entry ref and installs VMA private data.

Removal marks the entry `driver_removed` under the mmap xarray lock, walks attached dma-buf mappings, locks each reservation object, removes it from the entry list, marks it revoked, invalidates mappings, waits for bookkeeping fences, drops the dma-buf kref, and waits for completion. It then drops the entry reference. Final free erases every occupied xarray slot and calls provider `ops.mmap_free()` if present.

`rdma_udata_to_dev()` converts an `ib_udata` back to the device serving the uverbs operation. It requires the disassociate SRCU to be held and returns either the already-created context's device or the uverbs file's current device pointer if context creation is still in progress.

## State And Persistence
State is runtime-only per uverbs file and ucontext. `mmap_xa` stores page-offset ownership; `umap_lock` serializes range allocation with the VMA tracking list; each mmap entry has a kref, `driver_removed` gate, dma-buf list, and dma-buf mutex. Active VMAs hold references through `rdma_umap_priv`, so provider `mmap_free()` is delayed until the last VMA and driver reference are gone.

## Dependencies And Integration Points
The file depends on uverbs core types, xarray, Linux VMA/MM helpers, IO PFN remapping, SRCU disassociation, dma-buf reservation and invalidation APIs, and optional provider callbacks `mmap_free()`. Drivers that map BARs or doorbells to userspace use these helpers from their `mmap()` implementations and must return userspace byte offsets derived from `entry->start_pgoff`.

## Risks And Test Signals
Key risks are accepting non-shared mappings, size/offset mismatches, entry use after driver removal, dma-buf revocation races, leaking xarray slots for multi-page entries, and deadlocks around reservation locks or disassociate SRCU. The insert path returns `-ENOMEM` for several allocation/range failures, so callers should not assume all failures are memory pressure.

Useful tests include mmap of correct and incorrect sizes, non-`VM_SHARED` attempts, offset reuse after close, concurrent mmap and entry removal, hot unplug disassociation with live VMAs, dma-buf invalidation and fence wait behavior, range exhaustion in constrained offsets, provider `mmap_free()` timing, and lockdep coverage for `umap_lock`, `mmap_xa`, and disassociate SRCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/ib_core_uverbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iter.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/iter.c

## Purpose
This small file implements exported scatterlist block-iterator primitives for RDMA drivers. The iterator advances over DMA-mapped scatterlist data in fixed-size blocks chosen by the driver, reporting block DMA addresses that may span scatterlist entries.

## Important APIs, Types, And Functions
The exported APIs are `__rdma_block_iter_start()` and `__rdma_block_iter_next()`, operating on `struct ib_block_iter` from `<rdma/iter.h>`. The iterator tracks the current scatterlist pointer, remaining SG entries, current SG byte advance, current block DMA address, and page/block-size bit.

## Control Flow
`__rdma_block_iter_start()` zeroes the iterator, stores the scatterlist and entry count, and derives the block-size bit with `__fls(pgsz)`. `__rdma_block_iter_next()` stops when no SG entries remain, sets the current DMA address to `sg_dma_address()` plus per-entry advance, computes the remaining bytes to the next block boundary, consumes whole SG fragments until the block delta is satisfied, advances into the final SG entry by the remaining delta, and returns true for the produced block.

## State And Persistence
The iterator is caller-owned transient state. There is no persistent storage or locking; callers must provide a stable DMA-mapped scatterlist and valid block size for the duration of iteration.

## Dependencies And Integration Points
The implementation depends on Linux scatterlist DMA accessors and RDMA iterator definitions. It is intended for drivers that need to walk DMA segments by hardware page/block boundaries during MR registration, memory-key programming, or similar DMA-block setup.

## Risks And Test Signals
Risks include invalid or non-power-of-two `pgsz`, zero `pgsz` causing invalid `__fls()`, scatterlist entries with zero DMA length, arithmetic edge cases when a block exactly ends on an SG boundary, and callers using an unmapped or mutated scatterlist. Tests should cover single SG entries, multiple SG entries, exact block-boundary transitions, unaligned starting DMA addresses, zero-length/empty inputs, large block sizes, and comparison against expected DMA address sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.c

## Purpose
This file implements the kernel iWARP Connection Manager. It provides `iw_cm_id` creation/destruction, active connects, passive listens, accept/reject/disconnect operations, provider event handling, QP state helpers, sysctl tuning for listen backlog, and RDMA netlink registration for iWARP port mapper messages.

## Important APIs, Types, And Functions
Exported APIs include `iwcm_reject_msg()`, `iw_create_cm_id()`, `iw_cm_disconnect()`, `iw_destroy_cm_id()`, `iw_cm_listen()`, `iw_cm_reject()`, `iw_cm_accept()`, `iw_cm_connect()`, and `iw_cm_init_qp_attr()`. Internal state is `struct iwcm_id_private`, wrapping public `struct iw_cm_id` with state, flags, QP pointer, completion/waitqueue, spinlock, refcount, and preallocated work list.

Important helpers include `alloc_work_entries()`, `get_work()`, `put_work()`, `copy_private_data()`, `destroy_cm_id()`, `iw_cm_map()`, `iw_cm_check_wildcard()`, `cm_event_handler()`, `cm_work_handler()`, `process_event()`, `cm_conn_req_handler()`, `cm_conn_rep_handler()`, `cm_conn_est_handler()`, `cm_disconnect_handler()`, and `cm_close_handler()`. Provider operations used include `iw_create_listen`, `iw_destroy_listen`, `iw_connect`, `iw_accept`, `iw_reject`, `iw_get_qp`, `iw_add_ref`, and `iw_rem_ref`.

## Control Flow
`iw_create_cm_id()` allocates an ID in `IDLE` state, installs provider-upcall and reference callbacks, initializes locks/wait queues, and returns the public object. Listening allocates backlog-sized work items, transitions from `IDLE` to `LISTEN`, asks IWPM to map the local address, and calls provider `iw_create_listen()`. Active connect preallocates four work items, sets `CONNECT_WAIT`, gets and references the QP, transitions to `CONN_SENT`, maps addresses through IWPM, and calls provider `iw_connect()`.

Provider upcalls enter `cm_event_handler()` in interrupt context. The handler pulls a preallocated work item, copies connect private data when needed, takes an ID reference, and queues ordered work. The workqueue dispatches events: connect requests create child IDs in `CONN_RECV`; active replies either move `CONN_SENT` to `ESTABLISHED` or back to `IDLE`; passive established moves `CONN_RECV` to `ESTABLISHED`; disconnect moves established IDs to `CLOSING`; close drops the QP reference and returns to `IDLE` or finishes destruction.

Accept validates `CONN_RECV`, gets the QP from the provider, references it, stores it, and calls provider `iw_accept()`. Reject validates `CONN_RECV`, moves to `IDLE`, and calls provider `iw_reject()`. Disconnect waits for pending connect/accept downcalls, moves established IDs to `CLOSING`, and modifies the QP to ERR for abrupt close or SQD for graceful close. Destroy sets `DROP_EVENTS`, waits for connect/accept to finish, tears down listens or live connections, rejects pending passive requests, drops QP references, and removes IWPM mappings.

Module init initializes IWPM, creates an ordered workqueue, registers `net/iw_cm/default_backlog`, and registers IWPM RDMA netlink callbacks. Cleanup unregisters netlink/sysctl/workqueue/IWPM in reverse order.

## State And Persistence
Connection state is runtime-only in `iwcm_id_private::state`: `IDLE`, `LISTEN`, `CONN_RECV`, `CONN_SENT`, `ESTABLISHED`, `CLOSING`, and `DESTROYING`. Flags `IWCM_F_DROP_EVENTS` and `IWCM_F_CONNECT_WAIT` coordinate destruction and blocking disconnect/destroy while provider downcalls are in progress. Work items are preallocated per ID to avoid allocation from provider interrupt-context upcalls. Mapped local/remote addresses persist in the public ID until destroy removes associated IWPM mapinfo and mapping.

## Dependencies And Integration Points
The file depends on RDMA provider iWARP ops, the RDMA QP modify path, IWPM port mapping, RDMA netlink, sysctl, ordered workqueues, wait queues, and public `<rdma/iw_cm.h>`. Upper layers use public `iw_cm_id` callbacks and receive connection events with original or unmapped socket addresses after IWPM translation.

## Risks And Test Signals
The most important risks are state-machine races among provider upcalls, application accept/reject/disconnect/destroy, and queued work. The design relies on preallocated work item counts, so backlog sizing and event count assumptions are critical. Some invalid state paths use `BUG()`, making provider contract violations fatal. Private data is copied only for connect request/reply events, and must be freed exactly once. IWPM failures are intentionally nonfatal in some paths, so fallback address behavior needs coverage.

Useful tests include active connect success, connect reject/reset/timeout, passive listen accept/reject, destroy during pending connect and pending accept, disconnect before accept, simultaneous disconnect, provider close after destroy, backlog exhaustion, private-data delivery/freeing, QP reference balancing, wildcard address mapping, IWPM unavailable/downlevel daemon behavior, sysctl backlog changes, and lockdep/KCSAN stress of state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.h

## Purpose
This private header defines the iWARP CM internal state machine and private wrapper around the public `iw_cm_id`. It is consumed by `iwcm.c` to track connection lifecycle, queued work capacity, QP association, and destruction/connect synchronization.

## Important APIs, Types, And Functions
`enum iw_cm_state` defines the allowed internal states: `IW_CM_STATE_IDLE`, `LISTEN`, `CONN_RECV`, `CONN_SENT`, `ESTABLISHED`, `CLOSING`, and `DESTROYING`. `struct iwcm_id_private` embeds `struct iw_cm_id`, state, flags, associated QP pointer, destroy completion, connect waitqueue, spinlock, refcount, and a free list of preallocated work items. Flags are `IWCM_F_DROP_EVENTS` and `IWCM_F_CONNECT_WAIT`.

## Control Flow
The header itself has no runtime flow, but its state names document the transitions implemented in `iwcm.c`: IDLE to LISTEN or CONN_SENT, LISTEN to child CONN_RECV on inbound requests, CONN_RECV or CONN_SENT to ESTABLISHED on provider success, ESTABLISHED to CLOSING on disconnect, and terminal cleanup through DESTROYING.

## State And Persistence
All fields are runtime-only per iWARP connection ID. The spinlock protects state/QP transitions, the waitqueue coordinates connect/accept downcalls with disconnect/destroy, the refcount keeps queued events alive, and the work free list guarantees provider upcalls can enqueue work without allocating.

## Dependencies And Integration Points
The header depends on public RDMA CM/QP types, completions, wait queues, spinlocks, refcounts, and list heads through included kernel/RDMA headers. It is tightly coupled to `iwcm.c`; external code should use the public `iw_cm_id` API rather than these internals.

## Risks And Test Signals
State additions or flag changes require synchronized updates to every switch in `iwcm.c`, including paths that currently call `BUG()`. Tests are indirect through iWARP CM operations: active/passive connect, reject, disconnect, destroy, event dropping, and queued-work reference handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_msg.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_msg.c

## Purpose
This file implements the iWARP Port Mapper netlink protocol message layer. It sends kernel requests to the userspace `iwpmd` port mapper, processes responses and notifications, negotiates ABI version, tracks the userspace daemon PID, and bridges synchronous CM mapping calls to asynchronous RDMA netlink callbacks.

## Important APIs, Types, And Functions
Public/request APIs include `iwpm_valid_pid()`, `iwpm_register_pid()`, `iwpm_add_mapping()`, `iwpm_add_and_query_mapping()`, and `iwpm_remove_mapping()`. Callback APIs registered by `iwcm.c` include `iwpm_register_pid_cb()`, `iwpm_add_mapping_cb()`, `iwpm_add_and_query_mapping_cb()`, `iwpm_remote_info_cb()`, `iwpm_mapping_info_cb()`, `iwpm_ack_mapping_info_cb()`, `iwpm_mapping_error_cb()`, and `iwpm_hello_cb()`.

Important global state is `iwpm_user_pid`, `iwpm_ulib_version`, `iwpm_ulib_name`, and `echo_nlmsg_seq`. Netlink attribute policies validate register-pid responses, add/query mapping responses, mapinfo requests/acks, error messages, and hello requests.

## Control Flow
Registration sends a multicast `RDMA_NL_IWPM_REG_PID` request containing a kernel sequence, interface name, IB device name, and user-library name. A matching callback verifies device/library name and minimum ABI, records the sender PID and ABI version, marks the netlink client valid, completes the waiting request, and saves the daemon echo sequence.

Add mapping and add-and-query mapping first require a valid registered daemon. They allocate an `iwpm_nlmsg_request`, build a netlink message with local and optionally remote socket addresses plus flags for newer ABI versions, unicast it to `iwpm_user_pid`, and block in `iwpm_wait_complete_req()`. Their callbacks parse the response, validate requested addresses and address families, copy mapped local/remote addresses into the caller's `iwpm_sa_data`, set any protocol error code, and wake the waiter.

Remove mapping sends a best-effort unicast removal message and resets `iwpm_user_pid` to undefined if sending fails. Remote-info notifications are unsolicited messages carrying original and mapped peer addresses; they are validated and stored in the remote-info hash table for passive CM request processing. Mapping-info notifications indicate that a daemon started or restarted; the kernel records incomplete registration, stores the daemon PID, and sends all existing mapinfo records. Hello negotiates the ABI version by taking the min of kernel and daemon versions and replies with `iwpm_send_hello()`.

## State And Persistence
State is runtime-only and global to the IWPM client. `iwpm_user_pid` may be undefined, unavailable, or a positive daemon PID. `iwpm_ulib_version` gates whether optional flags are sent. `echo_nlmsg_seq` follows daemon sequence echoing and is included in outgoing requests. In-flight request state and mapinfo/reminfo tables live in `iwpm_util.c`.

## Dependencies And Integration Points
The file depends on `iwpm_util.h`, RDMA netlink send helpers, netlink attribute parsing, IWPM UAPI constants from `<rdma/iw_portmap.h>`, and CM callers in `iwcm.c`. It integrates synchronous kernel calls with userspace daemon responses through `iwpm_nlmsg_request::sem` and callback completion.

## Risks And Test Signals
Risks include daemon restart races, stale or invalid `iwpm_user_pid`, downlevel ABI behavior when flags are required, request timeout handling, mismatched netlink sequences, accepting malformed sockaddr families, leaking requests when sends fail, and global ABI/PID state shared across clients. Some failure modes intentionally degrade to no port mapping rather than failing connection setup, so tests must distinguish quiet fallback from true errors.

Useful tests include no daemon present, daemon registration success and invalid library/device/version responses, ABI v3/v4 flag behavior, add/query/remove mapping success and timeout, remote query reject, malformed address family responses, unsolicited remote-info storage and retrieval, daemon restart mapinfo replay, mapping error messages with and without matching requests, hello negotiation, and concurrent mapping requests with sequence matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.c

## Purpose
This file provides the utility and state-management layer for the iWARP Port Mapper. It manages in-flight netlink requests, local mapping-info and remote-info hash tables, registration state, sockaddr comparison/hashing, netlink message allocation/parsing, mapinfo replay, and hello responses.

## Important APIs, Types, And Functions
Lifecycle APIs are `iwpm_init()` and `iwpm_exit()`. Mapping table APIs are `iwpm_create_mapinfo()`, `iwpm_remove_mapinfo()`, `iwpm_add_remote_info()`, `iwpm_get_remote_info()`, `iwpm_send_mapinfo()`, and `iwpm_mapinfo_available()`. Request APIs are `iwpm_get_nlmsg_request()`, `iwpm_free_nlmsg_request()`, `iwpm_find_nlmsg_request()`, `iwpm_wait_complete_req()`, and `iwpm_get_nlmsg_seq()`. Registration helpers are `iwpm_get_registration()`, `iwpm_set_registration()`, and `iwpm_check_registration()`. Netlink/socket helpers are `iwpm_compare_sockaddr()`, `iwpm_create_nlmsg()`, `iwpm_parse_nlmsg()`, `iwpm_print_sockaddr()`, and `iwpm_send_hello()`.

Global state includes `iwpm_nlmsg_req_list`, `iwpm_hash_bucket`, `iwpm_reminfo_bucket`, and `iwpm_admin`. Hash sizes are 512 buckets for local mapinfo and 64 buckets for remote info.

## Control Flow
Initialization allocates both hash tables and marks the RDMA netlink client registration undefined. Exit frees all mapinfo and remote-info entries, frees the bucket arrays, and resets registration. `iwpm_create_mapinfo()` allocates a record for original and mapped local sockaddr plus flags, hashes the address pair, and inserts under `iwpm_mapinfo_lock`. Removal hashes the same pair, finds a matching mapped address, deletes it, and frees the record.

Remote info is keyed by mapped local and mapped remote sockaddr. `iwpm_add_remote_info()` inserts records supplied by IWPM callbacks, and `iwpm_get_remote_info()` retrieves and removes the matching record, copying the original remote address back to the CM caller.

Netlink request flow allocates `iwpm_nlmsg_request`, links it into the in-process list, initializes a kref and semaphore, and pre-acquires the semaphore. Callback code finds a request by sequence, takes a kref, sets `err_code`/`request_done`, drops the callback reference, and ups the semaphore. The sender waits with a 10-second timeout, returns the callback error code on success, and drops its reference.

`iwpm_send_mapinfo()` replays all local mapinfo records for a client to a daemon. It batches records into multipart netlink messages, sends `NLMSG_DONE` for each skb, caps the number of skbs, and finally sends a mapinfo count message. `iwpm_parse_nlmsg()` validates attributes against a policy, parses them, and rejects missing required attributes.

## State And Persistence
All IWPM utility state is runtime-only. The request list is protected by `iwpm_nlmsg_req_lock`; mapinfo by `iwpm_mapinfo_lock`; remote info by `iwpm_reminfo_lock`. `iwpm_admin.nlmsg_seq` is an atomic sequence generator and `reg_list[]` stores per-RDMA-netlink-client registration bits. Mapinfo persists while connections/listeners are mapped so it can be replayed to a restarted daemon.

## Dependencies And Integration Points
The file depends on RDMA netlink helpers, IWPM UAPI definitions, Linux jhash, socket address structures, skbuff allocation, semaphores, krefs, and spinlocks. `iwpm_msg.c` uses these helpers to send synchronous requests and process callbacks, while `iwcm.c` uses mapinfo/reminfo to translate active and passive iWARP connection addresses.

## Risks And Test Signals
Important risks include freeing hash buckets while callbacks are still adding records, request kref/list races, timeout paths freeing requests before late callbacks arrive, send-mapinfo batching while the mapinfo lock is dropped between skbs, duplicate mapinfo records, and hashes that collide but require exact sockaddr comparison. `iwpm_add_remote_info()` drops a record silently if the bucket table is unavailable or address family is invalid.

Useful tests include init/exit with outstanding or empty tables, duplicate add/remove mapinfo, IPv4 and IPv6 hashing/comparison, invalid sockaddr family handling, request timeout and late callback handling, concurrent request lookup/free, mapinfo replay with more records than one skb, skb allocation failure, daemon mapinfo ack count mismatch, remote-info one-shot retrieval, and registration bit transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.h

## Purpose
This private header defines the internal IWPM utility contract shared between the IWPM message layer and the iWARP CM. It centralizes constants, request/mapping/remote-info data structures, registration state representation, and function prototypes for netlink and address mapping helpers.

## Important APIs, Types, And Functions
Constants include netlink retry/timeout limits, mapinfo batching count, daemon PID sentinel values, and registration flags `IWPM_REG_UNDEF`, `IWPM_REG_VALID`, and `IWPM_REG_INCOMPL`. `struct iwpm_nlmsg_request` represents one in-flight synchronous netlink request with list linkage, sequence, caller buffer, client ID, completion flag, error code, semaphore, and kref. `struct iwpm_mapping_info` stores original and mapped local addresses with client ID and map flags. `struct iwpm_remote_info` stores mapped local/remote addresses and the original remote address. `struct iwpm_admin_data` stores the global netlink sequence and per-client registration bits.

The header declares all utility functions implemented in `iwpm_util.c`, message callback support used in `iwpm_msg.c`, and external `iwpm_ulib_version`. It also provides inline `iwpm_validate_nlmsg_attr()` to reject missing required attributes.

## Control Flow
No executable flow beyond the inline validator is defined here. The types describe the protocol flow: request allocation and lookup by sequence, mapinfo persistence for replay, remote-info one-shot storage for passive accepts, and registration state checks before netlink requests are sent.

## State And Persistence
The structures are runtime-only kernel state. Request objects are transient and kref-managed; mapping and remote-info objects persist in hash tables until removed or consumed; registration state persists until IWPM exit or daemon state changes.

## Dependencies And Integration Points
The header depends on Linux networking, netlink, spinlock, workqueue, mutex, delay, jhash, kref, and RDMA IWPM/netlink UAPI headers. It is included by both `iwpm_msg.c` and `iwpm_util.c`, and its function declarations are consumed indirectly by `iwcm.c` through public IWPM prototypes.

## Risks And Test Signals
Risks are ABI and contract drift: netlink timeout constants, registration bits, request fields, or sockaddr record layouts must remain aligned with both the message parser and userspace daemon expectations. The inline validator assumes attributes 1 through `nla_count - 1` are mandatory. Tests should compile all IWPM users and exercise every callback policy path, missing-attribute rejection, request lifetime, and mapinfo/reminfo storage path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/iwpm_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/lag.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/core/lag.c

## Purpose
This file implements RDMA LAG helper logic for selecting the correct transmit slave for RoCEv2 address handles over bonded netdevices. It synthesizes a minimal Ethernet/IP/UDP packet from an RDMA address handle so the networking stack's bond hashing logic can choose the same egress slave that real traffic should use.

## Important APIs, Types, And Functions
The public APIs are `rdma_lag_get_ah_roce_slave()` and `rdma_lag_put_ah_roce_slave()`. Internal helpers are `rdma_build_skb()` and `rdma_get_xmit_slave_udp()`. Inputs are `struct ib_device`, `struct rdma_ah_attr`, GRH/GID attributes, RoCE destination MAC, and the source GID's netdevice.

## Control Flow
`rdma_lag_get_ah_roce_slave()` first filters to RoCE AH attributes using UDP encapsulation and a nonzero GRH flow label. It reads the source GID netdevice under RCU, holds it, and returns NULL if the netdevice is not a bond master. For bond masters, `rdma_get_xmit_slave_udp()` builds a temporary skb containing Ethernet, IPv4 or IPv6, and UDP headers. UDP source port is derived from the RDMA flow label, destination port is the RoCEv2 UDP port, source/destination IP come from SGID/DGID, and source/destination MAC come from GID L2 fields and AH attributes. The helper passes that skb to `netdev_get_xmit_slave()`, takes a reference on the selected slave, frees the skb, drops the master reference, and returns the slave. Callers release it with `rdma_lag_put_ah_roce_slave()`.

## State And Persistence
No persistent state is owned by this file. It takes temporary references on the master and selected slave netdevices and allocates a temporary skb for hashing. The device's `lag_flags` influence whether bond hashing may use all slaves through `RDMA_LAG_FLAGS_HASH_ALL_SLAVES`.

## Dependencies And Integration Points
The file depends on RDMA address handle/GID cache helpers, RoCEv2 UDP encapsulation constants, Linux skbuff/header helpers, RCU, and bonding/LAG netdevice APIs. It is used by RDMA drivers or core paths that need a concrete egress slave for AH operations in bonded RoCE configurations.

## Risks And Test Signals
Risks include malformed synthetic headers causing different bond slave selection than real packets, missing flow labels returning NULL and bypassing LAG selection, incorrect IPv4-mapped IPv6 detection, GID netdevice lifetime races, `netdev_get_xmit_slave()` returning NULL or an error-like value that callers must handle, and source MAC extraction mismatches for VLAN/bond configurations.

Useful tests include RoCEv2 IPv4-mapped and IPv6 AHs over bond masters, non-bond netdevices, zero flow-label AHs, non-RoCE or non-UDP GIDs, hash-all-slaves flag behavior, skb allocation failure, source/destination MAC validation, repeated get/put reference balance, and comparison of selected slave against real UDP flow hashing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/core/lag.c -->
