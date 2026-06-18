# Research: subset-b-004547

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pagealloc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pagealloc.c

## Purpose

`pagealloc.c` is the mlx5 firmware-page allocator. mlx5 firmware asks the host for 4 KiB adapter pages during boot, initialization, VF/SF enablement, and runtime events; this file allocates host pages, maps them for DMA, tracks the sub-4K slices handed to firmware, and reclaims them when firmware returns pages or when teardown forces recovery.

## Important APIs, Types, and Functions

Key local state is `struct fw_page`, an RB-tree node keyed by DMA page address with a `bitmask` and `free_count` for `MLX5_NUM_4K_IN_PAGE` adapter pages, plus `struct mlx5_pages_req`, the work item used for asynchronous page-request EQ events. The per-function RB roots live in `dev->priv.page_root_xa`; reusable partially free system pages are linked through `dev->priv.free_list`.

Exported or lifecycle functions are `mlx5_pagealloc_init()`, `mlx5_pagealloc_start()`, `mlx5_pagealloc_stop()`, `mlx5_pagealloc_cleanup()`, `mlx5_satisfy_startup_pages()`, `mlx5_reclaim_startup_pages()`, and `mlx5_wait_for_pages()`. Core helpers include `give_pages()`, `reclaim_pages()`, `release_all_pages()`, `alloc_system_page()`, `alloc_4k()`, `free_4k()`, `insert_page()`, `find_fw_page()`, and the EQ notifier `req_pages_handler()`.

## Control Flow

Startup calls `mlx5_satisfy_startup_pages()`, which issues `QUERY_PAGES` for boot or init pages and, if firmware requests pages, calls `give_pages()`. `give_pages()` allocates an input buffer large enough for all PAS entries, repeatedly obtains 4K adapter addresses from existing partially free host pages or allocates/maps a new system page, and sends `MANAGE_PAGES` with `MLX5_PAGES_GIVE`. On command failure it returns every not-yet-accepted 4K slice to software state and optionally notifies firmware with `MLX5_PAGES_CANT_GIVE`.

Runtime requests arrive through the `PAGE_REQUEST` EQ notifier. `req_pages_handler()` decodes function id, EC-function and release-all flags, clamps large negative reclaim requests to firmware limits, allocates a `mlx5_pages_req` with `GFP_ATOMIC`, and queues it on the single threaded page allocator workqueue. `pages_work_handler()` then serializes give, reclaim, or release-all behavior outside interrupt context.

Reclaim uses `MANAGE_PAGES` with `MLX5_PAGES_TAKE`; returned PAS entries are passed to `free_4k()`. If firmware is already gone and `mlx5_cmd_do()` returns `-ENXIO`, `reclaim_pages_cmd()` fabricates output entries from the driver's own RB-tree so the host can forcibly unmap/free pages. `mlx5_reclaim_startup_pages()` walks every function root in the xarray and repeatedly asks firmware for optimal batches until each root is empty or timeout expires.

## State and Persistence Behavior

The file mutates long-lived `dev->priv` state: `page_root_xa`, `free_list`, `pg_wq`, `pg_nb`, aggregate `fw_pages`, per-function-type `page_counters[]`, and diagnostic counters such as `fw_pages_alloc_failed`, `give_pages_dropped`, and `reclaim_pages_discard`. Function identity combines firmware function id and embedded CPU flag into an xarray key; this lets host PF, VF, EC VF, SF, and self pages be reclaimed independently.

The backing storage is ordinary allocated pages DMA-mapped bidirectionally. Firmware only persists the PAS entries it accepted. The driver persists exact subpage ownership in memory and relies on teardown paths to reclaim or force-free anything not returned cleanly.

## Dependencies and Integration Points

This code depends on the mlx5 command interface (`QUERY_PAGES`, `MANAGE_PAGES`), EQ notifier registration, timeout helpers, debugfs page counters, DMA mapping APIs, Linux xarray/RB-tree/list primitives, and device role helpers such as `mlx5_core_is_ecpf()`, `mlx5_core_max_vfs()`, and `mlx5_sf_max_functions()`. SR-IOV teardown calls `mlx5_wait_for_pages()` against VF and EC-VF counters, so page accounting here directly affects VF disable/unload behavior.

## Risks and Edge Cases

The RB-tree comparison is inverted from the usual left-less/right-greater convention but is internally consistent; future edits must preserve matching traversal in insert and lookup. `alloc_system_page()` remaps the same page when DMA address zero is returned and only unmaps the zero mapping later; this unusual retry path is worth regression testing on IOMMUs that can hand out address 0. `free_4k()` trusts firmware-returned PAS entries to point at known tracked pages and only warns if not found. `release_all_pages()` bypasses firmware and adjusts counters based on allocated subpage count, so it must only run when firmware has declared release-all or teardown owns the device.

## Test Signals

Useful signals are boot/init page satisfaction, VF/SF enable-disable loops, EC-PF page accounting, firmware page-request EQ injection, forced internal-error reclaim where firmware commands return `-ENXIO`, debugfs page counters returning to zero, and `mlx5_wait_for_pages()` not timing out during SR-IOV teardown. Fault injection should cover allocation failure, DMA mapping failure, `MANAGE_PAGES` remote IO errors, oversized reclaim events, and duplicate PAS insertion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pagealloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.c

## Purpose

`pci_irq.c` manages MSI-X IRQ allocation for mlx5 PCI PF/VF devices and for subfunctions that borrow their parent device IRQ table. It provides refcounted IRQ objects, IRQ pools for PCI functions and SF control/completion vectors, notifier fanout from the interrupt handler to EQ users, dynamic MSI-X vector allocation when supported, CPU affinity hints, and VF MSI-X table sizing commands.

## Important APIs, Types, and Functions

The central objects are `struct mlx5_irq`, which owns an atomic notifier head, affinity mask, MSI map, pool index, and refcount, and `struct mlx5_irq_table`, which points to `pcif_pool`, `sf_ctrl_pool`, and `sf_comp_pool`. Pool layout is defined by `struct mlx5_irq_pool` in `pci_irq.h`.

Public entry points include `mlx5_irq_table_init()`, `mlx5_irq_table_create()`, `mlx5_irq_table_destroy()`, `mlx5_irq_table_free_irqs()`, `mlx5_irq_table_cleanup()`, `mlx5_irq_table_get()`, `mlx5_irq_table_get_num_comp()`, `mlx5_irq_table_get_sfs_vec()`, `mlx5_irq_table_get_comp_irq_pool()`, `mlx5_ctrl_irq_request()`, `mlx5_ctrl_irq_release()`, `mlx5_irq_request()`, `mlx5_irq_request_vector()`, `mlx5_irq_release_vector()`, `mlx5_irq_attach_nb()`, `mlx5_irq_detach_nb()`, and accessors for IRQ number, index, pool, and affinity mask. VF sizing helpers are `mlx5_get_default_msix_vec_count()` and `mlx5_set_msix_vec_count()`.

## Control Flow

Table creation calculates PCI function completion vectors from ports, online CPUs, EQ capacity, and PCI MSI-X count. If dynamic MSI-X allocation is supported, only vector 0 is allocated initially and later completion vectors use `pci_msix_alloc_irq_at()`. Otherwise all requested vectors are statically allocated by `pci_alloc_irq_vectors()`. `irq_pools_init()` creates the base PCI pool and, if SF capacity exists, carves SF control and completion pools from the remaining vector range.

An IRQ request enters `irq_pool_request_vector()`, which locks the pool and either increments the refcount of an existing xarray entry or calls `mlx5_irq_alloc()`. Allocation creates the `mlx5_irq`, obtains the static or dynamic MSI map, optionally adds a CPU rmap entry for RFS, formats a name, calls `request_irq()` with `irq_int_handler()`, applies affinity hints, and stores the object in the pool xarray. The interrupt handler only calls the atomic notifier chain; EQ objects attach/detach notifier blocks with `mlx5_irq_attach_nb()` and `mlx5_irq_detach_nb()`.

Release uses `_mlx5_irq_release()` to synchronize the IRQ line and decrement the refcount. When it reaches zero, `irq_release()` erases the xarray entry, clears affinity/rmap state, frees the IRQ and dynamic MSI-X vector if needed, releases the cpumask, and frees the object. Shutdown has a special `mlx5_system_free_irq()` path used by `mlx5_irq_table_free_irqs()` to drop OS IRQ resources while keeping mlx5 software IRQ objects alive for later teardown.

## State and Persistence Behavior

Persistent driver state includes `dev->priv.irq_table`, pool xarrays, per-IRQ refcounts, per-IRQ notifier chains, affinity masks, pool thresholds, and optional SF `irqs_per_cpu` arrays. Hardware/PCI state includes allocated MSI-X vectors and per-VF `dynamic_msix_table_size` set through HCA capability commands. SF devices do not own an IRQ table; `mlx5_irq_table_get()` redirects them to `parent_mdev->priv.irq_table`.

## Dependencies and Integration Points

The file integrates with Linux PCI MSI-X APIs, IRQ request/free APIs, `irq_affinity_desc`, RFS `cpu_rmap`, mlx5 EQ code, SF capability helpers, vport capability access for VF MSI-X table updates, and SR-IOV control (`mlx5_core_sriov_set_msix_vec_count()`). Control IRQs are used by async/event EQs; completion IRQs are used by data path EQs.

## Risks and Edge Cases

The code has several split teardown paths: normal refcount release, table destroy cleanup, and system-free for shutdown. Double-free prevention relies on caller sequencing and xarray/refcount invariants. `mlx5_irq_request()` logs `af_desc->mask` and assumes affinity descriptor is present; callers should avoid passing NULL there. Dynamic MSI-X support changes index semantics because nonzero vectors may be allocated at any MSI index while `pool_index` remains the logical index. SF pools can be absent, in which case SFs fall back to PCI function IRQs with lower performance.

## Test Signals

Exercise static and dynamic MSI-X platforms, single-vector devices, multiport devices, SF-heavy configurations, CPU hotplug/online CPU count changes, RFS-enabled builds, notifier attach/detach failure paths, driver shutdown with live EQ references, and VF MSI-X resizing via sysfs. Inspect `/proc/interrupts`, IRQ affinity hints, xarray leak warnings, and that completion EQs do not share above pool thresholds unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.h

## Purpose

`pci_irq.h` is the private header for mlx5 PCI IRQ pool internals. It defines IRQ naming limits, the EQ-reference accounting multiplier, the IRQ pool structure, the SF-pool classifier, and low-level IRQ object functions used by `pci_irq.c` and IRQ affinity code.

## Important APIs, Types, and Functions

The key type is `struct mlx5_irq_pool`, containing a fixed prefix name, xarray index limits, a mutex serializing IRQ creation/destruction, the IRQ xarray, min/max sharing thresholds expressed in EQ references, optional per-CPU SF accounting, and the owning `mlx5_core_dev`. The opaque `struct mlx5_irq` and `struct cpu_rmap` declarations allow consumers to hold IRQ handles without seeing object layout.

Declared functions are `mlx5_irq_alloc()`, `mlx5_irq_get_locked()`, `mlx5_irq_read_locked()`, `mlx5_irq_put()`, and `mlx5_irq_get_pool()`. The inline `mlx5_irq_pool_is_sf_pool()` classifies pools whose name begins with `mlx5_sf`.

## Control Flow

This header has no runtime control flow, but its contract assumes callers hold `pool->lock` when using the `_locked` helpers and that pool indexes are bounded by `xa_num_irqs`. The name and formatted-name constants are used to keep Linux IRQ names inside fixed buffers while appending PCI identity.

## State and Persistence Behavior

The header defines the persistent pool fields that back the IRQ lifecycle: xarray contents, lock, thresholds, and per-CPU accounting. It does not allocate storage itself.

## Dependencies and Integration Points

It depends on `linux/mlx5/driver.h` for `struct mlx5_core_dev` and on Linux xarray/mutex types through included driver headers. It is consumed by `pci_irq.c` and any lower-level affinity helper that needs to inspect or increment IRQ refcounts under the pool lock.

## Risks and Test Signals

`mlx5_irq_pool_is_sf_pool()` uses a string prefix convention rather than an explicit enum, so new SF pool names must retain the `mlx5_sf` prefix. Compile testing should cover `CONFIG_MLX5_SF` and non-SF builds, and lockdep should validate that `_locked` helpers are called under `pool->lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pci_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pd.c

## Purpose

`pd.c` is a minimal mlx5 protection-domain command wrapper. It allocates and deallocates firmware PD numbers used by consumers that need hardware protection-domain isolation, such as RDMA and queue/resource objects.

## Important APIs, Types, and Functions

`mlx5_core_alloc_pd()` builds an `ALLOC_PD` command, executes it with `mlx5_cmd_exec_inout()`, and returns the firmware `pd` field through `pdn` on success. `mlx5_core_dealloc_pd()` builds a `DEALLOC_PD` command with the caller's PD number and sends it with `mlx5_cmd_exec_in()`. Both functions are exported with `EXPORT_SYMBOL`, so in-kernel mlx5 consumers outside this compilation unit can use them.

## Control Flow

There is no local state machine. Callers allocate a PD before creating dependent firmware objects and must later deallocate it after those users are destroyed. Errors propagate directly from the command interface.

## State and Persistence Behavior

State is persisted in firmware as an allocated PD handle. This file does not cache handles or refcounts; ownership is entirely caller-managed. A successful allocation mutates only the caller-provided `pdn`.

## Dependencies and Integration Points

The file depends on command opcodes and layout macros from the mlx5 interface headers and on the core command executor. It integrates with RDMA, steering, transport, and other mlx5 modules that require a PD number.

## Risks and Test Signals

The main risk is caller misuse: leaking a PD on partial setup failure or deallocating while dependent objects still exist. Tests should include command-failure fault injection, create/destroy loops for PD consumers, and teardown ordering checks during driver unload and reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/pd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/port.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/port.c

## Purpose

`port.c` is the mlx5 port-register service layer. It wraps `ACCESS_REG` and several direct command opcodes to query and configure physical port capabilities, link state, MTU, module EEPROM, pause/PFC/DCB/ETS, Wake-on-LAN, FCS checking, PTP pins, trust/DSCP mappings, and link-speed interpretation.

## Important APIs, Types, and Functions

The foundational API is `mlx5_access_reg()`, exported as `mlx5_core_access_reg()`, which packages caller-supplied register payloads into `ACCESS_REG` command buffers. Higher-level register wrappers include `mlx5_query_pcam_reg()`, `mlx5_query_mcam_reg()`, `mlx5_query_qcam_reg()`, `mlx5_set_port_caps()`, `mlx5_query_port_ptys()`, `mlx5_set_port_beacon()`, admin status setters/getters, MTU queries/setters, EEPROM readers, pause/PFC/stall watermark routines, DCBX and ETS routines, port check/FCS helpers, MTPPS/MTPPSE pin access, trust state access, buffer ownership query, DSCP-to-priority mapping, and link speed helpers.

Important local data includes `struct mlx5_reg_pcap`, `mlx5e_link_info[]`, and `mlx5e_ext_link_info[]`, which map PTYS protocol bits to speed/lane tuples for legacy and extended link modes.

## Control Flow

Most functions are one-shot register transactions: populate the register-specific input struct, call `mlx5_core_access_reg()` with read or write mode, then extract fields from output. EEPROM reads have more logic: `mlx5_query_module_eeprom()` obtains the module number from PMLP, reads module ID via MCIA, translates SFP/QSFP offsets into I2C address/page/offset, clamps cross-page reads, and calls `mlx5_query_mcia()`. DSCP update reads the whole QPDPM table, copies it back to input, modifies one entry, and writes the table.

DCB/ETS helpers loop over traffic classes or priorities and program QTCT/QETCR fields. Link speed queries choose the extended PTYS table if supported, then scan capability or operational bitmasks and return the maximum matching speed.

## State and Persistence Behavior

This file does not cache port state. Successful writes persist in firmware/hardware registers: admin status, MTU, pause/PFC, ETS bandwidth and rate limits, DCBX parameters, FCS behavior, PTP pin events, trust state, and DSCP priority mappings. Query helpers return snapshots. `mlx5_toggle_port_link()` temporarily transitions admin status down and restores it if it was up, forcing hardware to apply newly set port registers.

## Dependencies and Integration Points

Dependencies are the mlx5 command executor, register layout macros, Ethernet/IB port constants, PCI/module EEPROM definitions, and exported mlx5 port APIs consumed by mlx5e, RDMA, devlink/ethtool, DCB, PTP, and eswitch paths. Several helpers gate behavior on capability bits such as PCAM, MCAM, PTYS extended Ethernet, ETS, ports check, and MCIA 32-dword support.

## Risks and Edge Cases

Several query wrappers ignore command errors by design or return default fallback values, such as FCS support defaults when PCMR is unavailable. `mlx5_query_mtppse()` appears to read `event_arm` and `event_generation_mode` from the input buffer after the access call rather than from output; that should be verified against local kernel expectations. EEPROM reads must not cross pages incorrectly, and MCIA size depends on capability. DCB arrays assume caller-provided buffers cover all supported traffic classes or 64 DSCP entries.

## Test Signals

Useful tests include ethtool link-mode reporting on legacy and extended PTYS devices, MTU set/query loops, SFP/QSFP EEPROM reads across low/high pages, DCB/PFC/ETS configuration through `dcbnl`, DSCP mapping changes, PTP pin arm/query, FCS toggling on devices with and without PCMR, and fault injection for `ACCESS_REG` allocation and command failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/port.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.c

## Purpose

`qos.c` is the NIC QoS scheduling-element helper layer. It checks whether NIC SQ scheduling, bandwidth sharing, and rate limit capabilities are present, then creates, updates, and destroys root, inner, and leaf QoS nodes in the firmware scheduling hierarchy.

## Important APIs, Types, and Functions

The public helpers are `mlx5_qos_is_supported()`, `mlx5_qos_max_leaf_nodes()`, `mlx5_qos_create_leaf_node()`, `mlx5_qos_create_inner_node()`, `mlx5_qos_create_root_node()`, `mlx5_qos_update_node()`, and `mlx5_qos_destroy_node()`. Leaf nodes are firmware `QUEUE_GROUP` elements. Inner/root nodes are `TSAR` elements configured as DWRR. All operations use scheduling command wrappers from `rl.c`.

## Control Flow

Creation validates support for the desired element type and, for inner nodes, DWRR TSAR support. It fills a `scheduling_context` with parent id, element type, bandwidth share, and max average bandwidth, adds TSAR attributes for DWRR when needed, and calls `mlx5_create_scheduling_element_cmd()` in `SCHEDULING_HIERARCHY_NIC`. Update builds a context containing only bandwidth fields and passes a modify bitmask for `BW_SHARE` and `MAX_AVERAGE_BW`. Destroy calls the destroy scheduling command.

## State and Persistence Behavior

State is held by firmware scheduling elements identified by returned IDs. This file does not keep a local tree or reference counts, so callers own node lifetime, hierarchy ordering, and rollback.

## Dependencies and Integration Points

It depends on QoS capability macros, scheduling context layouts, and command wrappers in `rl.c`. It is used by higher-level mlx5e QoS and traffic-class code to build NIC queue group trees.

## Risks and Test Signals

Risks are mostly capability mismatches and caller-managed hierarchy leaks. Tests should cover devices without each QoS capability, root/inner/leaf create and destroy ordering, bandwidth update propagation, max leaf count from `log_max_qos_nic_queue_group`, and firmware errors during partial tree setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.h

## Purpose

`qos.h` declares the mlx5 NIC QoS scheduling helper API and provides QoS-specific logging macros. It is the private interface consumed by mlx5e QoS users and implemented by `qos.c`.

## Important APIs, Types, and Functions

The header defines `MLX5_DEBUG_QOS_MASK` and wrappers `qos_err()`, `qos_warn()`, and `qos_dbg()`. It declares support/query helpers and node lifecycle functions: `mlx5_qos_is_supported()`, `mlx5_qos_max_leaf_nodes()`, `mlx5_qos_create_leaf_node()`, `mlx5_qos_create_inner_node()`, `mlx5_qos_create_root_node()`, `mlx5_qos_update_node()`, and `mlx5_qos_destroy_node()`.

## Control Flow and State

The header has no control flow or storage. Its function contracts are stateful because they create, update, and destroy firmware scheduling elements. Callers must keep returned IDs and destroy them in dependency order.

## Dependencies and Integration Points

It includes `mlx5_core.h` for `struct mlx5_core_dev` and firmware constants. The implementation depends on scheduling command helpers and QoS capability macros.

## Risks and Test Signals

Prototype drift between `qos.h` and `qos.c` is the main header-level risk. Build coverage should include mlx5e QoS users under configs where QoS is enabled and disabled, and logging should preserve the `QoS:` prefix for diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/qos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.c

## Purpose

`rdma.c` enables and disables the default RoCE support needed by mlx5 when eswitch/RDMA steering is available. It programs the NIC vport RoCE state, installs a default RoCE GID derived from the MAC address, and creates an RDMA RX flow table that allows traffic from the eswitch manager source port.

## Important APIs, Types, and Functions

Public functions are `mlx5_rdma_enable_roce()` and `mlx5_rdma_disable_roce()`. Local helpers are `mlx5_rdma_enable_roce_steering()`, `mlx5_rdma_disable_roce_steering()`, `mlx5_rdma_make_default_gid()`, `mlx5_rdma_add_roce_addr()`, and `mlx5_rdma_del_roce_addr()`. Persistent objects are stored in `dev->priv.roce`: flow table, flow group, and allow rule.

## Control Flow

Enable first checks the generic RoCE capability. It enables RoCE on the NIC vport, constructs and installs a default link-local GID, then creates steering objects. Steering validates RDMA RX flow-table capabilities, allocates flow-group input and flow spec buffers, gets the RDMA RX kernel namespace, creates a one-entry flow table, creates a flow group scoped to source port, and adds an allow rule matching the eswitch manager vport. Any failure unwinds in reverse: destroy flow group/table, delete GID, disable vport RoCE.

Disable is idempotent on `roce->ft`: if steering was not created, it returns. Otherwise it deletes the allow rule, flow group, and flow table, removes the GID, and disables NIC vport RoCE.

## State and Persistence Behavior

Firmware state includes the vport RoCE enable bit, GID table entry 0 for RoCE v2, and RDMA RX flow-table objects. The driver caches the flow objects in `dev->priv.roce` but does not explicitly clear the pointers after destroy in this file, so higher-level lifecycle must prevent double-disable after the objects are destroyed or rely on object memory being cleared elsewhere.

## Dependencies and Integration Points

It depends on `CONFIG_MLX5_ESWITCH`, RDMA verbs `union ib_gid`, IPv6 EUI-48 address construction, vport RoCE helpers, flow steering APIs, and eswitch source-port match helpers. `rdma.h` compiles the API to no-ops when eswitch support is absent.

## Risks and Test Signals

Risk centers on partial enable cleanup and idempotency. Test RoCE enable/disable during probe, unload, eswitch mode changes, and firmware capability absence. Validate GID entry programming, RDMA RX namespace creation, source-port filtering, and that traffic from non-manager ports is not unintentionally allowed. Fault injection should cover namespace, table, group, rule, and GID programming failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.h

## Purpose

`rdma.h` exposes the mlx5 RoCE enable/disable hooks to the core driver while hiding the implementation behind `CONFIG_MLX5_ESWITCH`.

## Important APIs and Control Flow

When eswitch support is enabled, it declares `mlx5_rdma_enable_roce()` and `mlx5_rdma_disable_roce()` from `rdma.c`. Otherwise it provides inline stubs: enable returns success and disable is empty. This lets callers sequence RDMA setup unconditionally without scattering Kconfig checks.

## State and Dependencies

The header includes `mlx5_core.h` and has no storage. In enabled builds, calls mutate vport RoCE, GID, and flow steering state. In disabled builds, no state is changed.

## Risks and Test Signals

The main risk is assuming RoCE was actually enabled in non-eswitch builds because the stub returns 0. Compile both Kconfig paths and exercise callers that depend on RoCE availability checks separately from this helper's success code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rl.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rl.c

## Purpose

`rl.c` provides two related services: generic firmware scheduling-element command wrappers used by QoS/eswitch code, and a lazy, refcounted packet-pacing rate-limit table used to share hardware rate-limit entries among consumers.

## Important APIs, Types, and Functions

Scheduling capability helpers are `mlx5_qos_tsar_type_supported()` and `mlx5_qos_element_type_supported()`. Firmware command wrappers are `mlx5_create_scheduling_element_cmd()`, `mlx5_modify_scheduling_element_cmd()`, and `mlx5_destroy_scheduling_element_cmd()`.

Rate-limit APIs are `mlx5_init_rl_table()`, `mlx5_cleanup_rl_table()`, `mlx5_rl_is_in_range()`, `mlx5_rl_are_equal()`, `mlx5_rl_add_rate()`, `mlx5_rl_remove_rate()`, `mlx5_rl_add_rate_raw()`, and `mlx5_rl_remove_rate_raw()`. The table is `dev->priv.rl_table`, with `rl_lock`, `max_size`, `min_rate`, `max_rate`, lazy `rl_entry[]`, and a table refcount. Each `mlx5_rl_entry` has a hardware index, raw context bytes, UID, dedicated flag, and per-entry refcount.

## Control Flow

Initialization checks QoS and packet pacing capabilities, initializes the mutex, and records table size/rate range from capabilities. The actual entry array is allocated lazily in `mlx5_rl_table_get()` on first rate addition and freed by `mlx5_rl_table_put()` when the table refcount falls to zero.

Adding a rate validates table support and range, locks `rl_lock`, allocates the table if needed, then calls `find_rl_entry()`. Shared entries reuse an existing non-dedicated entry with identical raw context and UID; dedicated entries take the first free slot. New entries are programmed with `SET_PP_RATE_LIMIT`, marked dedicated if requested, refcounted, and returned as a 1-based hardware index. Removal decrements the entry refcount and, when it reaches zero, sends `SET_PP_RATE_LIMIT` without context to clear the hardware entry. Cleanup clears every configured entry and frees the array.

## State and Persistence Behavior

Hardware state is the packet pacing rate-limit table, whose index 0 is reserved for unlimited rate and whose usable entries are represented as indexes 1..max_size. Driver state persists only while references exist unless cleanup forces clear. The table refcount tracks active users, while each entry refcount tracks consumers of identical or dedicated rates.

## Dependencies and Integration Points

The code depends on QoS capabilities, scheduling command layouts, packet pacing UID support, and the core command executor. It is integrated with QoS, flow/transport objects that need packet pacing, and exported symbol consumers.

## Risks and Edge Cases

`mlx5_rl_remove_rate_raw()` indexes `table->rl_entry[index - 1]` without local range checks, so callers must pass an index returned from add. `mlx5_rl_remove_rate()` calls `find_rl_entry()` without first ensuring `rl_entry` is non-NULL; it is safe only under the contract that remove follows a successful add while the table still exists. Lazy table refcounting must stay balanced across every add failure and remove path. Dedicated entries intentionally do not deduplicate, so capacity exhaustion is possible even with repeated identical rates.

## Test Signals

Test no-packet-pacing capability, invalid zero/out-of-range rates, shared duplicate add/remove refcounts, dedicated entry exhaustion, UID-capable and UID-less devices, cleanup with live entries, and fault injection for `SET_PP_RATE_LIMIT`. Observe firmware table clearing and that `max_size` excludes reserved index 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/rl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/cmd.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/cmd.c

## Purpose

`sf/cmd.c` is the low-level command wrapper file for mlx5 subfunctions. It allocates/deallocates SF firmware function IDs and enables/disables the HCA for a specific SF function.

## Important APIs and Control Flow

`mlx5_cmd_alloc_sf()` sends `ALLOC_SF` with a function id. `mlx5_cmd_dealloc_sf()` sends `DEALLOC_SF`. `mlx5_cmd_sf_enable_hca()` sends `ENABLE_HCA` with `embedded_cpu_function` cleared and the SF function id. `mlx5_cmd_sf_disable_hca()` sends `DISABLE_HCA` similarly. All functions use fixed-size command buffers and return command executor status directly.

## State and Persistence Behavior

Successful commands mutate firmware SF allocation and HCA state. This file stores no local state, so higher-level SF tables own function id selection, software-to-hardware mapping, deferred free, and state transitions.

## Dependencies and Integration Points

It depends on `priv.h` declarations and the mlx5 command interface. `sf/hw_table.c` uses alloc/dealloc and `sf/devlink.c` uses enable/disable during devlink port function state changes.

## Risks and Test Signals

The wrappers are thin, so most risk is misuse by callers. One detail to verify is that `mlx5_cmd_sf_disable_hca()` sets `embedded_cpu_function` using the `enable_hca_in` macro name on the disable input buffer; if layouts diverge, this could become wrong. Tests should cover SF create/delete, active/inactive transitions, command-failure rollback, and EC-function platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.c

## Purpose

`sf/dev/dev.c` discovers active mlx5 subfunctions and represents each active SF as a Linux auxiliary device. It listens for VHCA state events, creates/removes auxiliary devices as SFs become active or inactive, and probes externally created active SFs during table creation.

## Important APIs, Types, and Functions

The main private type is `struct mlx5_sf_dev_table`, containing an xarray of `mlx5_sf_dev` objects indexed by SF index, BAR base/length information, optional active-scan workqueue, a stop flag, and the parent core device. `struct mlx5_sf_dev_active_work_ctx` carries queried active-state data to per-function VHCA workqueues.

Public functions are `mlx5_sf_dev_allocated()`, `mlx5_sf_dev_notifier_init()`, `mlx5_sf_dev_table_create()`, `mlx5_sf_dev_notifier_cleanup()`, and `mlx5_sf_dev_table_destroy()`. Local helpers create and remove auxiliary devices, arm VHCA events for every SF function, scan active SFs, and handle state-change notifications.

## Control Flow

Table creation checks `sf` and VHCA-event support, allocates a table, computes each SF BAR length from `log_min_sf_size`, records BAR2 base, initializes the device xarray, optionally starts an active-SF scan workqueue for non-eswitch-manager devices, and arms VHCA change events for all local SF function IDs. Active-scan work queries every function's VHCA state and, for active entries, queues add work onto a VHCA event worker selected by function id modulo `MLX5_DEV_MAX_WQS`.

Runtime state changes enter `mlx5_sf_dev_state_change_handler()`. It filters function IDs into the SF range, maps function ID to xarray index, and deletes devices for INVALID, ALLOCATED, or TEARDOWN_REQUEST states. For ACTIVE, it creates an auxiliary device if one does not already exist. Creation allocates an auxiliary id, fills `struct mlx5_sf_dev` with parent mdev, function id, SF number, and BAR base, initializes and adds the auxiliary device, then stores it in the xarray. Removal erases the xarray entry, deletes the auxiliary device, and uninitializes it so the release callback frees memory and auxiliary id.

## State and Persistence Behavior

Driver state is `dev->priv.sf_dev_table`, its xarray of auxiliary devices, each `mlx5_sf_dev`'s parent pointer, function id, SF number, auxiliary id, and BAR address. Firmware state is only observed via VHCA query/events and event arming. The table destroy path stops active scanning, removes all auxiliary devices after notifiers are cleaned up, warns if the xarray remains non-empty, and clears the priv pointer.

## Dependencies and Integration Points

The file depends on VHCA event APIs, auxiliary bus APIs, PCI BAR resources, SF capability helpers, ECPF/eswitch-manager tests, tracepoints in `dev_tracepoint.h`, and the auxiliary driver implemented in `sf/dev/driver.c`. It also relies on `mlx5_vhca_events_work_enqueue()` ordering to serialize add work per function hash.

## Risks and Edge Cases

There is an acknowledged race between querying an externally active SF and the SF becoming inactive before probe completes; the code accepts that probe may later fail or be removed after init. `mlx5_sf_dev_add()` stores the auxiliary device in the xarray only after `auxiliary_device_add()`, so a very early state event could observe no device and attempt another add. Destroy must run after notifier cleanup to avoid event/remove races. Failure after `auxiliary_device_add()` but before xarray insert calls remove/uninit, which should trigger proper release.

## Test Signals

Test local and external SF creation, active-state scan with many SFs, VHCA active/allocated/teardown events, auxiliary device sysfs `sfnum`, BAR address calculation, table destroy with live devices, and repeated SF enable/disable under lockdep/KASAN. Tracepoints `mlx5_sf_dev_add` and `mlx5_sf_dev_del` should match xarray contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.h

## Purpose

`sf/dev/dev.h` declares the auxiliary-device representation of an mlx5 subfunction and the lifecycle hooks for SF device discovery and the SF auxiliary driver.

## Important APIs and Types

When `CONFIG_MLX5_SF` is enabled, `struct mlx5_sf_dev` embeds `struct auxiliary_device` and stores parent mdev, child mdev, SF BAR base, user SF number, and hardware function id. `struct mlx5_sf_peer_devlink_event_ctx` carries function id, devlink pointer, and error status for parent/peer devlink association. The header declares notifier/table lifecycle functions, driver register/unregister functions, and `mlx5_sf_dev_allocated()`.

When SF support is disabled, all lifecycle functions become no-ops, registration returns success, and `mlx5_sf_dev_allocated()` returns false.

## State, Dependencies, and Integration

The header depends on `linux/auxiliary_bus.h` in enabled builds and bridges `sf/dev/dev.c`, `sf/dev/driver.c`, and parent SF/devlink code. State is in the concrete structs owned by the implementation.

## Risks and Test Signals

Callers must tolerate the no-op stub behavior in non-SF builds. Compile both Kconfig paths and verify that `MLX5_SF_DEV_ID_NAME` matches the auxiliary driver id table and generated device names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/diag/dev_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/diag/dev_tracepoint.h

## Purpose

`sf/dev/diag/dev_tracepoint.h` defines tracepoints for SF auxiliary device creation and deletion. It provides observability for the SF device table in `sf/dev/dev.c`.

## Important APIs and Control Flow

The file declares an event class `mlx5_sf_dev_template` with fields for parent device name, SF device pointer, auxiliary id, hardware function id, and SF number. It then defines `mlx5_sf_dev_add` and `mlx5_sf_dev_del` events from that class. The trace include path/file footer enables Linux tracepoint code generation when included with `CREATE_TRACE_POINTS`.

## State and Dependencies

Tracepoints do not mutate driver state. They depend on Linux tracepoint infrastructure, `struct mlx5_core_dev`, and `struct mlx5_sf_dev`. The fast assignment reads `dev_name(dev->device)`, `sfdev->fn_id`, and `sfdev->sfnum`.

## Risks and Test Signals

The header must remain include-guarded for multi-read trace generation and the relative include path to `dev.h` must match the source tree. Test by enabling ftrace/perf trace events and confirming add/delete events fire with matching auxiliary ids and function ids during SF activation and teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/diag/dev_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/driver.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/driver.c

## Purpose

`sf/dev/driver.c` is the auxiliary bus driver for mlx5 subfunction devices. It turns an `mlx5_sf_dev` auxiliary device into a child `mlx5_core_dev`, maps the SF BAR, links peer devlink state to the parent SF devlink port, and runs the normal or lightweight mlx5 probe path.

## Important APIs and Functions

The auxiliary driver callbacks are `mlx5_sf_dev_probe()`, `mlx5_sf_dev_remove()`, and `mlx5_sf_dev_shutdown()`, registered by `mlx5_sf_driver_register()` and unregistered by `mlx5_sf_driver_unregister()`. `mlx5_core_peer_devlink_set()` notifies the parent mdev with `MLX5_DRIVER_EVENT_SF_PEER_DEVLINK` so the parent devlink port can point to the child devlink.

## Control Flow

Probe allocates a devlink/core device, initializes core fields from the parent SF device, marks local eswitch-manager SFs as lightweight, initializes the mlx5 mdev profile, ioremaps the SF BAR segment, sets peer devlink before registration, then calls `mlx5_init_one_light()` for local lightweight SFs or `mlx5_init_one()` for externally managed SFs. On success it initializes VHCA debugfs. Every error path unwinds in reverse.

Remove sets `MLX5_BREAK_FW_WAIT`, drains the health workqueue, runs light or full uninit, unmaps BAR, uninitializes mdev, and frees devlink. Shutdown similarly breaks firmware waits, drains health work, and unloads the device without freeing all probe objects.

## State and Persistence Behavior

The driver stores the child mdev pointer in `sf_dev->mdev`; the child mdev records the parent mdev, auxiliary index, PCI device, BAR address, coredev type `MLX5_COREDEV_SF`, and possibly lightweight mode. Firmware/device state is established by the ordinary mlx5 init path.

## Dependencies and Integration Points

It integrates with the Linux auxiliary bus, mlx5 devlink allocation, mdev init/uninit, health workqueue, ESwitch manager detection, peer devlink notifier in `sf/devlink.c`, and VHCA debugfs.

## Risks and Test Signals

Peer devlink setup must happen before child devlink registration, so notifier failures abort probe. Remove assumes `sf_dev->mdev` is valid after successful probe; partial probe failures must not leave it exposed. Test local lightweight SFs, external full SFs, probe failure at mdev init, ioremap, peer devlink, and init-one stages, plus shutdown during firmware wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/dev/driver.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/devlink.c

## Purpose

`sf/devlink.c` implements devlink PCI SF port management for mlx5. It creates and deletes SF devlink ports, maps user SF numbers to hardware function IDs, activates/deactivates SF HCAs through devlink port function state, updates operational state from VHCA events, and cleans up SFs when eswitch mode changes.

## Important APIs, Types, and Functions

`struct mlx5_sf` is the per-devlink-port object: it embeds `struct mlx5_devlink_port`, stores devlink port index, controller, software table id, hardware function id, and cached VHCA state. `struct mlx5_sf_table` holds the parent device, xarray lookup by hardware function id, and `sf_state_lock`.

Public devlink operations are `mlx5_devlink_sf_port_new()`, `mlx5_devlink_sf_port_del()`, `mlx5_devlink_sf_port_fn_state_get()`, and `mlx5_devlink_sf_port_fn_state_set()`. Lifecycle functions are `mlx5_sf_notifiers_init()`, `mlx5_sf_table_init()`, `mlx5_sf_notifiers_cleanup()`, `mlx5_sf_table_cleanup()`, and `mlx5_sf_table_empty()`.

## Control Flow

New-port validation requires `DEVLINK_PORT_FLAVOUR_PCI_SF`, no user-selected port index, a valid user `sfnum`, valid controller support, correct PF number, SF hardware table support, and switchdev eswitch mode. Allocation uses `mlx5_sf_hw_table_sf_alloc()` to reserve a software id and firmware function, converts it to a hardware function id, derives a devlink port index, inserts the object into the xarray, and loads the eswitch SF vport. Delete unloads the eswitch vport and deallocates the SF.

Function state set is serialized by `sf_state_lock`. ACTIVE enables the SF HCA, optionally sets default max IO EQs on the devlink port, and moves cached state to ACTIVE. INACTIVE disables the HCA and changes cached state to TEARDOWN_REQUEST. VHCA events update cached state only for valid transitions: ACTIVE<->IN_USE and TEARDOWN_REQUEST->ALLOCATED. Deallocation frees immediately if the hardware state is still ALLOCATED; otherwise it requests disable if needed and calls deferred hardware-table free so the function id is recycled only after firmware reports ALLOCATED.

The file registers notifiers for eswitch mode changes, VHCA events, and parent mdev peer-devlink events. Legacy eswitch mode deletes all SF ports. Peer-devlink events attach the child SF devlink to the parent devlink port.

## State and Persistence Behavior

Driver state is `dev->priv.sf_table`, the xarray by function id, each `mlx5_sf` object, vport `max_eqs_set`, and cached hardware state. Firmware state includes allocated SF function IDs, HCA enable/disable, VHCA state, and eswitch vports. Devlink state includes PCI SF ports, function state/opstate, and child peer devlink linkage.

## Dependencies and Integration Points

Dependencies include devlink port APIs, mlx5 eswitch load/unload, SF hardware table APIs, VHCA event APIs, SF command wrappers, max IO EQ devlink helpers, notifier chains, and SF tracepoints. It is the main user-facing integration point for `devlink port add/del` and `devlink port function set state`.

## Risks and Edge Cases

State transitions are asynchronous and split between user commands and firmware events; missing or delayed VHCA events leave entries pending deferred free. Deleting an ACTIVE SF treats it as possibly IN_USE and always waits for firmware confirmation before recycling the id. On eswitch legacy transition, `mlx5_sf_del_all()` iterates the xarray while deleting entries, which relies on xarray iteration semantics and deletion safety. Peer devlink notifier returns `NOTIFY_DONE` when no SF is found, so child probe can proceed without peer linkage if ordering is wrong.

## Test Signals

Run devlink SF add/delete with duplicate `sfnum`, invalid controller, invalid PF, and non-switchdev mode. Test ACTIVE, INACTIVE, IN_USE, and teardown transitions with child driver attached. Verify deferred free after child detach, eswitch legacy cleanup, peer devlink association, max IO EQ default programming, and tracepoints for add/free/activate/deactivate/update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/sf_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/sf_tracepoint.h

## Purpose

`sf/diag/sf_tracepoint.h` defines tracepoints for mlx5 SF devlink and hardware-table operations. It provides visibility into SF allocation, free, deferred free, activation, deactivation, and VHCA state updates.

## Important APIs and Control Flow

Events include `mlx5_sf_add`, `mlx5_sf_free`, `mlx5_sf_hwc_alloc`, `mlx5_sf_hwc_free`, `mlx5_sf_hwc_deferred_free`, `mlx5_sf_activate`, `mlx5_sf_deactivate`, and `mlx5_sf_update_state`. A shared event class is used for activate/deactivate style state events. Each event captures device name and relevant identifiers such as port index, controller, hardware function id, SF number, or state.

## State and Dependencies

The tracepoints are observational only. They depend on Linux tracepoint infrastructure, `struct mlx5_core_dev`, and the SF VHCA event type. The footer sets `TRACE_INCLUDE_PATH` to `sf/diag` and `TRACE_INCLUDE_FILE` to `sf_tracepoint`.

## Risks and Test Signals

Tracepoint field names must match the data passed by `sf/devlink.c` and `sf/hw_table.c`. Test by enabling mlx5 SF trace events while running devlink SF lifecycle commands and confirming hardware IDs and user SF numbers correlate with devlink output and firmware events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/sf_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/vhca_tracepoint.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/vhca_tracepoint.h

## Purpose

`sf/diag/vhca_tracepoint.h` defines the tracepoint emitted when an mlx5 VHCA state event is queried, rearmed, and fanned out.

## Important APIs and Control Flow

The single `TRACE_EVENT(mlx5_sf_vhca_event)` records device name, hardware function id, software SF number, and new VHCA state from `struct mlx5_vhca_state_event`. It is used by `vhca_event.c` after querying firmware state and before notifying subscribers.

## State and Dependencies

The tracepoint does not change state. It depends on Linux tracepoint infrastructure, `struct mlx5_core_dev`, and `struct mlx5_vhca_state_event`. The include footer points trace generation to `sf/diag/vhca_tracepoint`.

## Risks and Test Signals

If event fields diverge from `struct mlx5_vhca_state_event`, trace output will become misleading. Validate with ftrace/perf during SF active, in-use, teardown, and allocated transitions, and compare with devlink function opstate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/diag/vhca_tracepoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/hw_table.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/hw_table.c

## Purpose

`sf/hw_table.c` owns mlx5 SF hardware-function-id allocation. It maps user SF numbers to software indexes and firmware function IDs for local and external controllers, registers devlink resources that expose maximum SF capacity, allocates/deallocates SFs in firmware, and handles deferred recycling after VHCA detach events.

## Important APIs, Types, and Functions

`struct mlx5_sf_hw` records user SF number, allocation state, and pending-delete state for one software slot. `struct mlx5_sf_hwc_table` stores the per-controller slot array, max function count, and base hardware function id. `struct mlx5_sf_hw_table` wraps local and external controller tables with `table_lock`.

Public functions are `mlx5_sf_sw_to_hw_id()`, `mlx5_sf_hw_table_sf_alloc()`, `mlx5_sf_hw_table_sf_free()`, `mlx5_sf_hw_table_sf_deferred_free()`, `mlx5_sf_hw_table_init()`, `mlx5_sf_hw_table_cleanup()`, `mlx5_sf_hw_notifier_init()`, `mlx5_sf_hw_notifier_cleanup()`, `mlx5_sf_hw_table_destroy()`, and `mlx5_sf_hw_table_supported()`.

## Control Flow

Initialization requires VHCA event support, queries local max SFs and external HPF SF capacity/base id, registers devlink resources `max_local_SFs` and `max_external_SFs`, allocates the table, initializes local/external slot arrays, and stores it in `dev->priv.sf_hw_table`. Allocation locks the table, finds a free software slot while rejecting duplicate user `sfnum`, computes the hardware function id, sends `ALLOC_SF`, writes the software function id with `mlx5_modify_vhca_sw_id()`, arms VHCA events for external-controller SFs, traces allocation, and returns the software id.

Immediate free locks, computes hardware id, sends `DEALLOC_SF`, and clears slot state. Deferred free queries VHCA state; if already ALLOCATED, it deallocates immediately and clears allocation, otherwise it marks `pending_delete`. The VHCA notifier listens for ALLOCATED events, maps function id back to the right controller table and software id, and deallocates any allocated slot marked pending delete. Destroy force-deallocates all still allocated local and external SFs, covering missed firmware events.

## State and Persistence Behavior

Driver state is `dev->priv.sf_hw_table`, slot arrays, allocation bits, user SF numbers, and pending-delete bits. Firmware state is the allocated SF function, its software id, event arm state, and eventual VHCA state. Devlink resource registration persists visible max-SF capacities until cleanup unregisters resources.

## Dependencies and Integration Points

The file depends on SF command wrappers, VHCA event/query/arm helpers, eswitch external controller capacity query, devlink resource APIs, SF tracepoints, and `mlx5_sf_devlink.c` as the primary allocator user.

## Risks and Edge Cases

Duplicate detection is per controller table, so the same user SF number may be valid on separate controller domains. Deferred free relies on receiving a later ALLOCATED event; `mlx5_sf_hw_table_destroy()` is the safety net for missed events. `mlx5_sf_hw_table_sf_deferred_free()` ignores query errors except for unlocking, leaving state unchanged; repeated delete/retry behavior should be checked. Devlink resource registration failure is logged but not fatal, so management visibility may be missing even when SFs work.

## Test Signals

Test allocation until local and external tables are full, duplicate `sfnum`, command failure rollback after `ALLOC_SF` and `MODIFY_VHCA_STATE`, deferred free while SF is IN_USE, ALLOCATED event recycling, destroy with pending slots, and devlink resource presence. Tracepoints should show alloc, deferred free, and final free with matching hardware ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/hw_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/mlx5_ifc_vhca_event.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/mlx5_ifc_vhca_event.h

## Purpose

`sf/mlx5_ifc_vhca_event.h` defines firmware interface layouts for querying and modifying VHCA state. It is the local IFC extension used by SF/VHCA event code.

## Important APIs and Types

`enum mlx5_ifc_vhca_state` defines firmware states: INVALID, ALLOCATED, ACTIVE, IN_USE, and TEARDOWN_REQUEST. `struct mlx5_ifc_vhca_state_context_bits` contains `arm_change_event`, `vhca_state`, and `sw_function_id`. Query and modify command input/output bit structs define opcode, UID, op_mod, embedded CPU flag, function id, field select bits, and the state context.

## Control Flow and State

The header has no executable flow. Its bit layouts are consumed by `vhca_event.c`, `sf/hw_table.c`, and `sf/devlink.c` via `MLX5_SET()`/`MLX5_GET()` macros to arm events, read states, and set user-visible software function ids.

## Dependencies and Integration Points

It is tightly coupled to firmware command opcodes `QUERY_VHCA_STATE` and `MODIFY_VHCA_STATE`. It integrates with devlink SF state, hardware table deferred free, and auxiliary SF device discovery.

## Risks and Test Signals

Any mismatch with firmware layout would corrupt event arming or state decoding. Validate by querying all expected states on real firmware, checking `sw_function_id` round trips after allocation, and ensuring field select bits modify only intended fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/mlx5_ifc_vhca_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/priv.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/priv.h

## Purpose

`sf/priv.h` is the private cross-file interface for mlx5 SF management. It declares command wrappers, software-to-hardware id translation, and hardware table allocation/free helpers used inside the SF subsystem.

## Important APIs

Declarations include `mlx5_cmd_alloc_sf()`, `mlx5_cmd_dealloc_sf()`, `mlx5_cmd_sf_enable_hca()`, `mlx5_cmd_sf_disable_hca()`, `mlx5_sf_sw_to_hw_id()`, `mlx5_sf_hw_table_sf_alloc()`, `mlx5_sf_hw_table_sf_free()`, `mlx5_sf_hw_table_sf_deferred_free()`, and `mlx5_sf_hw_table_supported()`.

## Control Flow, State, and Dependencies

The header has no logic or storage. The declared functions mutate firmware SF allocation/HCA state and driver hardware-table state in `dev->priv.sf_hw_table`. It depends on `linux/mlx5/driver.h` for `struct mlx5_core_dev`.

## Risks and Test Signals

Because this is an internal header, risks are prototype drift and accidental use outside intended SF layering. Build coverage should ensure `cmd.c`, `hw_table.c`, and `devlink.c` remain synchronized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/sf.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/sf.h

## Purpose

`sf/sf.h` is the public internal SF manager header for mlx5 core. It declares SF hardware-table, notifier, table, and devlink port operations, with no-op stubs when `CONFIG_MLX5_SF_MANAGER` is disabled.

## Important APIs

Enabled declarations include hardware table init/cleanup/destroy and notifier init/cleanup, SF devlink table init/cleanup/notifiers, `mlx5_sf_table_empty()`, and devlink PCI SF operations for port add/delete and function state get/set. Disabled builds provide stubs for lifecycle and table-empty helpers; devlink operation prototypes are omitted because callers are normally Kconfig-gated.

## Control Flow and State

The header has no direct flow. The declared functions manage `dev->priv.sf_hw_table`, `dev->priv.sf_table`, VHCA/eswitch/blocking notifiers, and devlink SF ports.

## Dependencies and Integration Points

It includes `linux/mlx5/driver.h` and `lib/sf.h`. It is consumed by mlx5 core probe/cleanup and devlink operations that need SF manager support.

## Risks and Test Signals

Callers must not assume SF manager support when stubs are compiled. Compile both Kconfig paths, verify no unresolved devlink SF operation references in disabled builds, and test lifecycle ordering around notifiers and table cleanup in enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/sf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.c

## Purpose

`sf/vhca_event.c` provides VHCA state event infrastructure for mlx5 SF management. It enables VHCA state event capabilities, creates per-bucket workqueues, handles EQ state-change events, queries full state from firmware, rearms events, traces them, and fans them out to blocking notifier subscribers.

## Important APIs, Types, and Functions

Private types are `struct mlx5_vhca_event_work`, carrying a function id event into process context, `struct mlx5_vhca_event_handler`, owning one workqueue, and `struct mlx5_vhca_events`, grouping `MLX5_DEV_MAX_WQS` handlers. Public functions include `mlx5_cmd_query_vhca_state()`, `mlx5_modify_vhca_sw_id()`, `mlx5_vhca_event_arm()`, `mlx5_vhca_state_cap_handle()`, `mlx5_vhca_state_notifier_init()`, `mlx5_vhca_event_init()`, `mlx5_vhca_event_cleanup()`, `mlx5_vhca_event_start()`, `mlx5_vhca_event_stop()`, `mlx5_vhca_event_notifier_register()`, `mlx5_vhca_event_notifier_unregister()`, `mlx5_vhca_events_work_enqueue()`, and `mlx5_vhca_event_work_queues_flush()`.

## Control Flow

Initialization sets up a blocking notifier head and an EQ notifier for `VHCA_STATE_CHANGE`, then `mlx5_vhca_event_init()` allocates a `vhca_events` object and creates multiple single-threaded workqueues. Start registers the EQ notifier. When an EQ event arrives, `mlx5_vhca_state_change_notifier()` allocates a work item with `GFP_ATOMIC`, records the function id, chooses a workqueue by function id modulo `MLX5_DEV_MAX_WQS`, and queues it.

The work handler calls `mlx5_vhca_event_notify()`, which queries the current VHCA state and software function id, rearms change events for that function, emits `mlx5_sf_vhca_event`, and calls every blocking notifier in `dev->priv.vhca_state_n_head`. Stop unregisters the EQ notifier and flushes all workqueues so no pending events race with cleanup.

## State and Persistence Behavior

Driver state includes `dev->priv.vhca_events`, `vhca_state_nb`, and `vhca_state_n_head`. Firmware state includes VHCA event capability bits, per-function `arm_change_event`, `sw_function_id`, and current state. Event work is transient and freed after notification.

## Dependencies and Integration Points

The file depends on command layouts from `mlx5_ifc_vhca_event.h`, EQ notifier infrastructure, workqueues, SF tracepoints, and capability macros. Subscribers include SF devlink state tracking, SF hardware-table deferred free, and SF auxiliary device discovery.

## Risks and Edge Cases

The EQ event carries only function id; the work item queries firmware later, so rapid state transitions may collapse into the latest state. If rearming fails, the code still notifies subscribers but future events may be missed. Workqueue allocation failure drops events. Stop must flush after unregistering to prevent callbacks into freed SF tables.

## Test Signals

Test capability enable bits in `set_hca_cap`, active/in-use/teardown/allocated transitions, event rearm after every event, notifier registration/unregistration order, workqueue flush on unload, dropped-work allocation fault injection, and tracepoint correlation with devlink SF state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.h

## Purpose

`sf/vhca_event.h` declares the VHCA state event interface used by mlx5 SF manager components and provides no-op stubs when `CONFIG_MLX5_SF` is disabled.

## Important APIs and Types

`struct mlx5_vhca_state_event` carries hardware function id, software function id, and new VHCA state. The enabled API includes support detection, capability setup, notifier init, event init/cleanup/start/stop, notifier registration, software id modification, event arming, state query, work enqueue, and workqueue flush.

Disabled builds stub capability setup, notifier init, init/cleanup/start/stop to no-ops or success. Not all helper prototypes have stubs, so callers of query/arm/register functions must remain in SF-enabled code.

## State and Dependencies

The header itself has no storage. Enabled implementations mutate firmware VHCA state/event arm bits and `dev->priv.vhca_events`/notifier chains. It depends on `struct mlx5_core_dev`, `struct notifier_block`, and `struct work_struct` through included driver headers.

## Risks and Test Signals

Kconfig boundaries are the main risk. Compile SF and non-SF builds and validate that SF manager files do not call missing non-SF stubs. Runtime tests should confirm `mlx5_vhca_event_supported()` matches firmware capability before lifecycle functions allocate resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.c

## Purpose

`sh_devlink.c` creates a shared devlink instance for mlx5 PF devices that expose a usable serial number in PCI VPD. The shared devlink groups related devices by serial number through the kernel devlink shared-device facility.

## Important APIs and Functions

`mlx5_shd_init()` reads PCI VPD, extracts the `V3` keyword or falls back to the standard serial-number keyword, strips trailing space-delimited firmware padding, and calls `devlink_shd_get()` with empty `mlx5_shd_ops`. `mlx5_shd_uninit()` releases the shared devlink with `devlink_shd_put()` if one was acquired.

## Control Flow

Only PF devices participate. VPD absence returns success, while other VPD allocation errors propagate. Missing serial keywords also return success because shared devlink is optional. A valid keyword is duplicated, trimmed at the first space, used to get/create the shared devlink, freed, and stored in `dev->shd`.

## State and Persistence Behavior

The only driver state is `dev->shd`. The shared devlink object is reference-counted by devlink core and keyed by serial number. No mlx5-specific devlink operations are registered in this file.

## Dependencies and Integration Points

It depends on PCI VPD helpers, devlink shared-device APIs, PF detection, and `dev->pdev`. It integrates with mlx5 core init/uninit ordering and any user tooling that observes shared devlink topology.

## Risks and Test Signals

Serial parsing stops at the first space; if a legitimate serial contains spaces, grouping may truncate. VPD `V3` and legacy SN fallback should be tested on old and new adapters. Verify PF-only behavior, VPD `-ENODEV` tolerance, shared devlink refcount release, and no leak when allocation or `devlink_shd_get()` fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.h

## Purpose

`sh_devlink.h` declares the mlx5 shared-devlink lifecycle hooks used by core probe and cleanup code.

## Important APIs

It declares `mlx5_shd_init(struct mlx5_core_dev *dev)` and `mlx5_shd_uninit(struct mlx5_core_dev *dev)`.

## Control Flow, State, and Dependencies

The header has no logic or storage. The implementation stores a shared devlink pointer in `dev->shd` for PF devices with VPD serial data. It includes `linux/mlx5/driver.h` for `struct mlx5_core_dev`.

## Risks and Test Signals

Header risk is limited to prototype drift and Kconfig/build inclusion. Compile users of the hooks and test PF/VF/SF probe paths to ensure only PFs acquire shared devlink state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sh_devlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sriov.c

## Purpose

`sriov.c` manages mlx5 SR-IOV lifecycle. It enables/disables VFs at the mlx5 device and PCI layers, integrates VF vports with the eswitch, restores VF GUID/policy settings, configures dynamic VF MSI-X vector counts, waits for firmware pages to return, and exposes VF notifier registration for mlx5 submodules.

## Important APIs, Types, and Functions

Important public APIs are `mlx5_core_sriov_configure()`, `mlx5_sriov_disable()`, `mlx5_core_sriov_set_msix_vec_count()`, `mlx5_sriov_attach()`, `mlx5_sriov_detach()`, `mlx5_sriov_init()`, `mlx5_sriov_cleanup()`, `mlx5_sriov_blocking_notifier_register()`, and `mlx5_sriov_blocking_notifier_unregister()`. Local helpers are `mlx5_device_enable_sriov()`, `mlx5_device_disable_sriov()`, `mlx5_sriov_enable()`, `sriov_restore_guids()`, and `mlx5_get_max_vfs()`.

State lives in `dev->priv.sriov`: `max_vfs`, `num_vfs`, `max_ec_vfs`, and per-VF contexts with notifier heads, enabled bits, GUIDs, and policy.

## Control Flow

Enable takes the devlink lock around device-level setup, enables eswitch SR-IOV, computes default VF MSI-X vector count, and loops through requested VFs. For each VF it notifies registered listeners before enablement, calls `mlx5_core_enable_hca()`, sets MSI-X vector count if supported, marks the VF enabled, and restores InfiniBand GUID/policy settings for IB port-type devices. After device setup succeeds, `pci_enable_sriov()` creates PCI VFs; PCI failure triggers device-level disable rollback.

Disable first calls `pci_disable_sriov()`, then under devlink lock walks enabled VFs in reverse order, notifies listeners, disables each HCA, clears enabled bits, disables eswitch SR-IOV, and waits for VF and/or EC-VF firmware pages depending on whether this is a num-VF change or driver unload. ECPF devices skip host VF page wait until the ECPF itself is destroyed.

Attach/detach handle existing PCI VFs across driver bind/unbind. Initialization allocates per-VF contexts based on PCI total VFs, handles ECPF eswitch-manager max-VF query through eswitch functions, and initializes each notifier head.

## State and Persistence Behavior

Persistent driver state includes enabled flags, notifier heads, stored GUID/policy context, current and max VF counts, and EC VF capacity. Firmware state includes enabled VF HCAs, eswitch VF vports, vport GUID/policy context, and per-VF dynamic MSI-X table size. PCI state is created/destroyed by `pci_enable_sriov()` and `pci_disable_sriov()`.

## Dependencies and Integration Points

The file depends on PCI SR-IOV APIs, mlx5 HCA enable/disable commands, eswitch SR-IOV control, dynamic MSI-X helpers in `pci_irq.c`, vport context modification, page allocator wait counters, devlink locking, and blocking notifier chains used by VF-related modules.

## Risks and Edge Cases

`mlx5_device_enable_sriov()` continues after per-VF enable, MSI-X, or GUID restore failures and still returns 0 after eswitch enable; this can leave a partially enabled VF set, so callers and tests must inspect per-VF state. Page wait selection differs for EC SR-IOV and regular SR-IOV; incorrect counters can cause false timeouts or skipped waits. Notifier registration validates against `sriov->num_vfs`, not total allocated contexts, so notifiers for disabled but possible VFs are rejected.

## Test Signals

Test enabling/disabling varying VF counts, PCI enable rollback, driver attach with preexisting VFs, ECPF/EC-VF page wait behavior, IB GUID/policy restore, dynamic MSI-X sysfs updates including default count, eswitch enable failure, per-VF HCA failures, and notifier callbacks before VF enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/Makefile

## Purpose

This `Makefile` supplies a build include path for the mlx5 steering subtree.

## Important Content and Control Flow

It contains only the SPDX line and `subdir-ccflags-y += -I$(src)/..`, which adds the parent mlx5 core directory to compiler include paths for objects built in this directory and its subdirectories.

## State, Dependencies, and Integration

There is no runtime state. The build-state effect is that steering sources can include headers from `core/..` relative to their source path without every object adding its own include flag.

## Risks and Test Signals

The risk is build breakage if directory layout changes or if another Makefile stops inheriting this flag. Test by building mlx5 steering objects and checking that local includes resolve without adding broader include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/Makefile

## Purpose

This HWS `Makefile` supplies a parent-directory include path for hardware steering sources.

## Important Content and Control Flow

It contains only the SPDX line and `subdir-ccflags-y += -I$(src)/..`, adding `core/steering` as an include root for HWS compilation units.

## State, Dependencies, and Integration

There is no runtime state. The build integration allows HWS files to include neighboring steering headers without object-specific include flags.

## Risks and Test Signals

The risk is compile failure if HWS headers move or if subdirectory flag inheritance changes. Test by building the HWS steering objects under relevant mlx5 Kconfig options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.c

## Purpose

`steering/hws/action.c` is the mlx5 hardware steering action engine. It validates action ordering, creates and destroys action objects, allocates STC resources, builds shared/default STCs, creates backing firmware objects for destination arrays, samplers, ranges, reformat, and modify-header actions, and converts rule-time action data into WQE control/data setters.

## Important APIs, Types, and Functions

Public action creation APIs include `mlx5hws_action_create_dest_table_num()`, `mlx5hws_action_create_dest_table()`, `mlx5hws_action_create_dest_drop()`, `mlx5hws_action_create_default_miss()`, `mlx5hws_action_create_tag()`, `mlx5hws_action_create_aso_meter()`, `mlx5hws_action_create_counter()`, `mlx5hws_action_create_dest_vport()`, `mlx5hws_action_create_push_vlan()`, `mlx5hws_action_create_pop_vlan()`, `mlx5hws_action_create_reformat()`, `mlx5hws_action_create_modify_header()`, `mlx5hws_action_create_dest_array()`, `mlx5hws_action_create_insert_header()`, `mlx5hws_action_create_remove_header()`, `mlx5hws_action_create_dest_match_range()`, `mlx5hws_action_create_last()`, `mlx5hws_action_create_flow_sampler()`, and `mlx5hws_action_destroy()`.

Template APIs are `mlx5hws_action_template_create()`, `mlx5hws_action_template_process()`, and `mlx5hws_action_template_destroy()`. STC helper APIs used by other HWS files are `mlx5hws_action_alloc_single_stc()`, `mlx5hws_action_free_single_stc()`, `mlx5hws_action_get_default_stc()`, `mlx5hws_action_put_default_stc()`, `mlx5hws_action_prepare_decap_l3_data()`, `mlx5hws_action_type_to_str()`, `mlx5hws_action_get_type()`, and `mlx5hws_action_get_dev()`.

Key local helpers include `hws_action_fill_stc_attr()`, `hws_action_fixup_stc_attr()`, shared STC get/put functions, reformat and modify-header builders, range action table builders, WQE setter functions, and action order validation against `action_order_arr`.

## Control Flow

Action creation starts with generic allocation and validation. `hws_action_create_generic_bulk()` requires HWS FDB flags, checks context HWS support and eswitch-manager restrictions, allocates one or more `struct mlx5hws_action`, and initializes type/context/flags. `hws_action_create_stcs()` fills an STC attribute for the action type, locks `ctx->ctrl_lock`, and allocates an STC from `ctx->stc_pool`; FDB actions program both the base and mirror STC objects. `hws_action_fixup_stc_attr()` adapts STCs for table direction and mirror behavior, such as turning ignored mirror table jumps into DROP, converting ALLOW to JUMP_TO_VPORT in FDB TX/RX, turning uplink vport jumps into JUMP_TO_UPLINK, and suppressing TAG in FDB TX.

Simple actions allocate a single STC for drop, miss, tag, counter, ASO meter, table jump, vport jump, push/pop VLAN, remove header, and tunnel L2 decap. Pop VLAN also obtains a shared double-pop STC. Reformat actions are specialized: L2-to-tunnel uses header insert with an argument object; L2-to-tunnel-L3 combines a shared decap-L3 STC with insert; tunnel-L3-to-L2 builds a modify-header program that removes outer headers, inserts L2 bytes in reverse-order inline chunks, and removes padding. Modify-header actions calculate NOP insertion for hardware constraints, optionally allocate a shared argument object, use inline single actions when possible, otherwise allocate patterns and argument storage.

Destination arrays and samplers create intermediate firmware forwarding tables ("islands") with `mlx5hws_cmd_forward_tbl_create()` and then an STC pointing to that table. Range destination creates a definer on outer packet length, an STE pool, paired RTCs for FDB base/mirror, an always-hit match STE plus range STE through the control send queue, a hit table action, and an STC that jumps into the STE table.

Action template processing maps a validated action-type list into a sequence of WQE setter slots. It reserves one extra setter for jumbo/match STE jump-in, assigns counter, single, double, remove, insert, modify, ASO, and hit setters, handles two POP_VLAN actions through a shared double-pop STC, installs a default hit STC if no terminal hit action is supplied, computes the number of action STEs, and marks templates that only terminate without action DWs.

## State and Persistence Behavior

Persistent HWS state includes allocated action objects, STC pool chunks, default and shared STCs in `ctx->common_res`, argument objects, pattern ids, packet reformat objects, forwarding tables, range definers, STE pools, RTC ids, and action templates. Most firmware resource programming happens under `ctx->ctrl_lock` because modifying shared STC bases in parallel is unsupported. Rule-time WQE setters may write non-shared modify/reformat arguments into argument memory and set `apply->require_dep` so dependent writes are ordered.

## Dependencies and Integration Points

The file depends on nearly all HWS infrastructure: context capabilities, STC/RTC/forward-table command wrappers, STC and STE pools, pattern manager, argument manager, send queues, definers, table type translation, flow table objects, flow destination types, ASO meter constants, and public HWS action types from `mlx5hws.h`. It integrates with rule creation through action templates and setters, with FDB mirror tables, and with FS/HWS compatibility layers that create these actions for flow steering.

## Risks and Edge Cases

The action ordering array is the gatekeeper for supported sequences; new action types must update the order array, string table, STC fill, destroy, and template setter logic together. Bulk actions allocate arrays of `struct mlx5hws_action`; destroy paths assume the first action carries counts for all siblings. Shared actions reject combinations of shared flag, bulk size, and log bulk size that the implementation cannot represent. Error unwinds are complex, especially for range actions, destination arrays, and modify-header patterns/args. Several allocations occur under `ctx->ctrl_lock`; long command paths or send-queue drains can increase lock hold time. Runtime setters silently return if temporary allocation for NOP-expanded modify data fails, which can drop an argument write without direct rule-create failure.

## Test Signals

Test every public action type, valid and invalid action order combinations, FDB mirror behavior, merged and non-merged eswitch vport destinations, uplink destinations, shared/default STC refcounts, destroy after partial create failure, two-pop VLAN optimization, shared and non-shared reformat/modify-header actions, decap-L3 with and without VLAN, range destination packet-length matching, flow sampler and destination array forwarding tables, and rule-time WQE data writes. Fault injection should target STC allocation, command STC modify, pattern allocation, arg allocation/write, forwarding table create, RTC create, send-queue drain, and definer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.c -->
