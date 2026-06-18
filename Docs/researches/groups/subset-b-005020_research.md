# Research Report: subset-b-005020

This grouped report covers the requested Arm perf PMU, BRBE, CoreSight architecture PMU, and vendor backend files. Each source file has a source-tree-aligned section delimited for reconciliation into its mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-cmn.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm-cmn.c

Purpose: Implements the perf uncore PMU driver for Arm CMN-600/650/700, CMN-S3, and CI-700 coherent mesh interconnects. It discovers the CMN topology, exposes model/revision-filtered event aliases through sysfs, maps perf events onto XP DTM local counters and DTC global counters, supports XP watchpoints, services overflow IRQs, and handles CPU hotplug migration for the CPU that owns perf context and interrupt affinity.

Important APIs and types: Main runtime types are `struct arm_cmn`, `struct arm_cmn_node`, `struct arm_cmn_dtm`, `struct arm_cmn_dtc`, and the compact `struct arm_cmn_hw_event` embedded into `hw_perf_event`. The PMU callbacks are `arm_cmn_event_init()`, `arm_cmn_event_add()`, `arm_cmn_event_del()`, `arm_cmn_event_start()`, `arm_cmn_event_stop()`, `arm_cmn_event_read()`, transaction callbacks, and `arm_cmn_pmu_enable()/disable()`. Discovery and setup are handled by `arm_cmn_probe()`, `arm_cmn_discover()`, `arm_cmn_init_dtcs()`, `arm_cmn_init_dtm()`, `arm_cmn_init_dtc()`, and `arm_cmn_init_irqs()`. Event ABI is built by `arm_cmn_event_attrs`, `arm_cmn_format_attrs`, `arm_cmn_event_show()`, and `arm_cmn_event_attr_is_visible()`.

Control flow: Platform probe maps the whole configuration resource, resolves the CMN-600 root offset if needed, walks CFG and XP child pointers, filters unsupported/external nodes, detects part/revision, mesh dimensions, VC counts, multi-DTM layout, DTC domains, and PMU-capable device nodes. It then sorts nodes, initializes DTMs and DTCs, requests DTC MMIO windows/IRQs, registers a perf PMU, and optionally exposes a debugfs mesh map. Perf event init rejects sampling/task events, pins `event->cpu` to `cmn->cpu`, resolves the requested type/nodeid to one or more discovered nodes, computes DTC coverage and filter selectors, and validates group capacity. Add first reserves DTC global counters, then DTM local counters or watchpoint slots, writes DTM routing config, seeds counters, and optionally starts the event. Start writes DTC cycle-counter state, watchpoint value/mask registers, or per-node event select fields. Reads combine DTM local 16-bit counts with overflowed DTC 32-bit high-order counts; transactions stop the PMU around add/read batches to avoid skew. IRQ handling drains DTC overflow status and updates assigned events, following `irq_friend` links for shared interrupts.

State and persistence: Driver state is devm-managed under `struct arm_cmn`, with topology arrays for XPs/DNs/DTMs/DTCs, per-DTM counter and watchpoint allocation state, per-node occupancy/filter reference counts, DTC event pointers, active CPU, PMU state flags, and optional debugfs dentry. Hardware state lives in CMN DTM/DTC PMU registers, event-select fields, watchpoint config/value/mask registers, counter values, overflow status, and IRQ affinity. State persists until event deletion, PMU disable/remove, CPU migration, or device reset; module exit unregisters the platform driver, CPU hotplug state, and debugfs root.

Dependencies and integration points: Uses Linux perf uncore PMU APIs, platform devices, OF/ACPI match tables, IRQ APIs, CPU hotplug, debugfs, MMIO helpers, and kernel sort/slab helpers. Firmware bindings provide compatible/HID data, memory resources, IRQs, and for CMN-600 root-node offset. Sysfs event/format/cpumask/identifier files are the user ABI consumed by `perf stat -e arm_cmn_*/.../`.

Risks: The driver relies on exact hardware topology discovery; touching external or device-isolated nodes can hang the system, so the isolation check and external-node skip are critical. Counter allocation is constrained by four DTM counters per DTM, eight DTC counters per DTC, watchpoint pair/combine rules, and shared occupancy filter fields. Multi-DTM port mapping, CMN-S3 PMU offsets, combined HNP/CCLA nodes, and revision-specific event visibility are easy places for regressions. Overflow math depends on the DTM/DTC split and transaction stop/start behavior. Probe/remove and shared IRQ-friend logic should be reviewed carefully when changing DTC enumeration.

Test signals: Build with OF and ACPI, probe on each supported part/revision, verify `/sys/bus/event_source/devices/arm_cmn_*` events/format/cpumask/identifier, run `perf stat` for DTC cycles, HNF/HNS/XP/watchpoint events including by-node filters, stress event groups up to DTM/DTC capacity, force counter overflows, inspect debugfs `arm-cmn/map`, test CPU hotplug/NUMA migration and shared IRQs, and confirm probe refuses device-isolation configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-cmn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-ni.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm-ni.c

Purpose: Implements the perf PMU driver for Arm NI-700 family Network-on-Chip devices, including NI-700, NI-710AE, NOC-S3, and SI-L1 part IDs. It discovers clock domains and monitorable NI units, registers one perf PMU per clock domain, exposes node-type events requiring user-specified `nodeid` and `eventid`, and manages counters/overflow interrupts.

Important APIs and types: Core structures are `struct arm_ni`, `struct arm_ni_cd`, `struct arm_ni_unit`, and `struct arm_ni_node`. Perf callbacks are `arm_ni_event_init()`, `arm_ni_event_add()`, `arm_ni_event_del()`, `arm_ni_event_start()`, `arm_ni_event_stop()`, `arm_ni_event_read()`, and PMU enable/disable. Discovery/setup uses `arm_ni_probe()`, `arm_ni_probe_domain()`, `arm_ni_init_cd()`, `arm_ni_get_pmusel()`, and `arm_ni_init_irqs()`.

Control flow: Probe maps the full NI configuration space without claiming it all, validates the global node, reads part ID, counts clock domains by walking global -> voltage -> power -> clock-domain nodes, allocates a flex-array `struct arm_ni`, and initializes each CD. `arm_ni_init_cd()` walks child units, discovers PMU and node units, verifies non-secure access by writing/readback to PMUSEL/FCU selection registers, requests the PMU page, resets counters, registers a PMU named `arm_ni_<id>_cd_<cd>`, and stores PMU IRQ data. IRQ initialization handles shared IRQs through `irq_friend`, sets affinity to the selected CPU, enables overflow interrupts, and explicitly enables non-friend IRQs. Event init rejects sampling, pins events to the selected CPU, validates cycle-count vs unit events, and stores the matching `arm_ni_unit` in `hw.config_base`. Add allocates either the cycle counter or one of eight event counters, updates the per-unit PMUSEL byte array, writes PMEVTYPER node type/id, seeds the counter to half-range, and starts if requested. IRQs read overflow bits, update/reload active counters, clear overflow status, and follow shared-IRQ friends.

State and persistence: Driver state includes the mapped base, part/id, selected CPU, per-CD PMU base, IRQ, unit list, PMUSEL shadow bytes, active event pointer arrays, and CPU hotplug node. Hardware state includes PMCR, PMUSEL/FCU selectors, PMEVTYPER node routing, 32-bit event counters, 64-bit cycle counter, interrupt enables, overflow status, and IRQ affinity. Event state persists until deletion; remove disables PMUs and PMINTEN, unregisters per-CD PMUs, and removes hotplug state.

Dependencies and integration points: Integrates with Linux perf, platform resources, OF compatible `arm,ni-700`, ACPI HID `ARMHCB70`, IRQ/hotplug APIs, and MMIO helpers including non-atomic lo-hi 64-bit writes. The sysfs ABI exposes event groups for ASNI/AMNI/HSNI/HMNI/PMNI/TSNI/TMNI/CMNI and format fields `type`, `nodeid`, and `eventid`.

Risks: PMUSEL access is security/firmware dependent; inaccessible units are hidden, but incorrect readback assumptions could expose unusable events. The code assumes discovered CD IDs fit the allocated `cds[]` index space. Shared IRQ friend traversal depends on CD array adjacency. NI-7xx has different counter/PMUSEL offsets than later parts, tracked through `hw.flags`; offset mistakes produce silent counter corruption. Event groups are only capacity-validated, not semantically validated against per-node event IDs.

Test signals: Probe on supported firmware paths, verify one PMU per accessible clock domain, inspect event visibility for inaccessible units, run cycle and node events with explicit nodeid/eventid, fill all eight event counters plus cycle counter, trigger overflow interrupts, test shared IRQs, CPU hotplug migration, and remove/reprobe with PMINTEN cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm-ni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.c

Purpose: Provides ARM64 Branch Record Buffer Extension support for the Arm PMU perf branch-stack path. It probes BRBE capability, validates perf branch sample filters, programs BRBCR/BRBFCR system registers, invalidates branch records, reads banked BRBE entries, converts BRBINF metadata into `perf_branch_entry` fields, and applies per-event filtering before returning a branch stack.

Important APIs and types: Public functions exported through the local header are `brbe_probe()`, `brbe_num_branch_records()`, `brbe_invalidate()`, `brbe_enable()`, `brbe_disable()`, `brbe_branch_attr_valid()`, and `brbe_read_filtered_entries()`. Internal helpers include register index switch macros for `SYS_BRBSRC_EL1(n)`, `SYS_BRBTGT_EL1(n)`, `SYS_BRBINF_EL1(n)`, validation helpers for BRBIDR/ID_AA64DFR0 fields, `branch_type_to_brbfcr()`, `branch_type_to_brbcr()`, `perf_entry_from_brbe_regset()`, `prepare_event_branch_type_mask()`, and branch privilege/type filters.

Control flow: `brbe_probe()` reads `ID_AA64DFR0_EL1` and `BRBIDR0_EL1`, accepting only supported BRBE versions, record counts, format 0, and 20-bit cycle count encoding, then stores `reg_brbidr` in `struct arm_pmu`. During perf event initialization, `brbe_branch_attr_valid()` rejects unsupported branch filters and stores precomputed BRBFCR and BRBCR values in `event->hw.branch_reg` and `extra_reg`. `brbe_enable()` invalidates stale records, ORs the permitted filters from all active branch-stack events on the CPU, handles VHE `BRBCR_EL12` guest masking, writes BRBCR, then unpauses BRBE through BRBFCR. `brbe_read_filtered_entries()` builds a desired perf branch-type bitmap, iterates BRBE banks of 32 records, reads entries until an invalid record, maps source/target/type/cycles/prediction/privilege, drops or masks records that do not match the event's requested branch type or privilege, and writes `branch_stack->nr`.

State and persistence: Most state is per-CPU architectural BRBE system registers and the PMU's `reg_brbidr` capability field. Per-event filter state is cached in perf hardware register fields. Branch records persist in the hardware buffer until invalidated, overwritten, paused, or disabled. The driver has no heap allocation or module-owned mutable global state.

Dependencies and integration points: Depends on ARM64 system register definitions, `linux/perf/arm_pmu.h`, perf branch-stack ABI flags, bitmap helpers, privilege helpers such as `is_kernel_in_hyp_mode()`, and `access_ok()` for user/kernel address filtering. It is compiled behind `CONFIG_ARM64_BRBE` and called by the ARM PMU driver through `arm_brbe.h`.

Risks: BRBE programming is sensitive to synchronization; bank selection requires ISB before record access, and enable ordering must avoid stale or discontinuous records. The hardware is programmed with an OR of filters across all active events, so software post-filtering must correctly mask/drop records per event. `access_ok()` address classification is only a proxy for privilege and must stay aligned with how BRBINF privilege is interpreted. New perf branch ABI bits are guarded by `BUILD_BUG_ON`, so ABI expansion requires deliberate support. VHE/nVHE/guest behavior is subtle, especially for HV filters and BRBCR_EL12 writes.

Test signals: Build with and without `CONFIG_ARM64_BRBE`, verify `brbe_probe()` detects supported CPUs and rejects unsupported BRBIDR formats, run `perf record -j` with each allowed branch filter, confirm rejected filters fail cleanly, test user-only/kernel-only/mixed privilege captures, VHE host behavior, buffer sizes 8/16/32/64 records, cycle/no-cycle and flags/no-flags modes, and branch-stack correctness around PMU overflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.h -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.h

Purpose: Declares the BRBE helper interface used by the ARM PMU perf driver and provides safe stubs when `CONFIG_ARM64_BRBE` is disabled.

Important APIs and types: Forward-declares `struct arm_pmu`, `struct perf_branch_stack`, and `struct perf_event`. Under `CONFIG_ARM64_BRBE`, it declares `brbe_probe()`, `brbe_num_branch_records()`, `brbe_invalidate()`, `brbe_enable()`, `brbe_disable()`, `brbe_branch_attr_valid()`, and `brbe_read_filtered_entries()`. The disabled configuration returns zero/no-op for capability/control helpers and makes branch-stack validation fail with a warning if called on a branch-stack event.

Control flow: There is no runtime control flow in enabled builds beyond function linkage. In disabled builds, callers can compile unchanged: probing does nothing, branch record count is zero, enable/disable/invalidate are no-ops, branch attribute validation returns false, and filtered read leaves the stack untouched.

State and persistence: The header owns no state. It defines the compile-time contract between the ARM PMU core and `arm_brbe.c`, including the behavior when BRBE support is absent.

Dependencies and integration points: Depends on ARM PMU/perf types and the `CONFIG_ARM64_BRBE` Kconfig symbol. The stubs call `has_branch_stack()` and `WARN_ON_ONCE()`, so include order must provide those declarations through the ARM PMU/perf context.

Risks: Signature drift breaks ARM PMU integration at compile time. The disabled stub for `brbe_read_filtered_entries()` is declared `static` rather than `static inline`, which is acceptable for a header-local no-op but should not grow logic. Callers must still gate branch-stack support on `brbe_branch_attr_valid()` or record count.

Test signals: Compile both BRBE-enabled and disabled configurations, verify no unresolved symbols, and confirm branch-stack events are rejected cleanly when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_brbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Kconfig

Purpose: Defines build configuration options for the generic ARM CoreSight Architecture PMU driver and its NVIDIA and Ampere vendor/implementer backends.

Important APIs and types: Provides tristate symbols `ARM_CORESIGHT_PMU_ARCH_SYSTEM_PMU`, `NVIDIA_CORESIGHT_PMU_ARCH_SYSTEM_PMU`, and `AMPERE_CORESIGHT_PMU_ARCH_SYSTEM_PMU`. The generic driver depends on `ARM64 || COMPILE_TEST`; vendor options depend on the generic symbol.

Control flow: Kconfig selection controls whether `arm_cspmu_module.o`, `nvidia_cspmu.o`, and `ampere_cspmu.o` are compiled as built-in, module, or omitted. Vendor backend symbols cannot be enabled unless the generic CoreSight PMU architecture driver is enabled.

State and persistence: No runtime state. The file persists build-time feature availability and module dependency relationships.

Dependencies and integration points: Consumed by the perf drivers Makefile and kernel configuration system. Help text clarifies this is the CoreSight PMU architecture, not CoreSight self-hosted tracing, and notes Ampere's initial MCU PMU focus.

Risks: Vendor backend dependencies must match the runtime registration model in `arm_cspmu.c`; if a backend can be built without the generic driver, symbols such as `arm_cspmu_impl_register()` would fail. The Ampere stanza has whitespace inconsistency but no behavioral impact.

Test signals: `make menuconfig` visibility, all three tristate combinations, module dependency/modprobe behavior, and compile-test builds on non-ARM64 validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Makefile

Purpose: Connects the CoreSight PMU Kconfig symbols to object files built by Kbuild.

Important APIs and types: Builds `arm_cspmu_module.o` when `CONFIG_ARM_CORESIGHT_PMU_ARCH_SYSTEM_PMU` is set, with `arm_cspmu_module-y := arm_cspmu.o`. Builds `nvidia_cspmu.o` and `ampere_cspmu.o` under their respective vendor Kconfig symbols.

Control flow: Kbuild includes the listed objects as built-ins or modules according to each config symbol. The generic object is wrapped in a module name distinct from the source file, while vendor backends build as direct module objects.

State and persistence: No runtime state. It persists build linkage and module object naming.

Dependencies and integration points: Integrates with `drivers/perf` Kbuild and the Kconfig symbols in the same directory. Runtime vendor backend loading in `arm_cspmu.c` expects module names `nvidia_cspmu` and `ampere_cspmu`, matching this Makefile.

Risks: Renaming vendor objects without updating `module_name` in `arm_cspmu.c` would break request-module/deferred-probe behavior. Adding source files to the generic module requires extending `arm_cspmu_module-y`.

Test signals: Build the generic driver as built-in and module, build each vendor backend as module, and verify `modprobe nvidia_cspmu`/`modprobe ampere_cspmu` satisfies generic deferred probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/ampere_cspmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/ampere_cspmu.c

Purpose: Implements the Ampere vendor backend for ARM CoreSight Architecture PMUs, initially for AmpereOne MCU PMUs. It supplies Ampere-specific event names, format fields, PMU naming, filter programming, and validation for shared MCU filters.

Important APIs and types: Defines `struct ampere_cspmu_ctx`, AmpereOne MCU event/format attribute arrays, extractor helpers for `event`, `threshold`, `rank`, and `bank`, and backend callbacks `ampere_cspmu_get_event_attrs()`, `ampere_cspmu_get_format_attrs()`, `ampere_cspmu_get_name()`, `ampere_cspmu_set_cc_filter()`, `ampere_cspmu_set_ev_filter()`, `ampere_cspmu_validate_event()`, and `ampere_cspmu_init_ops()`. Registers via `arm_cspmu_impl_register()` with implementer ID `ARM_CSPMU_IMPL_ID_AMPERE`.

Control flow: Module init registers an implementer match. When the generic driver sees an Ampere PMIIDR, it calls `ampere_cspmu_init_ops()`, which allocates context, points to static AmpereOne event/format tables, allocates a unique `ampere_mcu_pmu_%d` name through an IDA, stores context in `cspmu->impl.ctx`, and overrides generic callbacks. Event start in the generic driver calls the backend filter hooks; regular events write threshold, rank, and bank to `PMAUXR0..2`, while cycle-counter filtering is a dummy because `PMCCFILTR` is RES0. Validation requires all events in the group and already active hardware events to use the same global filter tuple.

State and persistence: Static event tables are immutable. Runtime state is per-PMU devm context plus names allocated from `mcu_pmu_ida`; filter values persist in PMAUXR registers while events are active. There is no explicit IDA free path in the backend, so IDs are monotonically allocated for the module lifetime.

Dependencies and integration points: Depends on `arm_cspmu.h`, generic CoreSight PMU backend registration, MMIO writes, module infrastructure, and topology headers. Integrated entirely through `struct arm_cspmu_impl_ops`.

Risks: MCU PMU filters are global, so allowing mismatched threshold/rank/bank among concurrent events would produce misleading counts; this file explicitly prevents that. Event tables encode vendor hardware ABI and need vendor documentation alignment. PMCCFILTR writes are suppressed because the register is RES0; removing the override could cause unnecessary writes. The IDA allocation is not released on remove, which is acceptable for small module-lifetime IDs but worth noting for repeated bind/unbind tests.

Test signals: Build/load `ampere_cspmu`, confirm deferred generic PMU probes bind after backend registration, inspect `events` and `format` sysfs files, run multiple MCU events with matching filters, verify mismatched group/active filters fail, run `cycles`, and confirm PMAUXR writes through register tracing or hardware counter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/ampere_cspmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.c

Purpose: Implements the generic ARM CoreSight PMU architecture perf driver for MMIO uncore PMUs described by ACPI APMT or device tree. It provides default event/filter ABI, counter management, overflow IRQ handling, CPU affinity/hotplug ownership, PMU registration, and a backend registration mechanism for implementer-specific attributes and filter semantics.

Important APIs and types: Main data type is `struct arm_cspmu` from `arm_cspmu.h`, with `struct arm_cspmu_hw_events`, `struct arm_cspmu_impl`, and `struct arm_cspmu_impl_ops`. Public exports are `arm_cspmu_sysfs_event_show()`, `arm_cspmu_acpi_dev_get()`, `arm_cspmu_impl_register()`, and `arm_cspmu_impl_unregister()`. Key internal paths include `arm_cspmu_init_mmio()`, `arm_cspmu_init_impl_ops()`, `arm_cspmu_alloc_attr_groups()`, `arm_cspmu_event_init()`, `arm_cspmu_add()/del()`, `arm_cspmu_start()/stop()/read()`, `arm_cspmu_handle_irq()`, CPU association helpers, and platform probe/remove.

Control flow: Probe allocates a PMU object, maps page 0 and optional page 1, reads PMCFGR to determine counter count, counter width, cycle-counter support and logical-to-physical mapping, requests an optional overflow IRQ, determines associated CPUs from APMT, DT `cpus`, or all possible CPUs, then initializes implementer ops. Backend discovery reads PMIIDR or reconstructs it from PMPIDR registers, applies APMT override if present, matches NVIDIA/Ampere implementers, requests backend modules on demand, and pins the backend module during PMU registration. Attribute groups are allocated from backend or default callbacks. Event init rejects sampling/per-task events, validates CPU association, pins events to the active CPU, validates group counter capacity and backend constraints, and stores decoded event type. Add allocates logical counters, maps the cycle counter to physical index 31 when needed, and starts if requested. Start programs period, event type, and CC/event filters, then enables counter interrupt and count bits. IRQ handling stops all counters, reads/clears overflow status across SET/CLR banks, updates/reloads overflowed events, and restarts counters. Hotplug moves active ownership and IRQ affinity to another associated CPU.

State and persistence: Runtime state includes MMIO bases, PMCFGR capabilities, counter arrays/bitmaps, logical cycle-counter index, optional IRQ, associated/active CPU masks, sysfs attribute groups, implementer context, and platform driver data. Hardware state includes PMCR, PMEVTYPER, PMEVFILTR/PMEVFILT2R, PMCCFILTR, counter registers, enable/interrupt SET/CLR registers, and overflow status. Backend module pointers are temporarily held during registration and then installed in `pmu.module` for lifetime management by perf.

Dependencies and integration points: Uses Linux perf PMU APIs, platform driver APIs, ACPI APMT data, optional OF `cpus`, IRQ APIs, CPU hotplug, MMIO helpers including atomic/non-atomic 64-bit counter access, and dynamically registered NVIDIA/Ampere backend modules. User integration is through `/sys/bus/event_source/devices/<name>/events`, `format`, `identifier`, `cpumask`, and `associated_cpus`.

Risks: 64-bit counter access must honor APMT atomic flags or DT `reg-io-width`; the hi-lo-hi fallback can time out and return zero. Backend module loading/deferred probe depends on exact module names and implementer masks. Optional IRQ absence sets `PERF_PMU_CAP_NO_INTERRUPT`, so overflow behavior differs between platforms. Cycle-counter logical index remapping is subtle when regular counter count is below 31. Backend validation must be invoked before setting used bits to avoid leaked allocation state on errors. CPU hotplug must keep perf context and IRQ affinity aligned with `active_cpu`.

Test signals: Build generic-only and with vendor modules, probe via ACPI APMT and DT, verify sysfs ABI and PMU names, run default `cycles` and raw events with filters, test no-IRQ mode, force overflows with IRQ mode, validate 32-bit and 64-bit counters with and without atomic dword access, exercise backend deferred-probe/module-unregister paths, and offline/online associated CPUs while events are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.h -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.h

Purpose: Defines the shared register constants, attribute helpers, data structures, implementer-backend contracts, and exported helper prototypes for the ARM CoreSight PMU architecture driver and vendor modules.

Important APIs and types: Provides register offsets and bitfields for PMEV counters, filters, PMCR, PMCFGR, PMIIDR/PMPIDR, event/filter masks, default format/event attribute macros, implementer IDs, and maximum counter constants. Defines `struct arm_cspmu_hw_events`, `struct arm_cspmu_impl_ops`, `struct arm_cspmu_impl_match`, `struct arm_cspmu_impl`, and `struct arm_cspmu`. Declares `arm_cspmu_sysfs_event_show()`, `arm_cspmu_impl_register()`, `arm_cspmu_impl_unregister()`, and ACPI helper `arm_cspmu_acpi_dev_get()` with a stub outside ACPI+ARM64.

Control flow: The header has no executable runtime logic except the ACPI helper stub. It establishes callback flow: generic probe fills default `arm_cspmu_impl_ops`, vendor modules register an `arm_cspmu_impl_match`, and the generic driver calls backend hooks for attributes, naming, event decoding, filter programming, reset, and validation.

State and persistence: No direct state. Structure fields define persistent runtime ownership for PMU device state, counter bitmaps, active CPU masks, MMIO bases, implementation context, and sysfs attribute group pointers.

Dependencies and integration points: Included by `arm_cspmu.c`, `nvidia_cspmu.c`, and `ampere_cspmu.c`. Pulls in Linux ACPI, device, cpumask, perf, platform, module, bitfield, and type headers. The exported registration prototypes are the link contract for vendor backend modules.

Risks: Register definitions are shared by all backends; incorrect offsets or masks break generic and vendor behavior. `ARM_CSPMU_MAX_HW_CNTRS` sizes bitmaps and arrays and must match architectural limits. Callback semantics must remain stable because backend modules may be loaded separately from the generic module. Attribute macros create compound-literal attributes, so use remains intended for static attribute arrays.

Test signals: Compile all generic/vendor combinations, inspect generated sysfs format strings, validate PMIIDR implementer matching, and run sparse/build checks for structure and callback signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/arm_cspmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/nvidia_cspmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/nvidia_cspmu.c

Purpose: Implements NVIDIA-specific backend support for ARM CoreSight Architecture PMUs. It maps NVIDIA PMIIDR product IDs to named uncore PMU personalities, supplies event/format attributes, default filter behavior, product-specific validation, PCIE target address filter management, and PMU naming by socket/instance.

Important APIs and types: Uses `struct nv_cspmu_ctx`, `struct nv_cspmu_match`, `struct pcie_tgt_data`, and `struct pcie_tgt_addr_filter`. Backend callbacks include `nv_cspmu_get_event_attrs()`, `nv_cspmu_get_format_attrs()`, `nv_cspmu_get_name()`, `nv_cspmu_set_ev_filter()`, `nv_cspmu_reset_ev_filter()`, `nv_cspmu_set_cc_filter()`, `pcie_v2_pmu_validate_event()`, `pcie_tgt_pmu_validate_event()`, `pcie_tgt_pmu_set_ev_filter()`, `pcie_tgt_pmu_reset_ev_filter()`, `pcie_tgt_pmu_event_type()`, `pcie_tgt_pmu_is_cycle_counter_event()`, and `nv_cspmu_init_ops()`. Module init/exit call `arm_cspmu_impl_register()/unregister()` for NVIDIA implementer ID.

Control flow: Generic CSPMU probe invokes `nv_cspmu_init_ops()` for NVIDIA PMUs. The backend selects a product match by PMIIDR product/variant/revision mask, copies a template context, formats a PMU name using socket and optional ACPI `instance_id`, stores context, and overrides generic ops from either match-specific callbacks or NVIDIA defaults. Generic event start later calls NVIDIA filter callbacks: simple PMUs use `config1`/`config2` masked values with defaults when zero, UCF expands empty source/destination fields to all sources/destinations, PCIE v2 enforces global BDF filter consistency and mutual exclusion with root-port filters, and PCIE target events program separate address-filter registers with refcounted slots before selecting them in PMEVFILT2R. Generic stop calls reset hooks where present to clear filters and release address slots.

State and persistence: Static event and format tables define SCF, MCF, UCF, PCIE v2, PCIE target, NVLink/CNVLink, and generic PMU ABIs. Per-PMU state is devm context with masks/defaults/callbacks and optional PCIE target data. PCIE target state tracks up to eight address filter slots with base/mask/refcount and an ioremapped resource from the associated ACPI device. Hardware filter registers and target address windows persist while events are active.

Dependencies and integration points: Depends on `arm_cspmu.h`, topology for socket naming, ACPI helper `arm_cspmu_acpi_dev_get()`, firmware property `instance_id`, ACPI memory resources for PCIE target address filters, MMIO helpers, and generic CSPMU backend registration. PMU names such as `nvidia_pcie_pmu_%u_rc_%u` are consumed by perf users.

Risks: Product ID matching controls all user-visible ABI; a missing or too-broad match can expose wrong events/filters. PCIE v2 has one common BDF filter setting across counters, enforced in validation; bypassing this would mix counts. PCIE target address filters have shared finite slots and refcounts; leaks or underflows can leave address windows enabled or disable windows still in use. Name formatting can fail when ACPI instance ID is unavailable for socket-instance products. Default-zero filter expansion must match hardware expectations for "monitor all".

Test signals: Load `nvidia_cspmu` after/before generic probe to exercise deferred attach, verify PMU names for socket and RC instance formats, inspect events/format files for each product ID, run events with default and explicit filters, validate PCIE v2 BDF/root-port rejection cases and group consistency, allocate/reuse/exhaust PCIE target address filters, stop events and confirm filters are cleared/refcounts decremented, and test backend unregister unbinds matching generic devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_cspmu/nvidia_cspmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_dmc620_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_dmc620_pmu.c

Purpose: Implements the perf PMU driver for the Arm DMC-620 memory controller. It exposes clkdiv2 and clk event aliases, supports programmable mask/match/invert/increment/event fields, manages ten hardware counters, shares IRQ objects across PMU instances using the same interrupt, and handles overflow/reload and CPU hotplug migration.

Important APIs and types: Core structures are `struct dmc620_pmu` and shared `struct dmc620_pmu_irq`. PMU callbacks include `dmc620_pmu_event_init()`, `dmc620_pmu_add()`, `dmc620_pmu_del()`, `dmc620_pmu_start()`, `dmc620_pmu_stop()`, and `dmc620_pmu_read()`. Support functions include `dmc620_get_event_idx()`, `dmc620_event_to_counter_control()`, `dmc620_pmu_event_update()`, `dmc620_pmu_event_set_period()`, `dmc620_pmu_handle_irq()`, `dmc620_pmu_get_irq()`, and `dmc620_pmu_put_irq()`.

Control flow: Probe allocates a PMU, maps the PMU resource, disables all counters, clears overflow status, gets the platform IRQ, attaches to or creates a shared `dmc620_pmu_irq`, formats a PMU name from the physical address, and registers with perf. Event init rejects sampling/task events, pins events to the shared IRQ CPU, and rejects groups containing more than one hardware event because the hardware cannot atomically disable all counters. Add allocates a counter from the clkdiv2 pool or clk pool based on `clkdiv2`, writes mask/match registers, seeds state, and starts if requested. Start writes a half-range period and enables the counter with control bits derived from config fields. IRQ handling iterates all PMUs attached to the shared IRQ under RCU, disables active counters to avoid clear races, reads both overflow status banks, updates/reloads overflowed events, clears status registers, and re-enables non-stopped events. Hotplug migrates all PMU contexts sharing an IRQ and moves IRQ affinity to a surviving CPU.

State and persistence: Per-PMU state holds MMIO base, shared IRQ pointer, RCU list node, used-counter bitmap, and event pointers. Shared IRQ state holds list nodes, PMU list, refcount, IRQ number, and owner CPU. Hardware state includes per-counter mask/match/control/value registers and clkdiv2/clk overflow status. State persists across events until deletion; remove unregisters PMU and releases shared IRQ state after RCU synchronization.

Dependencies and integration points: Uses Linux perf uncore APIs, ACPI HID `ARMHD620`, platform resources/IRQs, cpuhotplug, IRQ affinity, RCU lists, mutexes, refcounts, and MMIO accessors. Sysfs exposes event aliases, format fields, and cpumask for perf tooling.

Risks: Shared IRQ lifetime is subtle: PMUs are on RCU lists while IRQ handling can traverse them, and removal must preserve ordering with perf unregister/devres. Group rejection is an important correctness workaround for non-atomic global disable; weakening it can race overflow clearing. Counter status masks split clkdiv2 and clk domains and must align with counter index pools. `for_each_set_bit(idx, &status, ...)` relies on local unsigned long layout for a small status value. Hotplug migration uses mutex rather than RCU and must keep IRQ CPU and perf contexts aligned.

Test signals: Probe multiple DMC-620 instances sharing and not sharing IRQs, verify sysfs events/formats, run clkdiv2 and clk events with mask/match filters, fill each counter pool, verify hardware event groups are rejected but software companions work, force overflow IRQs, remove/reprobe under load, and offline the owner CPU while events are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_dmc620_pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_dsu_pmu.c -->
# sources/distributed-fs/ceph-client/drivers/perf/arm_dsu_pmu.c

Purpose: Implements the perf PMU driver for Arm DynamIQ Shared Unit cluster PMUs. It discovers CPUs associated with a DSU, probes DSU PMU capabilities from an active CPU, exposes architected event aliases when supported, manages event and cycle counters, handles overflow interrupts, and migrates PMU ownership across CPU hotplug.

Important APIs and types: Main structures are `struct dsu_pmu` and `struct dsu_hw_events`. PMU callbacks are `dsu_pmu_event_init()`, `dsu_pmu_add()`, `dsu_pmu_del()`, `dsu_pmu_start()`, `dsu_pmu_stop()`, `dsu_pmu_read()`, `dsu_pmu_enable()`, and `dsu_pmu_disable()`. Hardware helpers wrap arch-specific functions from `<asm/arm_dsu_pmu.h>`, including counter read/write, PMCR access, event selection, interrupt enable/disable, PMCEID probing, and overflow reset. Probe and hotplug paths use `dsu_pmu_device_probe()`, `dsu_pmu_probe_pmu()`, `dsu_pmu_cpu_online()`, and `dsu_pmu_cpu_teardown()`.

Control flow: Platform probe allocates the PMU, parses associated CPUs from DT `cpus` phandles or ACPI cluster parent relationship, requests the overflow IRQ, registers a CPU hotplug instance, installs perf callbacks, and registers the PMU with a unique `arm_dsu_%d` name. The online callback for the first associated CPU probes PMCR counter count, PMCEID event availability, 32-bit vs 64-bit event counter width, and whether PMCCNTR exists, then sets active CPU and IRQ affinity. Event init rejects sampling, task-bound events, branch stacks, and CPUs outside the associated mask; it then pins events to the active CPU, validates group counter capacity, and stores event code and width flag. Add allocates the dedicated cycle counter for cycles when available or a generic counter otherwise. Start reloads period, programs event type for non-cycle counters, clears state, and enables counter interrupts/counting. IRQ handling reads and clears overflow bits, updates/reloads each overflowed active event, and returns handled status.

State and persistence: Runtime state includes PMU lock, used counter bitmap and event pointers, associated and active CPU masks, hotplug node, number of counters, IRQ number, counter-width/cycle-counter capability flags, and PMCEID bitmap. Hardware state includes DSU PMCR enable/reset bits, selected event types, counter values, interrupt enables, and overflow status. Active CPU ownership persists until hotplug migration or remove.

Dependencies and integration points: Depends on Linux perf, OF compatible `arm,dsu-pmu`, ACPI HID `ARMHD500`, platform IRQs, CPU hotplug, cpumask/sysfs helpers, and architecture DSU PMU assembly/system-register helpers. Perf users consume `events`, `format`, `cpumask`, and `associated_cpus` sysfs groups.

Risks: DSU PMU registers must be accessed only from associated CPUs; read/write paths warn and return if executed elsewhere. Capability probing is delayed until an associated CPU is online, so event init before active CPU assignment fails. PMCEID visibility hides unsupported common events, but raw config values can still be requested and rely on hardware behavior. 32-bit non-cycle counters and optional PMCCNTR require correct mask/index handling. Hotplug must leave IRQ disabled if no associated CPU remains online and migrate context before changing active affinity when possible.

Test signals: Probe via DT and ACPI, verify associated CPU masks, sysfs event visibility from PMCEID, run cycles with and without PMCCNTR support, run common DSU events, fill available counters and validate groups, force overflow IRQs for 32-bit and 64-bit counter modes, test branch-stack rejection, and offline/online CPUs in the DSU cluster while perf events run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/perf/arm_dsu_pmu.c -->
