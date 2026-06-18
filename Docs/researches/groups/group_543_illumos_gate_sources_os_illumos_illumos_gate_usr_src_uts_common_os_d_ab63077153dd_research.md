# Group Research: group_543_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_d_ab63077153dd

Scope verified against `Docs/research_subset_a.md`. The subset includes `sources/os/illumos/illumos-gate`, and all ten requested `usr/src/uts/common/os` source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_impl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_impl.c

## Role

`ddi_hp_impl.c` is the core DDI hotplug framework implementation for illumos. It provides the kernel-side logic behind coordinated hotplug requests from userland `modctl` paths and nexus-driver hotplug callbacks. The file defines the shared state-machine behavior for physical connectors and virtual ports, including state transitions, probing/unprobing, child online/offline, handle lookup, deregistration, and sysevent emission.

The large introductory block documents the Solaris Hotplug Framework architecture, terminology, and connector/port state machine. It places this file between user tools such as `cfgadm(8)`/`hotplug(8)`, `hotplugd`, `modctl`, DDI/NDI hotplug interfaces, nexus `bus_hp_op` implementations, PCIe hotplug support, and I/O subsystem notifications.

## Main Entry Points

- `ddihp_modctl()` implements hotplug `modctl()` operations by resolving the nexus path to a `dev_info_t`, checking `NEXUS_HAS_HP_OP()`, locking the parent before the child to preserve devinfo locking order, resolving connection handles by name, dispatching either direct `bus_hp_op` create-port operations or `DDIHP_CN_OPS()` calls, and translating DDI status codes to errno values.
- `ddihp_cn_getstate()` asks the nexus for current connection state and updates the handle state and last-change timestamp when it changes.
- `ddihp_cn_unregister()` refreshes state, refuses to remove busy connections above offline state, unlinks the handle from `DEVI(dip)->devi_hp_hdlp`, and frees the name and handle.
- `ddihp_cn_name_to_handle()` linearly searches a nexus device's hotplug handle list by connection name.
- `ddihp_connector_ops()` wraps connector operations, adding pre-change cleanup before downgrade, nexus `bus_hp_op` dispatch, and post-change state handling after change-state operations.
- `ddihp_port_ops()` implements virtual-port get-state, change-state, and remove-port operations.
- `ddihp_cn_gen_sysevent()` emits dynamic reconfiguration sysevents with DR AP IDs and either state-change hints or request types.

## Connector State Handling

Connector downgrade from `DDI_HP_CN_STATE_ENABLED` first calls `ddihp_cn_change_children_state(..., B_FALSE)` to offline dependent virtual-port children, runs `devfs_clean()` to avoid devfs references blocking detach, and calls nexus `DDI_HPOP_CN_UNPROBE` to remove children and ports.

Connector upgrade to enabled updates cached state, records the timestamp, calls `DDI_HPOP_CN_PROBE`, and then attempts to online all dependent child devices. If probe fails, it requests a fallback state of `DDI_HP_CN_STATE_POWERED` so userland can retry enabling later. State changes generate DR sysevents through `ddihp_cn_gen_sysevent()`.

`ddihp_cn_change_children_state()` walks all hotplug handles on the nexus, selects virtual ports that depend on the connector's connection number, and online/offline their `cn_child` devinfo nodes. Online failures are logged but do not stop attempts for sibling children; offline failures stop with `DDI_EBUSY`.

## Port State Handling

Virtual ports use a reduced state range from `PORT_EMPTY` through `ONLINE`. `DDI_HPOP_CN_GET_STATE` derives state from `cn_child` and the child devinfo node state:
- no child means empty or present;
- pre-attached node states map to offline;
- `DS_ATTACHED` maps to maintenance;
- `DS_READY` maps to online, unless `ddi_get_devstate()` reports a non-up device.

`ddihp_port_upgrade_state()` advances one state at a time: empty to present through connector change-state, present to offline via read-only probe and `cn_child` capture, and offline/maintenance to online through `ndi_devi_online()`.

`ddihp_port_downgrade_state()` reverses the flow: online/maintenance is offlined with `devfs_clean()` plus `ndi_devi_offline()`, offline is unprobed back to present through connector change-state, and present can return to empty.

## Locking and Error Behavior

All handle list operations assert the nexus devinfo busy lock. Paths that may later lock child and parent devinfo nodes explicitly enter the parent before the child to match the `devcfg.c` lock-ordering theory statement. `ddihp_modctl()` holds and releases the devinfo node obtained by path.

The code distinguishes DDI-level return codes from errno-level userland results. It logs operational failures with `cmn_err()` where device cleanup, probe, attach, detach, sysevent allocation, or sysevent logging fail.

## Subset Relevance

This file is part of the OS device-tree substrate that filesystem and storage stacks rely on during live insertion/removal of controllers, buses, and devices. It is not filesystem code itself, but it controls whether device nodes can be probed, attached, detached, and represented to userland during storage hotplug.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_impl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_ndi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_ndi.c

## Role

`ddi_hp_ndi.c` provides the NDI-facing hotplug interfaces used by nexus drivers and hotplug controllers. It is the companion to `ddi_hp_impl.c`: this file exposes registration, unregistration, state-change request, and connection-walk entry points, while `ddi_hp_impl.c` performs connector and port state-machine work.

## Main Entry Points

- `ndi_hp_register()` validates non-interrupt context, arguments, and nexus hotplug support, creates a `ddi_hp_cn_handle_t`, copies connection metadata, duplicates `cn_name`, initializes cached state through `ddihp_cn_getstate()`, and appends the handle to `DEVI(dip)->devi_hp_hdlp`.
- `ndi_hp_unregister()` validates context and arguments, finds the named handle, calls `ddihp_cn_unregister()`, and maps DDI return values to NDI return values.
- `ndi_hp_state_change_req()` lets a nexus/controller request a connection state transition either synchronously or asynchronously.
- `ndi_hp_walk_cn()` walks all registered connection handles for a devinfo node and invokes a caller-supplied callback with each `ddi_hp_cn_info_t`.

## Synchronous and Asynchronous Requests

For synchronous requests, `ndi_hp_state_change_req()` rejects interrupt context, locks the parent before the target devinfo node, finds the handle, and calls `ddihp_cn_req_handler()` directly. The handler deliberately does not refresh state before changing it because connector operations depend on the last known cached state to decide whether cleanup, sysevents, or probing are required.

For asynchronous requests, the function allocates a `ddi_hp_cn_async_event_entry_t` with `KM_NOSLEEP`, duplicates the connection name, holds the devinfo node, and dispatches `ddihp_cn_run_event()` to `system_taskq`. If dispatch fails, it releases the devinfo hold. The worker repeats the same parent-before-child locking discipline, finds the handle, performs the request if the handle still exists, releases the devinfo hold, and frees the event record.

## Walking Semantics

`ndi_hp_walk_cn()` holds the devinfo busy lock while walking `DEVI(dip)->devi_hp_hdlp`. It is resilient to callbacks that remove the current handle: it tracks the original head and previous node and restarts or advances appropriately when the list head or current link changes.

## Locking and Error Behavior

All public entry points reject or avoid interrupt context where needed because devinfo locking, allocation, and state transitions can block. Registration/unregistration uses `ndi_devi_enter()` on the nexus. State-change request paths use the same parent-before-child lock ordering documented in `ddi_hp_impl.c` to avoid deadlocks during nested devinfo operations.

The async path uses `KM_NOSLEEP` and taskq dispatch because it can be triggered from interrupt-adjacent hotplug notification paths. It returns `NDI_CLAIMED` once dispatched, not once the state change completes.

## Subset Relevance

This file is infrastructure for dynamic device discovery and removal. Storage and filesystem code depend on this layer indirectly when hotplug-capable buses add or remove disks, controllers, or ports.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_hp_ndi.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr.c

## Role

`ddi_intr.c` implements the public DDI interrupt framework and legacy interrupt compatibility APIs. It covers hardware interrupt discovery, allocation/free, capabilities, priority, handler registration, MSI-X handler duplication, enable/disable, MSI block enable/disable, masking, pending-status queries, IRM request resizing, soft interrupts, and older `ddi_add_intr()`/`ddi_remove_intr()` style interfaces.

The file is the primary consumer-facing interrupt API layer. Platform and nexus-specific work is delegated through `i_ddi_intr_ops()` and internal helpers implemented elsewhere.

## Interrupt Discovery and Allocation

`ddi_intr_get_supported_types()`, `ddi_intr_get_nintrs()`, and `ddi_intr_get_navail()` validate inputs, consult cached devinfo interrupt metadata when present, and otherwise issue nexus interrupt operations for supported types, count, or availability.

`ddi_intr_alloc()` performs the central allocation workflow:
- validates handles, type, count, interrupt number, and allocation behavior;
- prevents fixed-interrupt duplicate allocation for the same `inum`;
- obtains supported interrupt count and current interrupt type/count;
- enforces one interrupt type per device at a time;
- enforces device-supported limits and MSI power-of-two count rules;
- initializes per-device interrupt state and inserts the device into IRM on first allocation;
- adjusts IRM reservations for non-IRM-aware drivers on later allocations;
- applies strict versus normal allocation behavior when requested count exceeds available count;
- delegates allocation, priority lookup, and capability lookup to `i_ddi_intr_ops()`;
- records current type, supported count, and current allocated count;
- allocates one `ddi_intr_handle_impl_t` per actual interrupt, initializes its rwlock and fields, allocates a private handle, and stores fixed interrupt handles for legacy lookup.

On allocation failure after nexus allocation, the fail path frees the nexus allocation and finalizes per-device interrupt state.

## Free, Capabilities, and Priority

`ddi_intr_free()` requires an allocated handle, except duplicated MSI-X handles are freed from `ADDED` state. It delegates `DDI_INTROP_FREE`, updates duplicate counts or current interrupt counts, adjusts IRM for non-aware drivers, clears fixed-interrupt handle slots, finalizes devinfo interrupt state, frees private handles, destroys the rwlock, and releases the handle memory.

`ddi_intr_get_cap()` returns cached capabilities or asks the nexus, hiding `DDI_INTR_FLAG_MSI64` from consumers. `ddi_intr_set_cap()` only allows level/edge capability changes while the handle is allocated and supported.

`ddi_intr_get_hilevel_pri()` returns `LOCK_LEVEL + 1`. `ddi_intr_get_pri()` returns cached priority or queries the nexus. `ddi_intr_set_pri()` validates range, requires allocated state, avoids no-op changes, calls the nexus, and caches the new priority.

## Handler and Enable Lifecycle

`ddi_intr_add_handler()` requires an allocated handle and non-null callback, stores callback fields, delegates `DDI_INTROP_ADDISR`, and transitions to `ADDED`. On failure it clears callback state.

`ddi_intr_dup_handler()` supports MSI-X duplicate vectors only. It verifies the original handle is not merely allocated, is MSI-X, and is not itself a duplicate, asks the nexus to duplicate the vector, allocates a new handle, copies the original, reinitializes the duplicate's lock and unique fields, marks it `DDI_INTR_MSIX_DUP`, and points back to the original.

`ddi_intr_remove_handler()` requires `ADDED` state. Duplicates skip nexus ISR removal because the original owns the ISR. Originals must have zero duplicate count before `DDI_INTROP_REMISR`; successful removal clears callback fields and returns to allocated state.

`ddi_intr_enable()` and `ddi_intr_disable()` require added/enabled states respectively, reject per-vector enable/disable for block-capable MSI handles, verify MSI-X handle correctness, issue nexus operations, and maintain per-device enabled counts.

`ddi_intr_block_enable()` and `ddi_intr_block_disable()` validate every handle in the array for MSI block capability and consistent state, then issue one block operation via the first handle and update all handle states. The enabled count is treated as one block enable for the device.

## Masking, Pending, IRM, and Soft Interrupts

`ddi_intr_set_mask()`, `ddi_intr_clr_mask()`, and `ddi_intr_get_pending()` require the relevant capability bits and delegate to nexus operations.

`ddi_intr_set_nreq()` lets IRM-aware drivers change the number of requested interrupts. It requires an active interrupt type, IRM support for that type, and a request not exceeding supported interrupt count, then calls `i_ddi_irm_modify()`.

Soft interrupt APIs allocate `ddi_softint_hdl_impl_t` records, validate soft priority ranges, delegate platform add/remove/trigger/set-priority operations, and expose get/set/trigger wrappers. Legacy soft interrupt APIs translate older priority preferences into modern soft interrupt handles.

## Legacy Compatibility

The obsolete API section adapts old fixed-interrupt interfaces to the new framework:
- `ddi_intr_hilevel()` allocates or reuses a fixed interrupt handle and compares priority to high-level threshold.
- `ddi_dev_nintrs()` returns fixed interrupt count.
- `ddi_get_iblock_cookie()` returns priority as an iblock cookie.
- `ddi_add_intr()` allocates one fixed interrupt, retrieves priority, adds a handler, enables it, fills legacy cookies, and frees the temporary handle array.
- `ddi_remove_intr()` finds a fixed interrupt handle, disables it, removes the handler, and frees it.
- `ddi_add_fastintr()` is unsupported.
- old soft interrupt functions allocate/remove/trigger modern soft interrupt handles behind legacy opaque IDs.

## Subset Relevance

Interrupt allocation and teardown are fundamental to storage controllers, block devices, and filesystem-adjacent device drivers. This file defines the driver-facing contract for interrupt resources and directly interacts with IRM, making it part of the OS/storage substrate covered by subset A.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_impl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_impl.c

## Role

`ddi_intr_impl.c` contains internal helper routines for the DDI interrupt framework. It manages per-devinfo interrupt metadata, cached supported/current interrupt information, interrupt availability limits, MSI-X bookkeeping, fixed interrupt handle tables, interrupt weight properties, obsolete busops stubs, interrupt affinity, and x86 PCI MSI/MSI-X config metadata.

## Per-Device Interrupt State

`i_ddi_intr_devi_init()` allocates `devinfo_intr_t` for a devinfo node and caches supported interrupt types. `i_ddi_intr_devi_fini()` frees the metadata only when no interrupts are currently allocated. It also frees the legacy fixed-handle table and removes any IRM request before freeing `devi_intr_p`.

The file provides straightforward getters/setters for:
- supported interrupt types;
- supported interrupt count;
- current interrupt type;
- current allocated interrupt count;
- current enabled interrupt count;
- MSI-X metadata pointer;
- fixed interrupt handle slots.

`i_ddi_get_intr_handle()` and `i_ddi_set_intr_handle()` bounds-check interrupt numbers against cached supported count. The handle table is allocated lazily when the first fixed interrupt handle is stored.

## Availability and Limits

`i_ddi_intr_get_current_navail()` returns precise IRM-managed availability when the device has a request associated with a pool and the requested type matches; it locks `ipool_navail_lock` while reading `ireq_navail`. Otherwise it falls back to `i_ddi_intr_get_limit()`.

`i_ddi_intr_get_limit()` chooses a default limit from an IRM pool when one exists or from `DDI_INTROP_NAVAIL` otherwise. It caps the result by device-supported interrupt count. If both system and driver support IRM, the limit becomes the device-supported count. Otherwise global MSI-X and MSI caps are imposed (`ddi_msix_alloc_limit` on x86 and `DDI_MAX_MSI_ALLOC` for MSI).

## Properties and Compatibility Stubs

`i_ddi_get_intr_weight()` reads the uncommitted `ddi-intr-weight` integer property and clamps values below `-1` to undefined. `i_ddi_set_intr_weight()` updates the property only for positive changed values and returns the previous weight.

The obsolete busops entry points `i_ddi_get_intrspec()`, `i_ddi_add_intrspec()`, `i_ddi_remove_intrspec()`, and `i_ddi_intr_ctlops()` all warn that the parent nexus is down-rev and return unsupported or null behavior. They exist to catch drivers/nexus paths that have not moved to the newer interrupt operation interface.

## Interrupt Affinity and x86 Metadata

`get_intr_affinity()` requires a non-null enabled interrupt handle, delegates `DDI_INTROP_GETTARGET`, and caches the returned target CPU. `set_intr_affinity()` requires an enabled MSI-X handle, delegates `DDI_INTROP_SETTARGET`, and caches the target on success.

On x86, the file also stores and retrieves PCI config handles and MSI/MSI-X capability pointers in `devinfo_intr_t`.

## Subset Relevance

This file is a lower-level support layer for interrupt resource tracking. Storage drivers depend on these helpers through the public DDI interrupt APIs, particularly for MSI/MSI-X limits, current availability, legacy fixed interrupt handles, and CPU affinity.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_impl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_irm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_irm.c

## Role

`ddi_intr_irm.c` implements Interrupt Resource Management. IRM manages pools of interrupt vectors, tracks device interrupt requests, balances allocation across devices, and notifies IRM-aware drivers when MSI-X allocations should grow or shrink.

The file defines global IRM enable/active flags, default balancing policy, pool list locking, debug tunables, pool lifecycle routines, request insertion/modification/removal, callback-state changes, the balancing thread, reduction algorithms, and notification helpers.

## Initialization and Pool Lifecycle

`irm_init()` validates the default policy and initializes the global pool list when IRM is enabled. `i_ddi_irm_poststartup()` activates IRM after I/O startup by creating one balancing thread per existing pool and setting `irm_active` so future pools are activated at creation.

`ndi_irm_create()` validates nexus-supplied parameters, allocates a `ddi_irm_pool_t`, records owner, interrupt types, total size, policy, and default size, initializes request and scratch lists plus locks/CV, adds the pool to the global list, and starts a balancing thread if IRM is already active.

`ndi_irm_resize_pool()` updates pool size directly when growing or when current reservations fit the new size. When shrinking below reserved count, it performs a synchronous rebalance and rolls back if the pool cannot free enough vectors.

`ndi_irm_destroy()` requires an empty pool, removes it from the global list, asks the balancing thread to exit if active, joins it, destroys locks/lists/CV, and frees the pool.

## Request Management

`i_ddi_irm_insert()` maps a device into a pool for a given interrupt type. It ignores duplicates, finds a pool through `i_ddi_intr_get_pool()`, detects driver IRM support through `i_ddi_irm_supported()`, computes request/minimum/partial sizes, allocates a `ddi_irm_req_t`, verifies minimum fit, inserts it sorted by request size, and either fulfills directly, partially fulfills plus queues background rebalance, or performs immediate synchronous rebalance. If no interrupt is available at all, it removes the request and returns `DDI_EAGAIN`.

`i_ddi_irm_modify()` changes request size. MSI requests cannot be resized. Increases for non-IRM-aware drivers go through `i_ddi_irm_modify_increase()`, which can use a temporary proxy request for synchronous rebalance while preventing the existing allocation from being reduced. Decreases and IRM-aware changes update pool accounting, resort the request, and queue rebalancing.

`i_ddi_irm_remove()` removes a device request, subtracts minimum/request/reserved counts, queues rebalance, clears `devi_irm_req_p`, and frees the request.

`i_ddi_irm_set_cb()` updates whether a request is callback-capable. Gaining callback support lowers the minimum for MSI-X requests and queues background rebalance. Losing callback support reduces the request to static/default limits, updates minimum accounting, rebalances synchronously before clearing the callback flag, and resorts the request.

`i_ddi_irm_supported()` limits IRM-aware behavior to MSI-X devices with a registered DDI callback carrying `DDI_CB_FLAG_INTR`.

## Balancing Thread and Algorithms

Each pool has an `irm_balance_thread()` that performs initial balancing, marks the pool active, then waits for queued work, timeout intervals, waiters, or exit. Synchronous callers set a waiter flag and sleep on the pool CV until balance completes.

`i_ddi_irm_balance()` resets reducible requests to maximum availability, moves them into a scratch list, calls `i_ddi_irm_reduce()`, and then sends remove notifications before add notifications. If a driver fails to release interrupts after a remove notification, the request is removed from scratch processing, the imbalance is recomputed, and balancing restarts from the head.

`i_ddi_irm_reduce()` computes pool imbalance and first tries policy reduction. If that cannot reduce enough, it reduces a new request as a last resort.

`i_ddi_irm_reduce_by_policy()` supports:
- `DDI_IRM_POLICY_LARGE`, which reduces larger requests first;
- `DDI_IRM_POLICY_EVEN`, which reduces reducible requests evenly.

The algorithm operates on the scratch list sorted by request size, preserves descending order, avoids reducing below the pool default size during policy reductions, and uses batched reductions to minimize iterations.

`i_ddi_irm_reduce_new()` reduces the one new request when policy reductions are insufficient.

## Pool Lookup and Driver Notification

`i_ddi_intr_get_pool()` returns an existing associated pool when compatible, otherwise asks the nexus through `DDI_INTROP_GETPOOL`.

`i_ddi_irm_notify()` compares current availability to the scratch value, determines add/remove action and count, calls the driver's registered callback, logs callback failures, verifies the driver released enough interrupts after remove actions, adjusts pool reserved counts if not, and updates scratch state.

## Locking and Error Behavior

Pool structure is protected by `ipool_lock`; availability reads are isolated by `ipool_navail_lock` because readers can query availability while rebalancing. The global pool list has `irm_pools_lock`. The balancing path is careful about synchronous waiters and avoids deadlock when IRM is not yet active.

Failures are surfaced as `DDI_EINVAL`, `DDI_ENOTSUP`, `DDI_EAGAIN`, or `DDI_FAILURE`, with warnings when pools are too full or drivers fail callbacks/release requirements.

## Subset Relevance

IRM directly affects how many interrupt vectors high-performance storage drivers can allocate. It is important for MSI-X-heavy controllers and therefore part of the storage substrate under subset A.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_intr_irm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_nodeid.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_nodeid.c

## Role

`ddi_nodeid.c` implements DDI node ID management. It allocates, frees, and reserves integer node IDs for devinfo nodes using a sorted free-list of available ranges.

The managed range is `1 .. 0x10000000`. Values `0`, `DEVI_PSEUDO_NODEID`, and `DEVI_SID_NODEID` are illegal. The low numeric range is chosen to avoid overlap with PROM node IDs, even though the code can handle a broader 32-bit range.

## Data Structure

The free list consists of `struct available` range records:
- `nodeid` is the first free ID in the range;
- `count` is the number of consecutive free IDs;
- `next`/`prev` link records in sorted order.

The allocator starts with one seed range copied into heap memory during `impl_ddi_init_nodeid()`. A single global mutex, `nodeid_lock`, protects the list.

## Allocation and Freeing

`impl_ddi_alloc_nodeid()` takes the first ID from the head range without allocating memory. It advances the range start and decrements count, unlinking and freeing the range after dropping the lock if it becomes empty. It returns `DDI_FAILURE` and `*nodeid = 0` when no IDs remain.

`impl_ddi_free_nodeid()` allocates a potential new range before taking the lock, then reinserts the freed ID into the sorted list. It handles four cases:
- extend the beginning of an existing range;
- extend the end of an existing range and coalesce with the next range if adjacent;
- insert a one-ID range before the next higher range;
- append a one-ID range at the end.

If the freed ID already lies inside a free range, the function panics because that means a duplicate free.

## Reserving Existing IDs

`impl_ddi_take_nodeid()` removes a specified ID from the free list, usually to reserve an externally supplied node ID. IDs outside the managed range are treated as successfully reserved because this allocator does not own them.

Within a free range, the function can:
- take the first ID by advancing the range;
- take the last ID by decrementing count;
- take a middle ID by splitting the range into two records.

The middle-split case needs a preallocated range record. If called with `KM_NOSLEEP` and allocation fails, it returns `-1`; otherwise success is `0`. If the ID is not found in the free list, the function logs that uniqueness may not be guaranteed but still returns success.

## Subset Relevance

Node IDs are part of the devinfo tree identity layer. Filesystem and storage drivers appear as devinfo nodes and depend indirectly on stable allocation/reservation of these IDs during device enumeration.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_nodeid.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_periodic.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_periodic.c

## Role

`ddi_periodic.c` implements `ddi_periodic_add(9F)` and `ddi_periodic_delete(9F)` through the cyclic subsystem. It provides DDI-visible periodic callbacks at IPL 0 through IPL 10, either in kernel taskq context or via soft interrupt queues.

The implementation deliberately prevents overlapping executions of the same periodic handler and tightens cancellation semantics so the deleting caller blocks until the handler is no longer dispatched or executing.

## Core Objects and Globals

Each periodic registration has a `ddi_periodic_impl_t` allocated from `periodic_cache`, an opaque ID from `periodic_id_space`, a cyclic ID, lock/CV, preallocated taskq entry, handler, argument, level, interval, flags, and execution thread pointer.

Global state includes:
- `periodics`, the list of all active periodics;
- `periodic_softint_queue[10]` for IPL 1 through IPL 10;
- `periodic_taskq` for IPL 0 work;
- `periodics_lock`, protecting the global list and soft interrupt queues.

Tunables set max ID, taskq thread count, and base resolution. The minimum supported interval is 10 ms by default.

## Registration and Dispatch

`ddi_periodic_init()` creates the cache, active list, ID space, soft interrupt queues, taskq, and global mutex. `ddi_periodic_fini()` deletes any remaining periodics, destroys the taskq, ID space, cache, lists, and mutex.

`i_timeout()` is the implementation behind periodic add. It allocates a periodic, stores handler metadata, rounds intervals up to the supported resolution, creates a cyclic at `CY_LOCK_LEVEL`, and only then inserts the periodic into the visible global list before returning the opaque ID.

`periodic_cyclic_handler()` runs when the cyclic fires. It skips cancelled or already-dispatched periodics, marks the object dispatched, and either dispatches `periodic_execute()` to the taskq for IPL 0 or queues the object on the appropriate soft interrupt list and calls `sir_on(level)`.

`ddi_periodic_softintr()` drains the queue for one soft interrupt level and executes each pending periodic.

## Execution and Cancellation

`periodic_execute()` verifies the object is dispatched but not executing, checks cancellation, marks `DPF_EXECUTING`, records `curthread`, drops the lock, calls the consumer handler, then clears execution and dispatch flags, increments fire count, and broadcasts the CV.

`i_untimeout()` removes the periodic from the global list so only one deletion caller owns final cleanup. It panics if called from the periodic's own handler to avoid self-deadlock, marks the object cancelled, removes the cyclic under `cpu_lock`, waits for dispatched/executing flags to clear, and frees the ID, CV, lock, and cache object.

## Locking and Error Behavior

The file documents lock ordering: do not hold an individual periodic lock while acquiring `periodics_lock`. Objects in soft interrupt queues are protected from free by the dispatched flag. Cancellation waits for both dispatch queue removal and handler completion.

The implementation uses `VERIFY()` heavily for invariant checks. It warns and rounds up when a caller asks for a finer period than supported.

## Subset Relevance

Periodic callbacks are general OS driver infrastructure. Storage and filesystem-adjacent drivers may use this DDI service for polling, maintenance, or timeout-like periodic work.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_periodic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_ufm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_ufm.c

## Role

`ddi_ufm.c` implements the DDI UFM subsystem, which lets drivers expose upgradable firmware/module image information and image-read support to the `ufm(4D)` pseudo driver. It tracks per-device UFM handles, caches UFM reports, dispatches driver UFM ops, and provides helper setters for image and slot metadata.

## Handle Registry and Locking

UFM handles are stored in a global AVL tree keyed by device path. `ufm_lock` serializes tree access. Each `ddi_ufm_handle_t` has its own lock protecting state and cached data.

The documented lock discipline is:
- acquire `ufm_lock` to find a handle;
- acquire the handle lock;
- release `ufm_lock`;
- inspect state, update cache, or call UFM entry points while holding the handle lock.

Only one UFM handle lock should be held at a time.

## Cache Management

`ufm_cache_invalidate()` frees cached images, slots, strings, misc nvlists, the report nvlist, and resets image count/capability state. It expects the handle lock to be held.

`ufm_cache_fill()` populates the cached report lazily. It returns immediately if a report already exists. Otherwise it:
- calls the driver's `ddi_ufm_op_getcaps()`;
- requires `DDI_UFM_CAP_REPORT`;
- gets image count through `ddi_ufm_op_nimages()` or defaults to one image;
- allocates image records;
- calls `ddi_ufm_op_fill_image()` for each image and validates description/slot count;
- allocates slots and calls `ddi_ufm_op_fill_slot()` for each slot;
- asserts non-empty slots have a version;
- builds nested nvlists for images and slots;
- stores the final report in `ufmh_report`.

Any failure invalidates partially built cache state and returns the driver or local error.

## Image Reading

`ufm_read_img()` checks driver capabilities and the presence of `ddi_ufm_op_readimg()`, rejects unsupported reads, detects offset/length overflow, allocates a 1 MiB staging buffer, and loops until the requested length is copied out. Each iteration calls the driver read op and then `ddi_copyout()` to user/kernel ioctl destination according to copy flags. It returns the number of bytes read through `nreadp`.

## Registration and Driver Helpers

`ufm_init()` initializes the AVL tree and mutex during DDI setup.

`ufm_find()` searches by devpath and returns a handle with its lock held.

`ddi_ufm_init()` validates version and required ops, derives the devinfo path, reuses an old handle if the driver instance registered before, otherwise allocates a new one, records ops/arg/version/state, inserts new handles into the AVL tree, and creates a `ddi-ufm-capable` boolean property.

`ddi_ufm_fini()` marks the handle shutting down and invalidates cache. It does not remove the handle from the AVL tree, allowing reuse across unload/suspend scenarios. `ddi_ufm_update()` invalidates the cache and marks the handle ready unless shutdown is in progress.

Setter helpers update image descriptions, slot counts, image/slot misc nvlists, slot versions, attributes, and image sizes, replacing prior allocated data as needed.

## Subset Relevance

Firmware reporting and image reads matter for storage controllers and device management. This file is driver infrastructure rather than filesystem code, but it supports operational visibility for hardware that backs block and filesystem stacks.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddi_ufm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddifm.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddifm.c

## Role

`ddifm.c` implements DDI fault-management support for device drivers. It covers service-impact state changes, ereport posting, driver-defect ereports, FM handler registration, FM capability initialization/finalization, and access/DMA error state get/set/clear helpers.

The file defines the programming model for DDI fault-management capabilities: ereport generation, error callbacks, access-handle checking, and DMA-handle checking.

## Service Impact and Ereport Posting

`ddi_fm_service_impact()` updates devinfo service state under `devi_lock` and posts service impact ereports for lost, degraded, restored, or unaffected service. It avoids posting service changes for devices already offline.

`i_ddi_drv_ereport_post()` posts driver-defect reports from the root devinfo node when root supports ereports. In sleepable context it captures a stack trace, converts PCs to symbol strings, and includes driver name, stack depth, stack strings, and optional error-specific nvlist. In non-sleeping context it posts a smaller payload without allocating stack arrays.

`fm_dev_ereport_postv()` is the common ereport builder for DDI and NDI posting paths. It validates that the eqdip is ereport-capable, chooses normal nvlist allocation for sleepable non-panic context or reserves an errorq element for nosleep/panic-safe context, validates the required first vararg tuple is the ereport version, prefixes the error class with `io.`, generates ENA if needed, creates a dev-scheme detector FMRI from devpath/minor/devid/target-port data, merges optional payload nvlist and varargs payload, then posts via `fm_ereport_post()` or commits the errorq element.

`ddi_fm_ereport_post()` posts using the device itself as the ereport-capable node. `ndi_fm_ereport_post()` posts on behalf of a child through its parent and requires sleepable context.

## Error Callback Registration

`i_ddi_fm_handler_enter()` and `i_ddi_fm_handler_exit()` serialize driver FM error handling through the FM handle mutex and record the lock owner. `i_ddi_fm_handler_owned()` checks ownership.

`ddi_fm_handler_register()` rejects interrupt context, finds the parent devinfo node, verifies both child and parent have error-callback capability, allocates an error handler record and target record, and links it into the parent's FM target list under the parent's FM handler lock.

`ddi_fm_handler_unregister()` performs the inverse search/removal from the parent target list and frees the records.

## FM Initialization and Finalization

`ddi_fm_init()` must be called while the device is attaching. It honors default capability requests, asks the parent bus to initialize FM support and possibly adjust the iblock cookie, allocates an `i_ddi_fmhdl`, creates a virtual kstat named `fm`, initializes error counters and locks, and then enables the subset of requested capabilities also supported by the parent/system.

For enabled capabilities it creates devinfo properties:
- `fm-ereport-capable`;
- `fm-errcb-capable`;
- `fm-dmachk-capable`;
- `fm-accchk-capable`.

It also initializes DMA and access error caches through `i_ndi_fmc_create()` and returns the actual capability bitmask and iblock cookie.

`ddi_fm_fini()` requires detach or attach cleanup context. It deletes the kstat, removes capability properties, unregisters error callbacks for non-root devices, destroys DMA/access caches, calls parent bus FM fini, frees the handle, and clears `devi_fmhdl`. The access property removal string is `fm-accachk-capable`, which differs from the creation string `fm-accchk-capable` and is notable when auditing property cleanup behavior.

`ddi_fm_capable()` returns the device's current FM capability bitmask or `DDI_FM_NOT_CAPABLE`.

## Access and DMA Error Helpers

`ddi_fm_acc_err_get()` and `ddi_fm_dma_err_get()` validate the caller version, return early for null handles, and copy error status, ENA, expected flag, and handle pointer into `ddi_fm_error_t` when an error exists. Invalid versions generate driver-defect ereports and panic.

`ddi_fm_acc_err_clear()` and `ddi_fm_dma_err_clear()` reset handle error state to `DDI_FM_OK`, zero ENA, and mark the next error unexpected. Invalid versions also panic through defect reporting.

`i_ddi_fm_acc_err_set()` and `i_ddi_fm_dma_err_set()` set ENA/status/expected fields on the handle and increment per-device FM kstat counters for access or DMA errors.

`i_ddi_fm_acc_err_cf_get()` and `i_ddi_fm_dma_err_cf_get()` return comparison metadata from the handle's error record.

## Subset Relevance

Fault management is central to robust storage and filesystem operation because it records device faults, DMA/access errors, and service degradation. Storage drivers use these facilities to communicate hardware and I/O failures to the broader fault-management stack.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/ddifm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcache.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcache.c

## Role

`devcache.c` implements persisted kernel cache-file management for device metadata, usually under `/etc/devices`. Clients register cache files, keep their own in-memory lists, and provide pack/unpack/free callbacks. A background flush daemon serializes dirty in-memory state into nvlist-backed files without blocking the client path that updates device metadata.

The design is explicitly cache-oriented: persisted data must be stateless and regenerable through normal system operation. Examples include device ID caches that help attach a target device directly instead of forcing traversal/attachment of large parts of the device tree.

## Global State and Initialization

The global file lists are:
- `nvf_cache_files`, the normal registered file list;
- `nvf_dirty_files`, a temporary list used while flushing dirty files;
- `nvf_cache_mutex`, protecting list movement.

Flush-daemon state includes timer ID/busy flags, active thread flags, the flush CV/lock, delayed wakeup state, and tunables for write delay and idle exit time. Kernel file I/O reads/writes can be disabled with tunables.

`i_ddi_devices_init()` creates the lists and mutex, then initializes retire-store and devid-cache subsystems. `i_ddi_read_devices_files()` reads the retire store first, then MDI and devid cache files unless reads are disabled. `i_ddi_start_flush_daemon()` initializes daemon synchronization and wakes the daemon if any registered file is already dirty. `i_ddi_clean_devices_files()` cleans devid and MDI caches.

## Registration and Client Interface

`nvf_register_file()` allocates an `nvfd_t`, stores operation callbacks, initializes the per-file rwlock, inserts it into the global cache-file list, and returns an opaque handle. There is no unregister path.

Client helpers expose:
- `nvf_cache_name()` for the backing path;
- `nvf_lock()` for the per-file rwlock;
- `nvf_list()` for the client-owned data list;
- `nvf_mark_dirty()` and `nvf_is_dirty()` with assertions that the caller holds the lock in the required mode.

The file-level lock must be held as reader for traversal/state checks and writer for list mutation, dirty marking, reads, pack, unpack, and free-list callbacks.

## File Format and Read Path

Persisted files contain an `nvpf_hdr_t` followed by a packed native nvlist. `nvp_cksum()` computes a simple XOR checksum over 16-bit words, with odd trailing byte handling.

`fread_nvlist()` opens the file through `kobj_open_file()`, reads and validates the header magic/version/header checksum, reads the nvlist payload, verifies there is no trailing data, validates payload checksum, unpacks the nvlist, and returns it. It maps missing files to `ENOENT`, I/O errors to `EIO`, and malformed/corrupt data to `EINVAL`.

`fread_nvp_list()` walks the top-level nvlist. Each top-level pair must be a nested nvlist; the pair name identifies the cached element. It calls the client's unpack callback for each sublist while holding the file write lock. Unsupported types or unpack errors invalidate the partially built list by calling the client's free-list callback.

`nvf_read_file()` wraps this read path, respects global read-disable, and sets flags that later produce create/rebuild messages depending on whether the file was missing, corrupt, or unreadable.

## Kernel File I/O and Write Path

Low-level helpers wrap vnode operations:
- `kfcreate()` opens a file with create/write/truncate;
- `kfremove()` removes a file;
- `kfread()` and `kfwrite()` use `vn_rdwr()` and track file position/state;
- `kfclose()` fsyncs writable files before closing and releases the vnode;
- `kfrename()` atomically renames a temporary file over the target.

`fwrite_nvlist()` packs an nvlist, builds a checked header plus payload buffer, writes to `filename.new`, fsyncs/closes it, removes it on error, and renames it over the target on success. This temp-file-plus-rename protocol reduces the chance of cache-file data loss.

`e_fwrite_nvlist()` wraps write status into DDI return codes and marks a file read-only if the write failed with `EROFS`.

## Flush Scheduling and Daemon

`nvf_wake_daemon()` is called after dirtying a cache. It does nothing until I/O is initialized or during shutdown. Otherwise it starts the daemon thread if inactive, computes a delayed flush deadline, and arms a timeout when one is not already active. Repeated updates push `nvpticks` later so bursty device changes are coalesced.

`nvpflush_timeout()` either re-arms itself if the target deadline is still more than four ticks away or signals the daemon to flush.

`nvpflush_one()` handles one file. It obtains the file rwlock, skips clean/read-only/write-disabled/shutdown files, upgrades to writer, asks the client to pack the list into an nvlist, clears dirty and marks flushing, writes the nvlist without holding the file lock, then clears flushing and updates flags. Failed writable updates set error and dirty flags for retry. Read-only failures are silently treated as success. If the file was dirtied while the write was in progress, it returns failure so the daemon will schedule another flush.

`nvpflush_daemon()` waits for flush requests or idle timeout, exits when idle with no pending timer or on shutdown, moves dirty files from the main list to the dirty list, flushes them without holding the global list lock, moves clean files back, invokes write-complete callbacks, and reschedules itself when a file remains dirty or a write fails.

## Locking and Failure Behavior

The implementation separates global list locking from per-file data locking. Dirty files are moved to `nvf_dirty_files` so the daemon does not hold `nvf_cache_mutex` across packing or kernel file I/O. Packing and unpacking callbacks are called with the per-file write lock held and are expected to return with it still held.

Write failures are retried after delay unless the backing filesystem is read-only. Corrupt or missing files are not fatal because caches are expected to be rebuilt.

## Subset Relevance

This file is directly relevant to device discovery and persistent device metadata, including caches used by storage identity paths. It supports faster device attachment and stable metadata reconstruction for block/storage devices that filesystems depend on.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devcache.c -->