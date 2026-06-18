# subset-b-003922 InfiniBand ERDMA and HFI1 research

This grouped report covers the requested ERDMA verbs and HFI1 build, affinity, and ASPM files. Each source section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.c

## Purpose

This file implements the Alibaba Elastic RDMA provider's ib_verbs-facing operations. It handles device and port queries, protection domains, user contexts and mmap doorbells, queue pair and completion queue creation/destruction, memory registration, QP state transitions, RoCEv2 address handles, GID and pkey hooks, port events, MTU programming, and hardware stats. The implementation bridges RDMA core objects to ERDMA command queue requests and to PCI DMA resources.

## Important APIs, types, and functions

The main entry points are `erdma_alloc_ucontext()`, `erdma_dealloc_ucontext()`, `erdma_query_device()`, `erdma_query_port()`, `erdma_get_port_immutable()`, `erdma_alloc_pd()`, `erdma_create_qp()`, `erdma_destroy_qp()`, `erdma_modify_qp()`, `erdma_query_qp()`, `erdma_create_cq()`, `erdma_destroy_cq()`, `erdma_reg_user_mr()`, `erdma_get_dma_mr()`, `erdma_ib_alloc_mr()`, `erdma_map_mr_sg()`, `erdma_dereg_mr()`, `erdma_mmap()`, `erdma_add_gid()`, `erdma_del_gid()`, `erdma_create_ah()`, `erdma_destroy_ah()`, and `erdma_get_hw_stats()`.

Important internal helpers include `erdma_alloc_idx()` and `erdma_free_idx()` for bitmap-backed resource IDs, `create_qp_cmd()`, `create_cq_cmd()`, and `regmr_cmd()` for hardware command encoding, `get_mtt_entries()` and `put_mtt_entries()` for user memory translation tables, `erdma_map_user_dbrecords()` for shared doorbell record pinning, and `erdma_init_mod_qp_params_rocev2()` for converting RDMA core QP attributes to device masks.

## Control Flow

User context allocation increments `dev->num_ctx`, allocates either legacy BAR doorbells or extended doorbell pages through `CMDQ_OPCODE_ALLOC_DB`, inserts three RDMA mmap entries, and returns mmap offsets to userspace. `erdma_mmap()` later resolves those entries and maps the hardware doorbell page with device page protections. Deallocation removes mmap entries, frees extended doorbells, and decrements the context count.

QP creation validates capabilities and type support, reserves a QPN in `dev->qp_xa`, rounds queue depths to powers of two, then follows separate user and kernel setup paths. Kernel QPs allocate coherent SQ/RQ buffers, software WR tables, and DMA-pool doorbell records. User QPs pin the userspace queue buffer into SQ and RQ MTTs and map a userspace doorbell record page. `create_qp_cmd()` then posts the hardware create command with inline or one-level MTT addresses. CQ creation follows the same pattern: reserve CQN, initialize user MTT or kernel coherent memory, return userspace response data, then post `CMDQ_OPCODE_CREATE_CQ`.

MR registration pins user memory, computes page size and MTT entries, allocates an STAG, encodes access/type/page layout in `CMDQ_OPCODE_REG_MR`, and releases resources on any failure edge. Fast-registration MRs allocate a pre-sized MTT and are populated later by `erdma_map_mr_sg()`. QP modification serializes with `qp->state_lock`, validates RDMA core state rules for RoCEv2, maps IB states to ERDMA protocol states, and calls protocol-specific state transition helpers defined elsewhere.

## State and Persistence

State is in RDMA core objects, ERDMA private wrappers, xarrays, bitmaps, pinned `ib_umem`, DMA mappings, command-queue programmed hardware tables, and PCI BAR/doorbell resources. Nothing persists to disk. Resource ID bitmaps are protected by spinlocks. QP state transitions are protected by `state_lock`; QP lifetime uses `kref` plus `safe_free` completion. User doorbell record pages are tracked per context with a mutex and reference count so one pinned page can serve multiple QP/CQ records.

## Dependencies and Integration Points

The file depends on RDMA core (`ib_device`, `ib_pd`, `ib_qp`, `ib_cq`, `ib_umem`, uverbs copy helpers, RDMA mmap helpers, AH/GID helpers), Linux DMA and PCI APIs, xarray resource lookup, netdevice MTU/link helpers, IPv6 address helpers, and ERDMA hardware command definitions from local headers. It integrates with ERDMA CM for iWARP QP teardown, with `erdma_post_send()`, `erdma_post_recv()`, and `erdma_poll_cq()` declared in the header but implemented elsewhere, and with userspace ABI structs from `rdma/erdma-abi.h`.

## Risks

The highest-risk areas are resource unwind paths and hardware layout encoding. QP/CQ creation mixes xarray IDs, user pinned memory, DMA mappings, mmap offsets, and command queue state; a missing unwind can leak pinned pages or leave stale xarray entries. MTT code supports continuous and scatter multi-level tables, so page-size selection, high-count fields, and DMA unmap symmetry are critical. `alloc_db_resources()` appears to assign `ctx->cdb` from `rdb_off` and `ctx->rdb` from `cdb_off`, which should be treated as a review point against the hardware ABI. QP state validation is stricter for RoCEv2 than iWARP because iWARP state is largely delegated to connection-manager helpers. Destroy paths return early if hardware destroy commands fail, intentionally preserving software resources but making caller retry semantics important.

## Test Signals

Useful signals include `ibv_devinfo` capability output, uverbs context allocation and mmap tests, PD/QP/CQ/MR create-destroy stress with fault injection, kernel and userspace RC traffic, RoCEv2 UD/GSI AH creation, GID add/delete through netdevice address changes, FRMR map/unmap workloads, QP state transition tests, concurrent CQ/QP destroy during traffic, and hardware stats reads. Kernel logs should be checked for DMA mapping failures, command queue errors, refcount waits, leaked pinned pages, and WARNs from freeing unused resource bitmap IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.h

## Purpose

This header defines the ERDMA provider's verbs-layer private objects, protocol constants, state enums, conversion helpers, and exported verbs function prototypes. It is the contract between `erdma_verbs.c`, posting/polling code, connection-management code, and the device registration code that installs the ib_device operation table.

## Important APIs, types, and functions

Important limits include `ERDMA_MAX_PD`, `ERDMA_MAX_SEND_WR`, `ERDMA_MAX_ORD`, `ERDMA_MAX_IRD`, SGE limits, inline-data size, FRMR page-list length, MTT constants, MR type constants, and ERDMA access bits. Main object wrappers are `struct erdma_ucontext`, `struct erdma_pd`, `struct erdma_mtt`, `struct erdma_mem`, `struct erdma_mr`, `struct erdma_av`, `struct erdma_ah`, `struct erdma_uqp`, `struct erdma_kqp`, `struct erdma_qp`, and `struct erdma_cq`.

The header also defines iWARP and RoCEv2 QP states and attribute masks, `union erdma_mod_qp_params`, `struct erdma_qp_attrs`, xarray lookup helpers `find_qp_by_qpn()` and `find_cq_by_cqn()`, type-cast helpers such as `to_eqp()` and `to_ecq()`, `to_erdma_access_flags()`, protocol checks, and the full set of provider verbs prototypes.

## Control Flow

There is no standalone runtime flow in the header. The inline helpers shape control flow in implementation files by translating RDMA core objects to ERDMA containers, validating GID network types, choosing iWARP versus RoCEv2 behavior, and loading live QP/CQ objects from device xarrays. The prototypes expose create, destroy, query, modify, mmap, memory registration, CQ notification, posting, polling, stats, GID, pkey, and AH operations to other ERDMA modules.

## State and Persistence

The state described here is volatile kernel and hardware-facing state. `erdma_ucontext` stores doorbell mmap entries and a mutex-protected list of pinned user doorbell record pages. QPs carry a kref, completion for safe free, state semaphore, delayed reflush work, SQ/RQ backing state, CQ pointers, and protocol-specific attributes. CQs carry either kernel queue memory and doorbell record state or user MTT and doorbell record state. MRs store memory translation tables, page geometry, access flags, type, and validity.

## Dependencies and Integration Points

The header includes `erdma.h` and depends on RDMA core types, xarray-backed device fields, ERDMA protocol constants, Ethernet address sizes, and local hardware ABI structures. It is included by ERDMA verbs, CM, and send/receive completion paths. Public prototypes integrate with the ib_device ops registration and with RoCEv2 address/GID management paths.

## Risks

The header is a shared ABI inside the driver. Changing limits or struct fields can silently desynchronize command encoding, userspace ABI expectations, and posting/polling code. The iWARP and RoCEv2 state enums have different domains but share conversion tables in `erdma_verbs.c`; array dimensions and enum values must stay aligned. `find_qp_by_qpn()` and `find_cq_by_cqn()` return raw xarray pointers, so callers must pair lookups with the appropriate object lifetime rules. `to_erdma_access_flags()` intentionally omits local read as a hardware flag and always leaves local read handling to caller policy.

## Test Signals

Compile coverage is the first signal because this header fans out across the driver. Runtime signals include successful ib_device registration, object allocation through every exported op, QP lookup by async events or completions, CQ polling and notification, MR registration and fast-registration, and RoCEv2 AH/GID handling. ABI-sensitive changes should be tested with rdma-core userspace exercising context, QP, CQ, MR, AH, and mmap flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_verbs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Kconfig

## Purpose

This Kconfig file declares the HFI1 low-level InfiniBand/RDMA driver option and two debug-oriented configuration switches. The driver is presented as "Cornelis OPX Gen1 support" and can be built as a module or built in.

## Important APIs, types, and functions

The primary symbol is `CONFIG_INFINIBAND_HFI1`. It depends on `X86_64`, `INFINIBAND_RDMAVT`, `I2C`, and `!UML`, and selects `MMU_NOTIFIER`, `CRC32`, and `I2C_ALGOBIT`. `CONFIG_HFI1_DEBUG_SDMA_ORDER` enables SDMA completion ordering debug support for unit testing. `CONFIG_SDMA_VERBOSITY` enables verbose SDMA debug output.

## Control Flow

Kconfig resolution determines whether `drivers/infiniband/hw/hfi1/Makefile` contributes `hfi1.o` to the kernel build. The selected helper symbols ensure required subsystems are available before compiling the driver. The two debug booleans only become visible when `INFINIBAND_HFI1` is enabled.

## State and Persistence

Kconfig selections persist in the kernel `.config`, not in runtime driver state. The debug symbols may compile additional code paths or logging behavior into the resulting HFI1 object, depending on references in other source files.

## Dependencies and Integration Points

The driver integrates with RDMAVT, I2C, MMU notifier, CRC32, and bit-banged I2C infrastructure. The `!UML` exclusion prevents builds for User Mode Linux. X86_64 is required, reflecting platform and hardware assumptions in the HFI1 driver.

## Risks

Dependency changes can break allmodconfig or unsupported architecture builds. Removing selected symbols can produce link or runtime failures in memory registration, CRC, or QSFP/I2C paths. Debug options should remain default-off because they can increase logging volume or alter test-only SDMA behavior.

## Test Signals

Signals are Kconfig visibility checks, `olddefconfig` stability, `CONFIG_INFINIBAND_HFI1=m` and `=y` builds, allmodconfig coverage on x86_64, and negative coverage that UML does not offer the driver. Debug symbols should be build-tested both disabled and enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Makefile -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Makefile

## Purpose

This Makefile defines the object composition for the HFI1 kernel module or built-in object. It gathers the many HFI1 implementation units under `hfi1.o` when `CONFIG_INFINIBAND_HFI1` is enabled.

## Important APIs, types, and functions

The key build variable is `obj-$(CONFIG_INFINIBAND_HFI1) += hfi1.o`. The `hfi1-y` list includes core files such as `affinity.o`, `aspm.o`, `chip.o`, `device.o`, `driver.o`, interrupt and PCIe support, receive and transmit paths, IPOIB integration, MAD handling, SDMA, TID RDMA, user contexts, verbs, and QP/RC/UC/UD logic. Conditional additions include `debugfs.o` under `CONFIG_DEBUG_FS` and `fault.o` only when both fault-injection Kconfig symbols and debugfs support are enabled. `CFLAGS_trace.o = -I$(src)` gives generated trace code access to local headers, and `MVERSION` can define `HFI_DRIVER_VERSION_BASE` for `driver.o`.

## Control Flow

During kbuild, the HFI1 Kconfig symbol selects whether this directory emits `hfi1.o`. Kbuild compiles every object in `hfi1-y`, optionally appends debugfs/fault objects, applies per-object CFLAGS, and links them into the final HFI1 module or built-in object.

## State and Persistence

There is no runtime state in the Makefile. Its persistent effect is the build graph: which source files are compiled and which preprocessor flags are visible to specific objects.

## Dependencies and Integration Points

This file integrates HFI1 with Linux kbuild, debugfs, fault injection, tracing include paths, and external module version injection through `MVERSION`. It must stay aligned with source filenames and with Kconfig symbols that guard optional code.

## Risks

Missing an object from `hfi1-y` can compile cleanly only until a referenced symbol is needed, or worse can drop a feature path from the module. Adding optional code without matching Kconfig guards can break minimal builds. `CFLAGS_driver.o` quoting is sensitive because it feeds a C string macro. Trace include paths must remain correct for generated trace headers.

## Test Signals

Build `CONFIG_INFINIBAND_HFI1` as both module and built-in, with and without `CONFIG_DEBUG_FS`, `CONFIG_FAULT_INJECTION`, and `CONFIG_FAULT_INJECTION_DEBUG_FS`. Check that `modinfo hfi1` or built-in version strings reflect `MVERSION` when supplied and that trace compilation still finds local headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.c

## Purpose

This file manages HFI1 CPU affinity policy for MSI-X interrupts, completion vectors, and user processes. It builds NUMA-aware CPU masks, avoids hyperthread siblings where possible, spreads SDMA and receive interrupts, tracks CPUs reserved for completion vectors, reacts to user IRQ affinity changes, and recommends process CPU placement for PSM/user contexts.

## Important APIs, types, and functions

Public entry points are `init_real_cpu_mask()`, `node_affinity_init()`, `node_affinity_destroy_all()`, `hfi1_dev_affinity_init()`, `hfi1_dev_affinity_clean_up()`, `hfi1_comp_vectors_set_up()`, `hfi1_comp_vectors_clean_up()`, `hfi1_comp_vect_mappings_lookup()`, `hfi1_get_irq_affinity()`, `hfi1_put_irq_affinity()`, `hfi1_get_proc_affinity()`, and `hfi1_put_proc_affinity()`.

Important state includes global `node_affinity`, per-node `struct hfi1_affinity_node`, per-mask generation tracking in `struct cpu_mask_set`, the per-NUMA-node HFI device counter `hfi1_per_node_cntr`, per-device completion vector masks and mappings, and MSI-X entry masks. Internal helpers allocate per-node records, select least-used per-CPU completion-vector counters, create mapping tables, and update SDMA affinity notifiers.

## Control Flow

`node_affinity_init()` initializes global process masks, records topology counts, builds the real CPU mask by removing hyperthread siblings, scans PCI devices in `hfi1_pci_tbl`, and counts HFI devices per NUMA node. `hfi1_dev_affinity_init()` creates or reuses a NUMA-node entry, partitions CPUs into general/control, receive, SDMA/default, and completion-vector masks, reserves a per-device share of completion-vector CPUs, and stores the entry on the device.

`hfi1_comp_vectors_set_up()` converts a device completion-vector CPU mask into an index-to-CPU mapping, preferring CPUs not already used by default interrupts. `hfi1_get_irq_affinity()` selects a CPU based on IRQ type, sets `msix->mask`, publishes an IRQ affinity hint, and registers an SDMA notifier. If users later change an SDMA IRQ affinity through `/proc/irq`, the notifier updates `sde->cpu` and the global default interrupt mask. `hfi1_put_irq_affinity()` reverses accounting and removes hints/notifiers.

`hfi1_get_proc_affinity()` first respects a process already pinned to one CPU or a smaller explicit cpuset. Otherwise it chooses a CPU by generation: preferred NUMA node before other nodes, non-interrupt CPUs before interrupt CPUs, and physical cores before later hyperthreads. `hfi1_put_proc_affinity()` releases the CPU back to the global process mask.

## State and Persistence

All state is runtime-only. `node_affinity` and `hfi1_per_node_cntr` are module-global and protected by `node_affinity.lock` for list and mask mutation. Per-device state includes `dd->affinity_entry`, `dd->comp_vect`, `dd->comp_vect_possible_cpus`, and `dd->comp_vect_mappings`. `cpu_mask_set.gen` supports controlled overcommit by clearing or restoring `used` masks once all CPUs in a set have been consumed or released.

## Dependencies and Integration Points

The file depends on Linux topology, cpumask, interrupt affinity notifier, NUMA, PCI enumeration, and HFI1 internals from `hfi.h`, `sdma.h`, and `trace.h`. It integrates with MSI-X setup/teardown, SDMA engine CPU fields, RDMAVT completion-vector lookup, kernel receive queues, user context open/close paths, and debug tracing categories.

## Risks

Mask arithmetic is the main risk. Incorrect generation handling can overload CPUs prematurely or fail to release CPUs for later devices. NUMA fallback handles invalid PCI NUMA data by assigning one device per possible node, but performance may degrade. Some paths assume `node_affinity_lookup(dd->node)` succeeds after device init; calling IRQ teardown without prior init could dereference missing entries. `hfi1_update_sdma_affinity()` rejects `cpu > num_online_cpus()` rather than `cpu >= nr_cpu_ids`, which is worth reviewing for sparse CPU IDs. Completion-vector allocation depends on accurate `hfi1_per_node_cntr` and `dd->n_krcv_queues`; topology changes after init are not dynamically rebalanced.

## Test Signals

Validation signals include boot logs showing IRQ-to-CPU assignments, `/proc/interrupts` distribution across NUMA-local CPUs, SDMA notifier behavior when IRQ affinity is manually changed, completion-vector lookup returning stable CPUs, process affinity recommendations under default and pre-pinned cpusets, multi-device systems on the same NUMA node, systems with and without SMT, and invalid/missing PCI NUMA node fallback. Lockdep and KASAN are useful around init/cleanup and IRQ teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.h

## Purpose

This header declares the HFI1 affinity policy interface and shared data structures used by HFI1 initialization, MSI-X management, completion-vector mapping, and user process placement.

## Important APIs, types, and functions

`enum irq_type` classifies interrupts as SDMA, receive context, netdev context, general, or other. `enum affinity_flags` names broader affinity policies. `struct cpu_mask_set` pairs an allowed CPU mask with a used mask and generation counter. `struct hfi1_affinity_node` stores one NUMA node's interrupt and completion-vector masks plus per-CPU completion-vector counters. `struct hfi1_affinity_node_list` stores global node list state, real CPU mask, process CPU mask, topology counts, and the mutex protecting node affinity state.

The header exports init/cleanup, IRQ affinity get/put, process affinity get/put, completion-vector setup/cleanup/lookup, and the global `node_affinity` object.

## Control Flow

The header has no independent execution path. It defines the call surface used by module initialization to create global affinity state, by per-device probe to initialize node/device masks, by MSI-X allocation to assign and release IRQ CPUs, by RDMAVT to map completion vectors, and by user-context code to recommend CPU placement.

## State and Persistence

The structures describe runtime-only affinity state. `node_affinity` is global, while `hfi1_affinity_node` records are dynamically allocated per NUMA node and referenced by device data. CPU mask contents change as interrupts, completion vectors, and processes are assigned and released.

## Dependencies and Integration Points

The header includes `hfi.h`, so it relies on HFI1 device and context types plus Linux cpumask/list/mutex infrastructure made available through driver headers. It is consumed by `affinity.c` and other HFI1 files that need CPU assignment services.

## Risks

Because the structs are shared with device code, field changes require coordinated updates in init, teardown, and lookup paths. The global `node_affinity` extern makes initialization order important. `IRQ_OTHER` exists in the enum, but `affinity.c` treats unknown/default IRQ types as invalid for assignment, so callers should not expect a fallback policy for it.

## Test Signals

Build coverage across HFI1 is required after any header change. Runtime signals are successful device affinity initialization, MSI-X setup and teardown, completion-vector CPU lookup, user process affinity assignment, and clean module unload freeing all per-node records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/affinity.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.c

## Purpose

This file controls PCIe ASPM L1 policy for HFI1. It supports disabled, enabled, and dynamic modes. Dynamic mode disables ASPM when receive context interrupts arrive close together, then re-enables ASPM after a timer expires without enough interrupt activity.

## Important APIs, types, and functions

The module parameter is `aspm`, backed by global `aspm_mode`. Public functions are `aspm_init()`, `aspm_exit()`, `aspm_hw_disable_l1()`, `__aspm_ctx_disable()`, `aspm_disable_all()`, and `aspm_enable_all()`. Internal helpers include `aspm_hw_l1_supported()`, `aspm_hw_set_l1_ent_latency()`, `aspm_hw_enable_l1()`, `aspm_enable()`, `aspm_disable()`, `aspm_disable_inc()`, `aspm_enable_dec()`, `aspm_ctx_timer_function()`, and `aspm_ctx_init()`.

## Control Flow

`aspm_init()` initializes the device ASPM spinlock, detects L1 support on both downstream and upstream PCIe components, initializes per-receive-context locks and timers for static contexts, programs a slower L1 entry latency, forces ASPM off, and then enables it if the selected mode allows. Dynamic per-context support is enabled only when hardware supports ASPM, mode is dynamic, and the context index is below `first_dyn_alloc_ctxt`.

Receive interrupt paths call the inline wrapper in the header, which enters `__aspm_ctx_disable()` only for supported contexts. That function records interrupt timestamps, detects two interrupts within `ASPM_TRIGGER_NS`, disables device ASPM through a counted global disable if needed, and schedules a one-second timer. The timer calls `aspm_enable_dec()` and re-enables ASPM only when all dynamic disable users have released their count. `aspm_disable_all()` stops per-context timers and interrupt processing before forcing ASPM off, while `aspm_enable_all()` re-enables hardware and resets per-context dynamic state.

## State and Persistence

State is volatile and stored in `hfi1_devdata` and `hfi1_ctxtdata`: `aspm_supported`, `aspm_enabled`, `aspm_lock`, `aspm_disabled_cnt`, per-context `aspm_lock`, `aspm_intr_supported`, `aspm_intr_enable`, `aspm_enabled`, timestamp fields, and timers. The only persistent-like input is the read-only module parameter value for the loaded module instance. Hardware state lives in PCIe link control/configuration registers until changed or reset.

## Dependencies and Integration Points

The file depends on PCIe capability accessors, HFI1 PCI config constants, HFI1 context lookup/refcount helpers, timers, atomics, spinlocks, and `is_ax()` hardware stepping detection. It integrates with receive interrupt handling via `aspm_ctx_disable()`, context initialization, PSM open/close behavior through all-context enable/disable, and driver unload through `aspm_exit()`.

## Risks

ASPM programming must touch downstream and upstream components in the documented order; reversing order can violate PCIe ASPM sequencing. Timer and interrupt races are controlled by per-context locks and a device count, so changes must preserve locking. `aspm_ctx_timer_function()` unconditionally marks the context enabled after decrementing the device count; double timer scheduling or missed timer deletion would corrupt the disable count. `aspm_disable_all()` resets the atomic count after disabling hardware, so it must remain synchronized with context timer deletion. Dynamic mode trades power for latency; too-low trigger thresholds or excessive rescheduling can cause performance or power regressions.

## Test Signals

Signals include module parameter coverage for `aspm=0`, `1`, and `2`, inspection of PCIe L1 enable bits on both endpoints, interrupt-heavy verbs workloads showing dynamic disable/re-enable, idle periods showing L1 returns after about one second, PSM context open/close paths disabling dynamic interrupt processing, suspend/resume or driver unload leaving ASPM enabled for power saving, and lockdep/timer debugging under interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.h

## Purpose

This header declares the HFI1 ASPM control interface, the module-visible ASPM mode variable, and the fast inline receive-context hook used by interrupt paths.

## Important APIs, types, and functions

`enum aspm_mode` defines `ASPM_MODE_DISABLED`, `ASPM_MODE_ENABLED`, and `ASPM_MODE_DYNAMIC`. The exported `aspm_mode` is the backing storage for the module parameter. Public functions initialize and exit ASPM handling, force hardware L1 off, disable or enable all contexts, and handle dynamic per-context disable through `__aspm_ctx_disable()`. The inline `aspm_ctx_disable()` checks `rcd->aspm_intr_supported` before calling the heavier implementation.

## Control Flow

The header shapes receive interrupt flow by keeping the unsupported path to one likely branch. Driver initialization calls `aspm_init()`, receive contexts call `aspm_ctx_disable()` on interrupts, PSM/context management can call all-context enable/disable helpers, and driver teardown calls `aspm_exit()`.

## State and Persistence

The header itself stores no state beyond declaring `aspm_mode`. It assumes ASPM fields exist in `struct hfi1_devdata` and `struct hfi1_ctxtdata`, supplied by `hfi.h`. Those fields and PCIe link registers are runtime-only.

## Dependencies and Integration Points

The header includes `hfi.h` and is consumed by HFI1 interrupt and initialization code. It integrates the ASPM implementation with receive-context data structures without exposing PCIe register details to callers.

## Risks

The inline fast path is in an interrupt-sensitive area, so adding work before the `likely(!rcd->aspm_intr_supported)` return would affect receive latency. The enum values are user-visible through the module parameter description; changing numeric values would break existing boot/module options.

## Test Signals

Build coverage should include all HFI1 users of `aspm_ctx_disable()`. Runtime signals are correct behavior for each `aspm` module parameter value, no measurable overhead when dynamic ASPM is unsupported, and clean calls through init, interrupt, all-context disable/enable, and exit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/aspm.h -->
