# Group Research: group_561_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_os_s_6d49b265b59d

Scope verified against `Docs/research_subset_a.md`: `sources/os/illumos/illumos-gate` is included in subset A. The listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunddi.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunddi.c

## Purpose

`sunddi.c` implements a large portion of the illumos kernel DDI/DKI support layer used by drivers, nexus drivers, devfs, layered drivers, and dynamic reconfiguration code. It provides generic wrappers for bus mapping, control operations, DMA, register access, device properties, minor nodes, device path construction, soft-state storage, device IDs, event callbacks, user-memory locking, task queues, and branch creation/configuration.

This file is central framework glue rather than a single subsystem. Many routines are exported compatibility interfaces, while others are consolidation-private helpers used by devinfo, devfs, LDI, FMA, DACF, sysevent, and DR paths.

## Main Interfaces

Bus, mapping, and access helpers:

- `ddi_map()`
- `ddi_apply_range()`
- `ddi_map_regs()`
- `ddi_unmap_regs()`
- `ddi_bus_map()`
- `nullbusmap()`
- `ddi_rnumber_to_regspec()`
- `ddi_regs_map_setup()`
- `ddi_regs_map_free()`
- `ddi_device_mapping_check()`
- `ddi_map_fault()`
- `ddi_segmap()`

Peek/poke and copy helpers:

- `ddi_peek()`, `ddi_poke()`
- `ddi_peek8()`, `ddi_peek16()`, `ddi_peek32()`, `ddi_peek64()`
- `ddi_poke8()`, `ddi_poke16()`, `ddi_poke32()`, `ddi_poke64()`
- `ddi_peekpokeio()`
- `ddi_copyin()`, `ddi_copyout()`
- `ddi_device_zero()`
- `ddi_device_copy()`
- `ddi_swap16()`, `ddi_swap32()`, `ddi_swap64()`

DMA interfaces:

- legacy bus-DMA dispatchers such as `ddi_dma_allochdl()`, `ddi_dma_bindhdl()`, `ddi_dma_unbindhdl()`, `ddi_dma_flush()`, `ddi_dma_win()`
- public handle routines `ddi_dma_alloc_handle()`, `ddi_dma_free_handle()`
- memory routines `ddi_dma_mem_alloc()`, `ddi_dma_mem_free()`
- binding routines `ddi_dma_buf_bind_handle()`, `ddi_dma_addr_bind_handle()`
- cookie helpers `ddi_dma_nextcookie()`, `ddi_dma_ncookies()`, `ddi_dma_cookie_iter()`, `ddi_dma_cookie_get()`, `ddi_dma_cookie_one()`
- window and fault helpers `ddi_dma_numwin()`, `ddi_dma_getwin()`, `ddi_check_dma_handle()`, `i_ddi_dma_set_fault()`, `i_ddi_dma_clr_fault()`

Property framework:

- `ddi_prop_op()`
- `ddi_prop_search_common()`
- `ddi_bus_prop_op()`
- `impl_ddi_bus_prop_op()`
- `ddi_prop_lookup_common()`
- typed lookup/update routines for int, int64, string, string array, byte array, and composite properties
- legacy property routines `ddi_getprop()`, `ddi_getlongprop()`, `ddi_getlongprop_buf()`, `ddi_getproplen()`
- external `e_ddi_get*` property wrappers for `dev_t`
- property remove/undefine/cache/dynamic snapshot helpers

Devinfo, minor-node, and path helpers:

- `ddi_binding_name()`, `ddi_driver_major()`, `ddi_driver_name()`
- `ddi_get_name()`, `ddi_node_name()`, `ddi_get_instance()`, `ddi_root_node()`
- `ddi_create_minor_node()`, `ddi_create_priv_minor_node()`, `ddi_create_default_minor_node()`
- `ddi_create_internal_pathname()`
- `ddi_remove_minor_node()`
- `ddi_deviname()`, `ddi_pathname()`, `ddi_pathname_minor()`
- `ddi_pathname_obp()`, `ddi_pathname_obp_set()`
- `ddi_dev_pathname()`, `e_ddi_majorinstance_to_path()`

Soft-state and ID utilities:

- `ddi_soft_state_init()`, `ddi_soft_state_zalloc()`, `ddi_get_soft_state()`, `ddi_soft_state_free()`, `ddi_soft_state_fini()`
- `ddi_soft_state_bystr_*()`
- `ddi_strid_*()`

Device ID and layered-driver helpers:

- `ddi_devid_init()`
- `ddi_devid_register()`
- `ddi_devid_unregister()`
- `ddi_devid_get()`
- `ddi_lyr_get_devid()`
- `ddi_lyr_get_minor_name()`
- `ddi_lyr_devid_to_devlist()`
- `ddi_lyr_free_devlist()`

User-memory and buf helpers:

- `umem_lockmemory()`
- `ddi_umem_lock()`
- `ddi_umem_unlock()`
- `ddi_umem_iosetup()`
- `i_ddi_incr_locked_memory()`
- `i_ddi_decr_locked_memory()`

Callbacks, task queues, events, and DR:

- `ddi_set_callback()`, `ddi_run_callback()`
- `ddi_periodic_add()`, `ddi_periodic_delete()`
- `ddi_add_event_handler()`, `ddi_remove_event_handler()`, `ddi_get_eventcookie()`
- `ddi_cb_register()`, `ddi_cb_unregister()`
- `ddi_taskq_create()`, `ddi_taskq_destroy()`, `ddi_taskq_dispatch()`, `ddi_taskq_wait()`, suspend/resume helpers
- `e_ddi_branch_create()`, `e_ddi_branch_configure()`, `e_ddi_branch_unconfigure()`, `e_ddi_branch_destroy()`
- `e_ddi_branch_hold()`, `e_ddi_branch_rele()`, `e_ddi_branch_held()`
- `e_ddi_branch_referenced()`

## Mapping And Bus Operations

The top of the file implements generic mapping and control-operation dispatch through parent nexus bus operations. `ddi_map()` calls the parent’s `bus_map`; `ddi_bus_map()` delegates to `i_ddi_bus_map()`, and `nullbusmap()` rejects register-number mappings but passes other mappings upward. `ddi_map_regs()` and `ddi_unmap_regs()` build `ddi_map_req_t` structures for register mappings. On x86, `ddi_map_regs()` also synthesizes a `chosen-reg` property from `registers` or `reg`, then removes it on unmap.

Peek and poke operations use `i_ddi_peekpoke()` to package access parameters into `peekpoke_ctlops_t` and issue `DDI_CTLOPS_PEEK` or `DDI_CTLOPS_POKE`, or fall back to `peekpoke_mem()` when no devinfo node exists. The typed wrappers validate transfer sizes, and `ddi_peekpokeio()` uses byte, word, long, or 64-bit transfers to move data between a `uio` and device memory while preserving fault-aware semantics.

## DMA Support

The file contains both old-style dispatch entry points and newer public DMA helpers. Non-SPARC wrappers locate the relevant bus DMA operation pointer through cached devinfo fields and call nexus operations for allocation, binding, unbinding, flushing, windows, and synchronization.

`ddi_dma_alloc_handle()` copies caller attributes, chooses a driver or generic `bus_dma_allochdl` routine, and allocates a DMA handle. `ddi_dma_mem_alloc()` allocates a matching access handle, validates cache attributes, normalizes missing transfer-mode flags to streaming, initializes access-handle metadata, and calls `i_ddi_mem_alloc()`. On allocation failure with a custom wait callback, it queues the callback through the DDI callback system.

`ddi_dma_buf_bind_handle()` converts a `buf` into a `ddi_dma_req`, accounting for page I/O, shadow buffers, kernel remapped buffers, and user address spaces. `ddi_dma_addr_bind_handle()` binds a raw address range. Cookie helpers expose sequential, indexed, iterator, and single-cookie access while guarding misuse with assertions or panics for invalid single-cookie assumptions.

DMA fault support stores fault state in `ddi_dma_impl_t`; `ddi_check_dma_handle()` dispatches to a handle-specific checker if present, while `i_ddi_dma_set_fault()` and `i_ddi_dma_clr_fault()` toggle state and call optional notification hooks.

## Property Framework

The property subsystem is one of the largest sections. It manages software-defined driver, system, hardware, and global properties, plus PROM-derived properties. `ddi_prop_search_common()` implements the core search order:

1. driver-defined properties
2. system-defined properties
3. devinfo global properties
4. hardware properties
5. parent bus property operations
6. root/options fallback where applicable

Property search carefully handles `PROP_EXISTS`, `PROP_LEN`, `PROP_LEN_AND_VAL_BUF`, and `PROP_LEN_AND_VAL_ALLOC`. For sleepable allocation, it drops `devi_lock`, allocates a buffer, and retries to avoid sleeping while holding the lock. Explicit undefined properties return `DDI_PROP_UNDEFINED`.

The file defines OBP 1275-style encode/decode operators for integers, strings, and bytes, plus illumos int64 extensions. Typed update and lookup routines encode values into property handles, store encoded bytes into property lists, later decode into driver-facing allocated buffers, and use `ddi_prop_free()` to free decoded allocations.

Dynamic size properties for block drivers are handled by `ddi_prop_op_nblocks_blksize()`, `ddi_prop_op_nblocks()`, `ddi_prop_op_size_blksize()`, and `ddi_prop_op_size()`. These synthesize `Size`, `Nblocks`, legacy `size`, legacy `nblocks`, and `blksize` where representable, falling back to normal property lookup when values exceed supported widths.

## PROM And Global Properties

`impl_ddi_bus_prop_op()` searches PROM properties for self-identifying nodes when allowed, returning `DDI_PROP_FOUND_1275` so callers know to use PROM decode behavior. `ddi_bus_prop_op()` wraps this default nexus property behavior, then searches inherited software properties and finally the `options` node at the root.

Global property lookup uses `devnamesp[major].dn_global_prop_ptr` and `dn_lock`. `ddi_prop_lookup_common()` can search these global lists for rootnex or unbound DLPI style-2 devices.

## Devinfo And Minor Nodes

The devinfo accessors expose binding names, driver names, node names, parent/child/sibling links, instance numbers, node IDs, driver ops, and driver/private data. `ddi_driver_major()` is explicitly preferred over recomputing the major number from a dynamic alias binding.

Minor-node creation is centralized in `ddi_create_minor_common()`. It validates spec type, minor number size, driver binding, node type, network interface naming constraints, device class derivation, privilege metadata, clone aliases, and DACF matching. It appends `ddi_minor_data` under the devinfo busy lock and logs devfs sysevents for runtime minor creation outside attach/detach. Removal walks the minor list under `ndi_devi_enter()`, logs remove sysevents when appropriate, frees privilege policy, clears DACF client data, and removes matching entries.

Network minor nodes enforce PSARC 2003/375 names with only alphanumeric and underscore characters and length at most `IFNAMSIZ`. Network drivers are marked in `devnamesp`, and physical network drivers are detected when a network minor is created during attach.

## Sysevents And Device Classes

`i_log_devfs_minor_create()` and `i_log_devfs_minor_remove()` publish devfs minor create/remove sysevents with path, class, minor name, driver name, and instance attributes where available. Failure to log create events emits warnings that `/devices` or `/dev` may be stale; remove logging failures are intentionally ignored.

`derive_devi_class()` assigns rough classes based on node type, including disk, network, printer, and lofi pseudo devices. Device class strings are stored on devinfo nodes through `i_ddi_set_devi_class()`.

## Soft State And String IDs

`ddi_soft_state_*()` implements the classic driver soft-state array. It allocates an opaque handle with an expandable pointer array, grows in powers of two, and leaves old arrays on a dirty list so lock-free `ddi_get_soft_state()` readers cannot dereference freed arrays. `ddi_soft_state_fini()` frees all elements and dirty arrays when the driver is quiescent.

`ddi_soft_state_bystr_*()` provides hash-keyed soft state by string. `ddi_strid_*()` maps strings to compact numeric IDs using an `id_space` plus forward and reverse mod_hash tables. IDs are allocated with first-fit to keep ranges dense for callers that use IDs as soft-state indexes.

## Path Construction

`ddi_deviname()` builds one path component from node name and unit address. `ddi_pathname()` recursively builds full devinfo paths; `ddi_pathname_minor()` appends a minor name. `ddi_pathname_obp()` can prefer an `obp-path` property and reconstruct OBP-like paths for nodes with alternate firmware paths.

`ddi_dev_pathname()` reconstructs a path from `dev_t`, handling clone devices specially, resolving major/instance through the instance tree, optionally attaching the device and finding a matching minor node. `e_ddi_majorinstance_to_path()` can reconstruct a path without attach, using the instance tree first and per-driver devinfo lists as a fallback for pseudo branches.

## Device IDs

`ddi_devid_init()` builds binary device IDs for SCSI, ATA, NVMe, encapsulated, and fabricated IDs. Fabricated IDs combine hostid, timestamp, and a generation counter. Driver-name hints are stored in the fixed-size hint field.

`ddi_devid_register()` validates and encodes the ID as a string property, updates `devi_devid_str` for interrupt-context consumers, and registers the ID in the devid-to-path cache. Unregistering clears the cached flag, removes cache entries, frees the saved string, and removes the property.

Layered-driver helpers resolve devids and minor names from `dev_t` and map devid/minor pairs to device lists, triggering discovery if the cache is initially missing.

## User Memory Locking

`umem_lockmemory()` and `ddi_umem_lock()` lock page-aligned user virtual memory and return `ddi_umem_cookie` objects that can later be converted to `buf` structures or exported through devmap paths. The code validates access flags, starts the deferred unlock thread on first use, allocates a cookie, charges max-locked-memory resource controls when needed, and calls `as_pagelock()`.

`umem_lockmemory()` additionally supports `DDI_UMEMLOCK_LONGTERM`. Long-term locks require a cleanup callback and reject regular-file shared mappings to avoid truncate-related deadlocks. It registers `as_add_callback()` so address-space teardown or mapping changes can call `umem_lock_undo()`.

Unlocking is deferred when called from interrupt context. `ddi_umem_unlock()` queues cookies on a FIFO protected by `ddi_umem_unlock_mutex`; `i_ddi_umem_unlock_thread()` drains the queue and participates in CPR. Non-interrupt unlocks call `i_ddi_umem_unlock()` directly. That routine deletes address-space callbacks, unlocks pages, decrements locked-memory accounting, and frees the cookie when all callback references are gone.

`ddi_umem_iosetup()` creates a physical `buf` from locked user memory or non-pageable kernel memory, setting `B_SHADOW` when page arrays are present.

## Callbacks, Periodic Timers, And Task Queues

The DDI callback queue uses a mutex-protected list with an L1 dynamic allocation path and an L2 static emergency pool sized from physical memory. `ddi_set_callback()` records callbacks, coalescing duplicate function/argument pairs by count. `ddi_run_callback()` schedules `real_callback_run()` through `softcall()`, which retries callbacks that return zero and updates kstats.

`ddi_periodic_add()` and `ddi_periodic_delete()` wrap timeout infrastructure with DDI semantics. They reject interrupt-context use and validate interrupt priority levels.

`ddi_taskq_*()` wraps kernel task queues with DDI names derived from driver name and instance. It provides create, destroy, dispatch, wait, suspend, suspended-test, and resume operations.

Generic DDI callbacks registered through `ddi_cb_register()` are stored in `devi_cb_p`. Interrupt-resource-management callbacks notify IRM through `i_ddi_irm_set_cb()` on register and unregister.

## Events, Faults, And Miscellaneous Helpers

Event helpers call into nexus event operations for adding, removing, and resolving event cookies. `ddi_dev_report_fault()` assembles `ddi_fault_event_data`, obtains the device fault event cookie, and posts the event through NDI.

Miscellaneous exported helpers include:

- page/byte conversions `ddi_btop()`, `ddi_btopr()`, `ddi_ptob()`
- critical-section wrappers `ddi_enter_critical()`, `ddi_exit_critical()`
- default/no-op driver callbacks such as `ddi_no_info()`, `ddi_getinfo_1to1()`, `ddifail()`, `ddi_no_dma_*()`
- time, credential, PID, thread DID, signal-receivability, and panic-state helpers
- string duplication/free helpers `ddi_strdup()`, `strdup()`, `strfree()`
- interface-name parsing through `ddi_parse()` and `ddi_parse_dlen()`
- quiesce default helpers `ddi_quiesce_not_needed()` and `ddi_quiesce_not_supported()`

## Dynamic Reconfiguration Branches

The final section implements platform-independent branch creation, configuration, unconfiguration, destruction, holds, and reference checks.

`e_ddi_branch_create()` supports two branch types:

- PROM branches: walk firmware children under a PROM parent, select matching node IDs with a caller-provided predicate, create missing branches, mark new or existing infant branches offline, optionally configure them, and invoke optional callbacks.
- SID branches: allocate synthetic self-identifying devinfo nodes through a caller-supplied creation callback, set the node name from the `name` property, bind a driver if possible, recursively create children based on walk return codes, mark new nodes offline, optionally configure them, and invoke optional callbacks.

`e_ddi_branch_configure()` requires the branch to be held, initializes/binds it if needed, then configures it through `ndi_devi_config_one()`. `e_ddi_branch_unconfigure()` and `e_ddi_branch_destroy()` force devfs cleanup, release the branch hold temporarily under the parent busy lock, offline or remove the branch, and restore the hold if the branch remains.

`e_ddi_branch_referenced()` checks whether a held branch has external references. It walks devfs `dv_node` objects for vnode reference counts, walks specfs snodes for open counts, then optionally walks the devinfo branch and calls a callback with per-dip busy counts.

## Concurrency And Lifetime

Important synchronization and lifetime rules:

- devinfo property lists are protected by `devi_lock`.
- minor-node list mutations use `ndi_devi_enter()` / `ndi_devi_exit()`.
- devnames global property and driver lists use `dn_lock`.
- callback queue state uses `ddi_callback_mutex`.
- user-memory unlock queue uses `ddi_umem_unlock_mutex` and `ddi_umem_unlock_cv`.
- soft-state allocation/free uses a mutex, while `ddi_get_soft_state()` is intentionally lock-free and relies on dirty arrays being retained until finalization.
- branch operations rely on parent busy holds, explicit `DEVI_BRANCH_HELD` references, and careful avoidance of devfs cleanup while the parent is already busy-held.
- `umem_lockmemory()` stores the `as` pointer in the cookie because `proc->p_as` may become stale during process teardown.
- property lookup drops locks before sleepable allocation and retries to avoid blocking under `devi_lock`.

## Dependencies

This file integrates with most of the illumos device framework: devinfo internals, NDI, DDI bus ops, DMA implementation, PROM property access, devfs, specfs, layered driver interfaces, sysevents, DACF, device policy, task queues, kstats, resource controls, zones/projects/tasks, VM address spaces and segments, `as_pagelock()`, buf/page infrastructure, id spaces, mod_hash, event cookies, FMA fault events, and platform PROM-tree access.

## Research Notes

The highest-risk areas are property lifetime under concurrent updates, typed property compatibility with legacy consumers, DMA cookie cursor invariants, user-memory lock/unlock races with address-space callbacks, resource-control accounting balance, minor-node sysevent behavior during attach/detach, branch hold/unconfigure lifetime rules, and branch reference accounting across devfs and specfs. The file also contains many compatibility paths where changing return codes or default behavior could break third-party drivers.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunddi.c -->