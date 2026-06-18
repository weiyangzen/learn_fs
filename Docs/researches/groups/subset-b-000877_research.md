# subset-b-000877 research

Grouped source-tree-aligned research for x86 platform, Xen, UAPI, KVM, and ACPI files under `sources/distributed-fs/ceph-client`. Each section is bounded for reconciliation into the mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/x86_init.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/x86_init.h

Purpose: Defines x86 platform initialization and runtime callback tables. It is the main contract by which native PC, hypervisor, encrypted guest, ACPI, PCI, timer, interrupt, memory-resource, and CPU hotplug code override default x86 behavior without hard-coding platform tests at every call site.

Important APIs/types/functions: `struct x86_init_ops`, `x86_init_resources`, `x86_init_mpparse`, `x86_init_irqs`, `x86_init_oem`, `x86_init_paging`, `x86_init_timers`, `x86_init_iommu`, `x86_init_pci`, `x86_hyper_init`, `x86_init_acpi`, `x86_cpuinit_ops`, `x86_platform_ops`, `x86_hyper_runtime`, `x86_guest`, `x86_apic_ops`, `x86_legacy_features`, `x86_legacy_i8042_state`; globals `x86_init`, `x86_cpuinit`, `x86_platform`, `x86_msi`, `x86_apic_ops`; no-op helpers such as `x86_init_noop`, `bool_x86_init_noop`, `set_rtc_noop`, and `get_rtc_noop`.

Control flow: Early boot code and subsystem initializers call through these tables after platform detection has installed the right callbacks. The flow is deliberately indirect: MP table parsing, ROM/resource reservation, interrupt mode selection, page-table setup, timer/wallclock setup, ACPI root pointer handling, PCI initialization, hypervisor late init, CPU hotplug clock setup, and encrypted-memory transitions all dispatch through function pointers.

State and persistence behavior: Persistent state is the global callback tables and embedded legacy-feature flags. Guest encryption callbacks coordinate private/shared memory transitions and kexec conversion windows but do not store memory metadata themselves. Runtime wallclock, sched clock, NMI, APIC, IOMMU shutdown, and real-mode trampoline hooks mutate external platform state.

Dependencies and integration points: Forward declarations touch `ghcb`, `pt_regs`, `cpuinfo_x86`, `irq_domain`, and ACPI/PCI/interrupt concepts. Integrates with boot setup, SMP hotplug, APIC/MSI, ACPI, paravirtualization, SEV/TDX-style confidential computing, PAT, real-mode trampoline, RTC/wallclock, and x86 legacy device probing.

Risks and test signals: Main risks are NULL or stale callback wiring, wrong boot ordering, and platform callbacks that violate early-boot constraints. Test with native PC boot, Xen/KVM guest boot, SEV/TDX memory encryption transitions, CPU hotplug, PCI/MSI enumeration, ACPI reduced-hardware boot, kexec, suspend/resume, and builds across 32-bit, 64-bit, SMP, ACPI, PCI, and hypervisor configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/x86_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/cpuid.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/cpuid.h

Purpose: Documents and defines Xen CPUID leaves for x86 guests, including Xen signature discovery, Xen version reporting, hypercall page count/MSR base, time-source details, HVM feature bits, and PV machine-address width reporting.

Important APIs/types/functions: Macros `XEN_CPUID_FIRST_LEAF`, `XEN_CPUID_LEAF`, signature constants, `XEN_CPUID_FEAT1_MMU_PT_UPDATE_PRESERVE_AD`, TSC feature and mode constants, HVM feature flags such as `XEN_HVM_CPUID_IOMMU_MAPPINGS`, `XEN_HVM_CPUID_EXT_DEST_ID`, `XEN_HVM_CPUID_UPCALL_VECTOR`, `XEN_CPUID_MACHINE_ADDRESS_WIDTH_MASK`, and `XEN_CPUID_MAX_NUM_LEAVES`.

Control flow: This header owns no executable flow; Xen-aware detection code issues CPUID at the Xen leaf base and branches on the returned signature and feature bits.

State and persistence behavior: No kernel state is stored here. Values are ABI constants whose meaning persists across guest boot, migration, and userspace/tooling expectations.

Dependencies and integration points: Integrated with Xen guest discovery, clocksource/TSC setup, HVM interrupt routing, IOMMU mapping assumptions, and hypercall page setup. Consumers also pair it with `xen_cpuid_base()` in `hypervisor.h`.

Risks and test signals: ABI drift is the primary risk. Test by booting PV, HVM, and PVH guests on Xen hosts with and without Viridian leaves, checking Xen signature discovery, TSC mode handling, event upcall vector support, high APIC/MSI destination IDs, and migration-time TSC incarnation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/cpuid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/events.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/events.h

Purpose: Provides x86-specific Xen event-channel and IPI definitions, plus helpers for interrupt-state checks and event-channel rebind capability.

Important APIs/types/functions: `enum ipi_vector` with `XEN_RESCHEDULE_VECTOR`, function-call, spin-unlock, IRQ-work, and NMI vectors; `xen_irqs_disabled()`, `xchg_xen_ulong`, `xen_have_vector_callback`, `xen_support_evtchn_rebind()`, and `xen_percpu_upcall`.

Control flow: Xen event code calls `xen_irqs_disabled()` while handling upcalls and uses `xen_support_evtchn_rebind()` to decide whether event channels can be moved away from vCPU 0. The decision depends on PV/HVM mode and vector-callback availability.

State and persistence behavior: Persistent state is external: `xen_have_vector_callback` and `xen_percpu_upcall` record feature selection. This header only exposes the state and uses x86 `xchg` as the ordering primitive.

Dependencies and integration points: Depends on Xen domain mode helpers and x86 interrupt flag decoding. Integrates with event channels, IPI delivery, IRQ work, NMI routing, and HVM callback-vector setup.

Risks and test signals: Risks include incorrect interrupt-flag interpretation, event-channel affinity bugs on HVM guests without vector callbacks, and missing memory ordering assumptions. Test with PV and HVM event delivery, per-CPU upcalls, IRQ affinity changes, suspend/resume, CPU hotplug, and high-rate event-channel workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypercall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypercall.h

Purpose: Implements the Linux x86 Xen hypercall calling convention. It wraps Xen hypercalls in inline assembly, hides 32-bit versus 64-bit register assignments, routes calls through a static call trampoline, and exposes typed helpers for common Xen operations.

Important APIs/types/functions: `xen_hypercall_func`, `DECLARE_STATIC_CALL(xen_hypercall, ...)`, `_hypercall0` through `_hypercall4`, `xen_single_call()`, `privcmd_call()`, `__xen_stac()`, `__xen_clac()`, `HYPERVISOR_*` wrappers for trap table, MMU update, GDT, callback, debug registers, descriptor updates, VA mappings, scheduler, timer, MCA, platform, memory, multicall, event channel, Xen version, console, physdev, grant table, vm assist, vCPU, suspend, HVM, PMU, and device-model ops; `MULTI_*` multicall builders.

Control flow: Callers enter a typed `HYPERVISOR_*` wrapper, which loads hypercall number in `a/eax` and arguments into the Xen ABI registers, emits a call to the static-call trampoline, and returns the result. Privcmd and dm_op paths wrap the hypercall in `STAC`/`CLAC` because the hypervisor accesses user buffers. PV-only sections expose trap/MMU multicall helpers.

State and persistence behavior: No private runtime state is stored here, but it relies on the global static-call target for the active hypercall page/trampoline. Multicall builders populate caller-owned `struct multicall_entry` objects and emit trace events.

Dependencies and integration points: Depends on x86 alternative/static-call infrastructure, SMAP, nospec branch support, page-table types, Xen public interfaces, and Xen tracepoints. Integrated with Xen PV MMU batching, grant tables, event channels, platform ops, suspend, device model, and privileged userspace `privcmd`.

Risks and test signals: Highest risks are register constraint mistakes, clobber omissions, SMAP window errors, and ABI mismatch between 32-bit and 64-bit. Test with Xen PV and HVM boots, MMU update stress, multicall batching traces, suspend/resume, grant-table mapping, privcmd ioctls, module builds, objtool validation, and compiler variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypercall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypervisor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypervisor.h

Purpose: Exposes core Xen hypervisor state and x86-specific Xen helpers used outside the hypercall wrapper: shared info pointers, Xen signature discovery, PV dom0 MSI restore, CPU hotplug registration, PVH setup, lazy-mode batching, and ACPI capability sanitization.

Important APIs/types/functions: `HYPERVISOR_shared_info`, `xen_start_info`, `XEN_SIGNATURE`, `xen_cpuid_base()`, `xen_initdom_restore_msi()`, `xen_arch_register_cpu()`, `xen_arch_unregister_cpu()`, `xen_pvh_init()`, `mem_map_via_hcall()`, `enum xen_lazy_mode`, per-CPU `xen_lazy_mode`, `enter_lazy()`, `leave_lazy()`, `xen_get_lazy_mode()`, and `xen_sanitize_proc_cap_bits()`.

Control flow: Xen initialization discovers the CPUID base, maps shared/start info, and registers optional platform hooks. MMU and CPU update paths enter and leave lazy mode around batched operations, using BUG checks to enforce nesting correctness.

State and persistence behavior: Persistent state includes the Xen shared-info pointer, start-info pointer, and per-CPU lazy-mode state. PVH and dom0 helpers alter boot memory maps, MSI state, and ACPI processor capability views in external subsystems.

Dependencies and integration points: Depends on x86 `cpuid_base_hypervisor()`, BUG checks, per-CPU variables, boot params, PCI, ACPI, and Xen domain config symbols. Integrates with Xen PV/PVH boot, dom0 ACPI, CPU hotplug, MSI restoration, and paravirtual MMU batching.

Risks and test signals: Risks include lazy-mode imbalance, wrong CPUID leaf selection, BUG-only stubs called in unsupported configs, and PVH memory-map mismatch. Test Xen PV, PVH, dom0, CPU hotplug, MSI restore after suspend/resume, ACPI processor reporting, and debug builds that catch lazy-mode nesting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface.h

Purpose: Defines the common x86 portion of Xen's guest ABI: guest-handle types, machine-to-physical virtual ranges, trap-table entries, shared-info architecture fields, vCPU context layout, PMU context layout, and emulated-instruction prefixes.

Important APIs/types/functions: `DEFINE_GUEST_HANDLE*`, `set_xen_guest_handle`, `xen_pfn_t`, `xen_ulong_t`, `MACH2PHYS_*`, `MAX_VIRT_CPUS`, reserved GDT macros, `struct trap_info`, `struct arch_shared_info`, `struct vcpu_guest_context`, `VGCF_*` flags, PMU structs `xen_pmu_amd_ctxt`, `xen_pmu_intel_ctxt`, `xen_pmu_regs`, `xen_pmu_arch`, `PMU_*`, `XEN_EMULATE_PREFIX`, and `XEN_CPUID`.

Control flow: This header defines data passed to hypercalls and shared pages. Boot and vCPU setup fill `vcpu_guest_context`; trap setup sends `trap_info` arrays; p2m management updates `arch_shared_info`; PMU interrupt handling exchanges `xen_pmu_arch` with Xen; selected instructions can be forced through Xen emulation by prefix macros.

State and persistence behavior: ABI state persists in shared info pages, vCPU contexts, p2m generation counters, trap tables, GDT/LDT frame references, control/debug registers, and PMU cached contexts. `p2m_generation` uses odd/even updates to let external readers detect in-progress changes.

Dependencies and integration points: Pulls in 32-bit or 64-bit subheaders and `pvclock-abi.h`. Integrated with Xen hypercalls, PV boot, PVH/HVM context setup, perf/PMU virtualization, trap/IDT setup, p2m/m2p translation, and toolstack save/restore.

Risks and test signals: Risks are packed layout drift, pointer-handle size mismatch, stale p2m generation handling, and differences between PV/HVM/PVH context semantics. Test Xen guest boot on 32-bit and 64-bit, save/restore/migration, PMU sampling, trap callback setup, p2m inspection from dom0, and ABI size checks against Xen headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_32.h

Purpose: Supplies 32-bit x86 Xen ABI details: flat segment selectors, trap instruction, hypervisor and machine-to-physical virtual ranges, 32-bit CPU register layout, vCPU info, callback shape, and CR3 PFN packing.

Important APIs/types/functions: `FLAT_RING1_*`, `FLAT_RING3_*`, `FLAT_KERNEL_*`, `FLAT_USER_*`, `TRAP_INSTR`, `__MACH2PHYS_*`, `__HYPERVISOR_VIRT_START`, `struct cpu_user_regs`, `tsc_timestamp_t`, `struct arch_vcpu_info`, `struct xen_callback`, `XEN_CALLBACK()`, `xen_pfn_to_cr3()`, and `xen_cr3_to_pfn()`.

Control flow: PV boot and hypercall paths use these constants to build selectors, callbacks, and CR3 values. Xen trap entry uses `int $0x82`; vCPU context code serializes `cpu_user_regs` for hypervisor interactions.

State and persistence behavior: State is ABI layout only. Callback addresses and CR3-encoded PFNs are stored in Xen vCPU contexts and shared structures outside this header.

Dependencies and integration points: Included by `interface.h` under `CONFIG_X86_32`. Integrated with PV trap handling, GDT selector setup, vCPU initialization, TSC timestamp ABI, and p2m/m2p virtual windows.

Risks and test signals: Risks include selector constants or CR3 packing regressions that break 32-bit PV guests. Test 32-bit Xen PV boot, context save/restore, callback delivery, high page-table base encoding, and compatibility with Xen public headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_64.h

Purpose: Supplies 64-bit x86 Xen ABI details: flat segment selectors, hypervisor and m2p virtual ranges, segment-base hypercall selectors, iret stack context, 64-bit CPU register layout, CR3 PFN conversion, vCPU info, and callback address encoding.

Important APIs/types/functions: `FLAT_RING3_CS32`, `FLAT_RING3_CS64`, `FLAT_KERNEL_*`, `FLAT_USER_*`, `__HYPERVISOR_VIRT_*`, `__MACH2PHYS_*`, `SEGBASE_*`, `VGCF_in_syscall`, `struct iret_context`, `struct cpu_user_regs`, `xen_pfn_to_cr3()`, `xen_cr3_to_pfn()`, `struct arch_vcpu_info`, `xen_callback_t`, and `XEN_CALLBACK()`.

Control flow: Xen PV entry/exit and vCPU save/restore code uses these layouts to represent guest registers, syscall versus iret return context, and segment base state. Callback setup passes a RIP-only callback value on 64-bit.

State and persistence behavior: No private state. ABI data persists in vCPU contexts, shared vCPU info, and hypervisor-maintained segment base state.

Dependencies and integration points: Included by `interface.h` on 64-bit builds. Integrates with PV syscall/iret paths, Xen segment-base hypercalls, GDT setup, m2p mapping, and vCPU context exchange.

Risks and test signals: Risks are register layout drift, syscall-return flag mishandling, and 64-bit selector compatibility bugs. Test 64-bit Xen PV boot, syscall and interrupt return paths, segment base updates, save/restore, migration, and ABI comparisons to Xen public headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/page.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/page.h

Purpose: Provides x86 Xen page, frame, and address-translation helpers. It converts between pseudo-physical, machine, guest, bus, virtual, PFN, MFN, and GFN address spaces and exposes p2m/m2p state used by Xen PV guests.

Important APIs/types/functions: `xmaddr_t`, `xpaddr_t`, `XEN_PHYSICAL_MASK`, `XEN_PTE_MFN_MASK`, `INVALID_P2M_ENTRY`, `FOREIGN_FRAME`, `IDENTITY_FRAME`, globals `machine_to_phys_mapping`, `machine_to_phys_nr`, `xen_p2m_addr`, `xen_p2m_size`, `xen_max_p2m_pfn`; helpers `xen_alloc_p2m_entry`, `get_phys_to_machine`, `set_phys_to_machine`, `set_phys_range_identity`, `set_foreign_p2m_mapping`, `clear_foreign_p2m_mapping`, `xen_safe_read_ulong`, `xen_safe_write_ulong`, `__pfn_to_mfn`, `pfn_to_mfn`, `mfn_to_pfn`, `phys_to_machine`, `machine_to_phys`, `pfn_to_gfn`, `gfn_to_pfn`, `bfn_to_local_pfn`, `virt_to_machine`, `mfn_pte`, and `xen_arch_need_swiotlb`.

Control flow: Translation helpers first short-circuit non-PV domains to identity mappings. PV paths consult the p2m array, fall back to extended lookup for sparse/out-of-range entries, mask indicator bits for public conversions, and verify m2p round trips before returning local PFNs. Safe read/write helpers use exception-table fixups for potentially faulting m2p accesses.

State and persistence behavior: Persistent state is the p2m table, m2p mapping window, max p2m bounds, and special indicator bits for invalid, foreign, and identity frames. Foreign mappings must be marked with `FOREIGN_FRAME()` so generic PFN validation does not mistake them for local pages.

Dependencies and integration points: Depends on Linux MM, PFN, device, exception table, page-table, Xen grant-table, and Xen domain helpers. Integrates with PV MMU, grant mapping, SWIOTLB/DMA decisions, page-table construction, and memory hotplug/sparse p2m handling.

Risks and test signals: Risks include mfn/pfn confusion, foreign-page aliasing, faulting m2p reads, SME physical mask mistakes, and wrong behavior outside PV. Test Xen PV boot, grant map/unmap, ballooning, sparse memory hotplug, p2m identity ranges, DMA on PV/HVM, page-table creation, and fault injection on m2p windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/pci.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/pci.h

Purpose: Declares Xen-specific PCI initialization and PCI frontend MSI/MSI-X hooks, with no-op or error stubs when the relevant Xen PCI options are disabled.

Important APIs/types/functions: `pci_xen_init()`, `pci_xen_hvm_init()`, `pci_xen_initial_domain()`, `pci_xen`, `struct xen_pci_frontend_ops`, `xen_pci_frontend`, and inline wrappers for frontend MSI/MSI-X enable/disable.

Control flow: PCI setup calls Xen init hooks based on configuration and domain type. MSI/MSI-X wrappers check whether `xen_pci_frontend` and its operation are installed, delegate when present, and return `-ENOSYS` or no-op otherwise.

State and persistence behavior: Persistent state is the global `xen_pci_frontend` operations pointer provided by Xen PCI frontend code. PCI device MSI state is mutated by the delegated operations.

Dependencies and integration points: Integrates with `CONFIG_PCI_XEN`, `CONFIG_XEN_PV_DOM0`, `CONFIG_PCI_MSI`, PCI device setup, Xen pcifront, HVM PCI initialization, and dom0 PCI ownership.

Risks and test signals: Risks include missing frontend ops, stubs compiled into unexpected configs, and MSI vector leakage during frontend failure paths. Test Xen dom0 and domU PCI probing, MSI/MSI-X enable and disable, HVM guest PCI init, pcifront load/unload, and non-Xen PCI builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/swiotlb-xen.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/swiotlb-xen.h

Purpose: Declares x86 Xen SWIOTLB and contiguous-region helpers used to make DMA buffers suitable for devices when Xen memory layout or address-bit constraints require bounce or contiguous machine frames.

Important APIs/types/functions: `xen_swiotlb_fixup()`, `xen_create_contiguous_region()`, and `xen_destroy_contiguous_region()`.

Control flow: DMA/SWIOTLB setup calls the fixup helper after buffer allocation; device mapping code can request contiguous machine memory by physical start, order, and address-bit limit and later destroy the region.

State and persistence behavior: This header owns no state, but the declared functions mutate Xen memory reservations, DMA handles, and SWIOTLB slab backing memory.

Dependencies and integration points: Integrates with Xen memory management, DMA mapping, SWIOTLB, device address masks, and boot-time bounce-buffer setup.

Risks and test signals: Risks are leaked contiguous reservations, wrong DMA handle translation, and address-limit violations. Test PV/HVM DMA devices, highmem or encrypted-memory DMA paths, bounce-buffer allocation, contiguous region create/destroy failure injection, and IOMMU-disabled guests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/swiotlb-xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/trace_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/trace_types.h

Purpose: Defines trace-facing Xen multicall flush and extension reason enums plus a callback function type used by Xen tracing and multicall batching.

Important APIs/types/functions: `enum xen_mc_flush_reason`, `enum xen_mc_extend_args`, and `xen_mc_callback_fn_t`.

Control flow: Xen multicall code tags flushes as explicit, batch-space, argument-space, or callback-space exhaustion and tags extend attempts as ok, bad operation, or no space. Trace events consume these values.

State and persistence behavior: No state is stored. Enum values become part of trace output semantics and should remain stable for observability.

Dependencies and integration points: Integrated with Xen multicall batching, tracepoints, and callback queues.

Risks and test signals: Risks are trace decoder drift and missing reason coverage when multicall behavior changes. Test with Xen trace events enabled, multicall-heavy PV MMU workloads, and trace consumers that decode flush reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/trace_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/Kbuild

Purpose: Lists generated x86 UAPI syscall-number headers for Kbuild export: `unistd_32.h`, `unistd_64.h`, and `unistd_x32.h`.

Important APIs/types/functions: `generated-y` entries for the three generated unistd headers.

Control flow: During header generation/export, Kbuild creates or includes these ABI-specific syscall-number headers so userspace-facing installs have complete syscall definitions.

State and persistence behavior: No runtime state. The persistent artifact is the generated header set installed into exported UAPI headers.

Dependencies and integration points: Integrates with x86 syscall table generation and `uapi/asm/unistd.h` ABI selection for i386, x86_64, and x32.

Risks and test signals: Risks are missing generated headers in exported UAPI installs or stale syscall table generation. Test `make headers_install`, userspace builds against all three x86 ABIs, and syscall-number consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/a.out.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/a.out.h

Purpose: Exposes the legacy x86 `a.out` executable header layout and size accessor macros for userspace and compatibility tools.

Important APIs/types/functions: `struct exec`, `N_TRSIZE()`, `N_DRSIZE()`, and `N_SYMSIZE()`.

Control flow: No executable flow. Loaders or file-inspection tools read `struct exec` fields and use the macros to locate relocation and symbol data.

State and persistence behavior: No runtime state. It preserves on-disk ABI field order for old `a.out` binaries.

Dependencies and integration points: Integrated with legacy binary-format tooling and any compatibility loader code that still parses x86 `a.out`.

Risks and test signals: Risks are layout changes or macro incompatibility for old tools. Test by compiling userspace that includes the header and by parsing known `a.out` fixtures if legacy support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/a.out.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/amd_hsmp.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/amd_hsmp.h

Purpose: Defines the AMD Host System Management Port userspace ABI: message IDs, message descriptors, metrics table layout, protocol versions, and the ioctl used to exchange HSMP commands with the kernel driver.

Important APIs/types/functions: `HSMP_MAX_MSG_LEN`, `enum hsmp_message_ids`, `struct hsmp_message`, `enum hsmp_msg_type`, `enum hsmp_proto_versions`, `struct hsmp_msg_desc`, `hsmp_msg_desc_table`, `struct hsmp_metric_table`, `HSMP_BASE_IOCTL_NR`, and `HSMP_IOCTL_CMD`.

Control flow: Userspace fills `struct hsmp_message` with a socket index, message ID, argument count, expected response size, and up to eight arguments, then issues `HSMP_IOCTL_CMD`. Kernel driver validation can use the descriptor table to check supported GET/SET/SET_GET command shape before forwarding to platform firmware/SMU.

State and persistence behavior: No kernel state is owned by the header. The ABI conveys mutable platform state such as power limits, boost limits, link widths, P-states, telemetry counters, RAPL counters, and metrics table contents.

Dependencies and integration points: Depends on Linux UAPI integer and ioctl types. Integrates with AMD server firmware, the HSMP character device driver, telemetry agents, power-management tooling, and platform-specific PPR message definitions.

Risks and test signals: Risks include ioctl layout drift due to packing, mismatched descriptor counts, firmware protocol-version differences, and command IDs that are unsupported on a given family/model. Test ioctl round trips on supported AMD systems, descriptor validation for each message, 32-bit userspace compatibility, metrics table size/offset checks, and unsupported-message `-ENOMSG` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/amd_hsmp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/auxvec.h

Purpose: Defines x86-specific ELF auxiliary vector entries for vDSO/sysinfo discovery and the architecture aux-vector size budget.

Important APIs/types/functions: `AT_SYSINFO`, `AT_SYSINFO_EHDR`, and `AT_VECTOR_SIZE_ARCH`.

Control flow: ELF exec setup emits these auxiliary entries; userspace dynamic linkers and runtimes read them during process startup to locate vDSO or legacy vsyscall helpers.

State and persistence behavior: No persistent kernel state, but aux-vector contents are part of every process's initial userspace ABI.

Dependencies and integration points: Integrates with ELF binary loading, vDSO mapping, IA32 emulation, x32/non-compat x86-64 startup, and libc runtime initialization.

Risks and test signals: Risks include wrong aux-vector sizing for compat tasks and missing vDSO pointers. Test 32-bit, x32, and 64-bit process startup, `getauxval(AT_SYSINFO_EHDR)`, static and dynamic binaries, and IA32 emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bitsperlong.h

Purpose: Selects `__BITS_PER_LONG` for x86 UAPI based on compiler target ABI, using 64 for normal x86_64 and 32 for i386 or x32 ILP32.

Important APIs/types/functions: `__BITS_PER_LONG` and inclusion of `asm-generic/bitsperlong.h`.

Control flow: Header preprocessing branches on `__x86_64__` and `__ILP32__`; there is no runtime flow.

State and persistence behavior: No runtime state. The selected value affects userspace-visible type widths and ABI structure layouts.

Dependencies and integration points: Integrated with all UAPI headers that use `long`-dependent generic types, including IPC, stat, signal, and syscall data structures.

Risks and test signals: Risks are x32 being treated as 64-bit long or cross-compiler macro mismatches. Test headers with i386, x86_64, and x32 toolchains and compile-time assertions for `sizeof(long)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/boot.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/boot.h

Purpose: Exposes legacy x86 boot video mode constants used by setup/bootloader interfaces.

Important APIs/types/functions: `NORMAL_VGA`, `EXTENDED_VGA`, and `ASK_VGA`.

Control flow: Bootloaders or setup code pass these constants in boot parameters to request standard, extended, or interactive VGA mode selection.

State and persistence behavior: No runtime state. Values persist only as boot protocol constants.

Dependencies and integration points: Integrates with x86 boot protocol, setup header video mode fields, and early console/video initialization.

Risks and test signals: Risks are minimal but include stale bootloader assumptions. Test booting with normal, extended, and ask video mode options on BIOS-style x86 boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bootparam.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bootparam.h

Purpose: Defines the x86 boot protocol's main zeropage structures, setup header, load flags, e820 zeropage capacity, EFI/APM/EDD/screen/IST embeddings, and hardware subarchitecture enum.

Important APIs/types/functions: `RAMDISK_*`, `LOADED_HIGH`, `KASLR_FLAG`, `QUIET_FLAG`, `CAN_USE_HEAP`, `XLF_*`, `struct setup_header`, `struct sys_desc_table`, `struct olpc_ofw_header`, `struct efi_info`, `E820_MAX_ENTRIES_ZEROPAGE`, `JAILHOUSE_SETUP_REQUIRED_VERSION`, `struct boot_params`, and `enum x86_hardware_subarch`.

Control flow: Bootloaders populate `boot_params` and `setup_header`; early kernel code reads flags and addresses to decide relocation, command line, initrd, KASLR, 5-level paging, EFI handoff, memory encryption, setup-data chain traversal, e820 import, and subarchitecture dispatch.

State and persistence behavior: The zeropage is the persistent handoff state from bootloader/firmware to kernel entry. Some fields are obsolete but preserved; `sentinel` protects against bootloaders copying too much stale data.

Dependencies and integration points: Depends on setup-data, screen, APM, EDD, IST, and EDID UAPI structures. Integrates with boot/compressed kernel, EFI, BIOS E820, OLPC OFW, tboot, confidential-computing blobs, Jailhouse, Xen PV subarch, and early platform quirks.

Risks and test signals: Risks include packed-layout drift, offset changes, bootloader incompatibility, incorrect xloadflags interpretation, and e820 truncation. Test BIOS and EFI boots, 32-bit and 64-bit boot protocol versions, initrd above 4G, KASLR, 5-level paging, memory encryption, setup_data extensions, and struct offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/bootparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/byteorder.h

Purpose: Selects little-endian byte-order definitions for x86 UAPI.

Important APIs/types/functions: Inclusion of `linux/byteorder/little_endian.h`.

Control flow: None beyond preprocessing.

State and persistence behavior: No runtime state. The header defines compile-time conversion behavior for userspace-visible structures.

Dependencies and integration points: Integrated with UAPI code that needs endian annotations and conversion helpers.

Risks and test signals: Risk is effectively limited to include/export breakage. Test `headers_install` and userspace compilation of endian helper consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/debugreg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/debugreg.h

Purpose: Exposes x86 debug register numbers, DR6 status bits, DR7 control encodings, breakpoint access types, breakpoint lengths, and reserved masks to userspace and kernel UAPI consumers.

Important APIs/types/functions: `DR_FIRSTADDR`, `DR_LASTADDR`, `DR_STATUS`, `DR_CONTROL`, `DR6_RESERVED`, `DR_TRAP*`, `DR_BUS_LOCK`, `DR_STEP`, `DR_SWITCH`, `DR_CONTROL_SHIFT`, `DR_RW_*`, `DR_LEN_*`, `DR_LOCAL_ENABLE*`, `DR_GLOBAL_ENABLE*`, `DR_CONTROL_RESERVED`, and slowdown flags.

Control flow: Debugger, ptrace, perf, and hardware-breakpoint code interpret DR6/DR7 using these constants when setting or reporting debug exceptions.

State and persistence behavior: No state is owned here; state lives in CPU debug registers, ptrace-visible debug state, and task debug contexts.

Dependencies and integration points: Integrates with ptrace, perf hardware breakpoints, KVM debug registers, bus-lock detection, RTM debug behavior, and CPU exception handling.

Risks and test signals: Risks include wrong reserved masks on newer CPUs, incorrect breakpoint length/access encoding, and 32-bit versus 64-bit mask differences. Test ptrace hardware breakpoints, single-step, bus-lock debug exceptions, KVM debug register save/restore, and perf breakpoint events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/debugreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/e820.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/e820.h

Purpose: Defines legacy x86 E820 memory map offsets, entry counts, memory types, and user-visible `e820entry`/`e820map` structures.

Important APIs/types/functions: `E820MAP`, `E820MAX`, `E820_X_MAX`, `E820NR`, `E820_RAM`, `E820_RESERVED`, `E820_ACPI`, `E820_NVS`, `E820_UNUSABLE`, `E820_PMEM`, `E820_PRAM`, `E820_RESERVED_KERN`, `struct e820entry`, `struct e820map`, and BIOS/ISA address constants.

Control flow: Boot code reads E820 entries from the zeropage, sanitizes/merges them, and builds kernel memory/resource maps. Userspace tools can inspect maps using the same type definitions.

State and persistence behavior: E820 entries represent firmware-provided persistent boot memory state. Some types, especially PMEM/PRAM and reserved-kernel ranges, affect whether memory survives reboot or is available for allocation.

Dependencies and integration points: Depends on Linux UAPI types. Integrates with bootparam zeropage, EFI memory-map fallback, resource reservation, ACPI NVS, persistent memory, crash/kexec, and low-memory BIOS reservations.

Risks and test signals: Risks include map truncation at 128 zeropage entries, misclassified persistent memory, and incorrect reserved-region handling. Test BIOS and EFI memory maps, NUMA-heavy machines, PMEM legacy option, S3 resume, kexec, and `/proc/iomem` consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/e820.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/elf.h

Purpose: Defines x86 ELF note metadata for extended CPU feature components.

Important APIs/types/functions: `struct x86_xfeat_component` and its static alignment assertion.

Control flow: ELF core-dump and tooling paths consume arrays of component descriptors to describe XSAVE/xfeature state layout.

State and persistence behavior: No runtime state. The structure persists in ELF notes or userspace-visible metadata describing saved CPU state.

Dependencies and integration points: Depends on Linux UAPI types. Integrates with core dumps, ptrace/regset consumers, debuggers, and XSAVE feature enumeration.

Risks and test signals: Risks are layout or alignment changes that break debuggers. Test core dumps with extended xfeatures, `readelf`/gdb interpretation, and compile-time size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hw_breakpoint.h

Purpose: Placeholder UAPI header for x86 hardware breakpoint definitions. The file intentionally exports no x86-specific declarations in this tree.

Important APIs/types/functions: None beyond the file's presence and SPDX marker.

Control flow: No control flow.

State and persistence behavior: No state.

Dependencies and integration points: Included by generic perf or userspace code that expects an architecture hardware-breakpoint UAPI path to exist.

Risks and test signals: Risks are include-path breakage if removed or populated incompatibly. Test userspace builds that include `<asm/hw_breakpoint.h>` and perf breakpoint tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hwcap2.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hwcap2.h

Purpose: Defines x86 `AT_HWCAP2` feature bits exposed to userspace for ring-3 MONITOR/MWAIT and FSGSBASE availability.

Important APIs/types/functions: `HWCAP2_RING3MWAIT` and `HWCAP2_FSGSBASE`.

Control flow: CPU feature setup and ELF aux-vector code set these bits; userspace checks them before executing corresponding instructions.

State and persistence behavior: No private state. Values are process-visible feature bits in the auxiliary vector.

Dependencies and integration points: Depends on Linux bit constants. Integrates with CPU feature detection, ELF auxvec, libc/runtime feature dispatch, and instruction emulation policies.

Risks and test signals: Risks include exposing bits when the kernel has disabled user access or withholding bits when safe. Test `getauxval(AT_HWCAP2)`, user FSGSBASE instructions, ring-3 MWAIT policy, and CPU feature toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/hwcap2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ist.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ist.h

Purpose: Defines the legacy Intel SpeedStep Technology BIOS handoff structure embedded in x86 boot parameters.

Important APIs/types/functions: `struct ist_info` with `signature`, `command`, `event`, and `perf_level`.

Control flow: Boot code receives this firmware data in `boot_params`; power-management code may interpret it for legacy IST handling.

State and persistence behavior: No owned runtime state. The structure captures firmware-provided boot-time CPU performance metadata.

Dependencies and integration points: Depends on Linux UAPI types and integrates with `bootparam.h`, firmware/BIOS setup, and legacy CPU frequency support.

Risks and test signals: Risks are packed offset compatibility and obsolete firmware quirks. Test bootparam layout and legacy IST-capable system handling if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm.h

Purpose: Defines the x86-specific KVM userspace ABI for VM and vCPU state, interrupt chips, registers, CPUID, MSRs, PIT, debug state, XSAVE/XCRS, sync regs, quirks, nested VMX/SVM migration state, PMU filters, MCE injection, Xen HVM emulation, SEV/SNP, Hyper-V eventfds, x2APIC API, hypercall exits, protected VM types, and TDX subcommands.

Important APIs/types/functions: `struct kvm_regs`, `kvm_sregs`, `kvm_sregs2`, `kvm_fpu`, `kvm_msr_entry`, `kvm_msrs`, `kvm_msr_filter`, `kvm_cpuid_entry*`, `kvm_lapic_state`, `kvm_vcpu_events`, `kvm_debugregs`, `kvm_xsave`, `kvm_xcrs`, `kvm_sync_regs`, `kvm_nested_state`, `kvm_pmu_event_filter`, `kvm_x86_mce`, `kvm_xen_hvm_config`, `kvm_xen_hvm_attr`, `kvm_xen_vcpu_attr`, SEV/SNP command structs, `kvm_tdx_cmd`, `kvm_tdx_capabilities`, and `kvm_tdx_init_*`; feature flags such as `__KVM_HAVE_*`, `KVM_STATE_NESTED_*`, `KVM_XEN_HVM_CONFIG_*`, `KVM_SEV_*`, `KVM_X86_*_VM`, and PMU masked-entry helpers.

Control flow: Userspace VMMs exchange these structures through KVM ioctls. They create vCPUs, set CPUID/MSRs/registers, snapshot interrupt chips and timers, filter MSR/PMU access, migrate nested virtualization state, configure Xen compatibility, launch encrypted VMs, and initialize TDX VMs. Kernel KVM validates userspace-supplied state before loading it into vCPU or VM structures.

State and persistence behavior: These structures are the persistent migration and runtime ABI between userspace and KVM. They carry guest CPU state, interrupt-controller state, event injection state, nested VMCS/VMCB state, encryption launch state, Xen shared info/runstate/timer metadata, and protected-VM measurement inputs.

Dependencies and integration points: Depends on Linux UAPI types/ioctl/bit helpers and is consumed by QEMU, cloud hypervisors, test frameworks, migration tooling, and KVM kernel code. Integrates with VMX, SVM, Xen HVM emulation, Hyper-V emulation, SEV/SNP firmware, TDX module, PMU, LAPIC/IOAPIC/PIC, PIT, MCE, MSR, XSAVE, and ptrace-like debug facilities.

Risks and test signals: Risks are ABI layout drift, insufficient padding validation, migration incompatibility, malicious userspace state, nested-state size errors, protected-VM launch mismatch, and 32-bit userspace pointer handling. Test KVM selftests, QEMU boot/migration, nested VMX/SVM migration, Xen HVM tests, SEV/SNP/TDX launch paths, MSR filter tests, PMU event filters, XSAVE dynamic-size tests, MCE injection, and ioctl ABI size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_para.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_para.h

Purpose: Defines x86 KVM paravirtual CPUID leaves, feature bits, KVM-specific MSRs, PV clock/steal-time structures, async page-fault data, PV EOI flags, MMU hypercall payloads, and GPA range mapping flags.

Important APIs/types/functions: `KVM_CPUID_SIGNATURE`, `KVM_SIGNATURE`, `KVM_CPUID_FEATURES`, `KVM_FEATURE_*`, `KVM_HINTS_REALTIME`, `MSR_KVM_*`, `struct kvm_steal_time`, `struct kvm_clock_pairing`, `KVM_ASYNC_PF_*`, `struct kvm_mmu_op_*`, `struct kvm_vcpu_pv_apf_data`, `KVM_PV_EOI_*`, and `KVM_MAP_GPA_RANGE_*`.

Control flow: Guests detect KVM through CPUID, enable paravirtual features via MSRs, receive PV clock/steal-time/async-PF state in shared pages, and issue KVM hypercalls for MMU ops or GPA encryption-state changes.

State and persistence behavior: Persistent guest-visible state includes shared steal-time pages, PV clock MSR addresses, async page-fault pages/tokens, PV EOI memory, migration readiness, and encrypted/decrypted GPA range requests.

Dependencies and integration points: Depends on Linux UAPI types and bit macros. Integrates with KVM guest drivers, pvclock, scheduler steal accounting, async page fault handling, PV TLB flush/IPI/yield, confidential guest memory conversion, and live migration readiness.

Risks and test signals: Risks include feature-bit mismatch, shared-page alignment mistakes, stale versioning, and async-PF delivery-mode confusion. Test KVM guest boot, pvclock stability, steal-time accounting, async page fault modes, PV EOI, PV TLB flush/send IPI, migration control, and encrypted memory range mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_perf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_perf.h

Purpose: Provides x86 KVM perf trace decoding names and includes VMX/SVM/KVM exit-reason definitions needed by perf tooling.

Important APIs/types/functions: `DECODE_STR_LEN`, `VCPU_ID`, `KVM_ENTRY_TRACE`, `KVM_EXIT_TRACE`, and `KVM_EXIT_REASON`.

Control flow: Perf tooling uses these constants to locate tracepoints and decode exit-reason fields using included VMX/SVM definitions.

State and persistence behavior: No runtime state. Tracepoint names are an observability ABI.

Dependencies and integration points: Includes `asm/svm.h`, `asm/vmx.h`, and `asm/kvm.h`; integrates with perf, ftrace, KVM tracepoints, and virtualization performance analysis.

Risks and test signals: Risks are tracepoint name drift or exit-reason decode mismatch. Test `perf kvm` on Intel and AMD hosts, KVM entry/exit traces, and decoding of VMX/SVM exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm_perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ldt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ldt.h

Purpose: Defines the userspace ABI for the legacy `modify_ldt` syscall, including LDT capacity and user descriptor layout.

Important APIs/types/functions: `LDT_ENTRIES`, `LDT_ENTRY_SIZE`, `struct user_desc`, and `MODIFY_LDT_CONTENTS_*`.

Control flow: Userspace passes `user_desc` to `modify_ldt`; kernel validates fields and installs or reads LDT descriptors. On 64-bit, base/limit and many segment choices are constrained, and `lm` must be treated carefully for 32-bit callers.

State and persistence behavior: LDT entries persist in per-mm or per-task descriptor tables until replaced or process exit. The header itself owns no state.

Dependencies and integration points: Integrates with segmentation, TLS/compat tasks, ptrace-like process setup, DOSEMU/Wine-style users, and syscall entry restrictions.

Risks and test signals: Risks include 32-bit user initialization of the 64-bit `lm` bit, descriptor privilege mistakes, and syscall compatibility regressions. Test `modify_ldt` selftests, i386 compatibility, Wine/DOSEMU workloads, and 64-bit syscall behavior with unusual segment descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ldt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mce.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mce.h

Purpose: Defines the userspace-visible machine-check event record and ioctls for querying mcelog record and buffer properties.

Important APIs/types/functions: `struct mce`, `MCE_GET_RECORD_LEN`, `MCE_GET_LOG_LEN`, and `MCE_GETCLEAR_FLAGS`.

Control flow: Kernel machine-check handlers fill records; userspace reads them and uses ioctls to determine record length, log length, and clear flags. Fields must remain stable for mcelog and other consumers.

State and persistence behavior: `struct mce` instances persist in kernel logs/ring buffers and userspace crash telemetry. Header comments explicitly require adding shared fields only at the end and avoiding vendor-specific field insertion.

Dependencies and integration points: Depends on Linux UAPI types and ioctl. Integrates with x86 MCE handling, EDAC/rasdaemon/mcelog, SMCA, protected processor inventory, microcode reporting, and APEI/MCE reporting paths.

Risks and test signals: Risks include structure offset changes, vendor-specific ABI pollution, missing SMCA field handling, and 32-bit consumers misreading 64-bit fields. Test mcelog/rasdaemon ingestion, MCE injection, SMCA systems, ioctl record-length checks, and ABI offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mman.h

Purpose: Adds x86-specific `mmap` flags for low 32-bit placement and above-4G placement, then includes generic memory mapping flags.

Important APIs/types/functions: `MAP_32BIT`, `MAP_ABOVE4G`, and generic mman definitions.

Control flow: Userspace passes these flags to mmap-like syscalls; kernel address-selection code constrains the mapping range accordingly.

State and persistence behavior: No state. Resulting VMAs persist in the process address space.

Dependencies and integration points: Integrates with x86 virtual memory layout, legacy JIT/runtime low-address assumptions, and generic mmap UAPI.

Risks and test signals: Risks include address-selection regressions, conflicts with ASLR, and unsupported flag handling on compat paths. Test mmap with both flags, ASLR-enabled processes, 32-bit compatibility, and VMA placement verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msgbuf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msgbuf.h

Purpose: Selects the generic SysV message queue buffer ABI except for x32, where it defines the x86_64-compatible `msqid64_ds` layout using x32-sized kernel types.

Important APIs/types/functions: `struct msqid64_ds` for x32 and inclusion of `asm-generic/msgbuf.h` otherwise.

Control flow: SysV IPC syscalls copy this structure between kernel and userspace for message queue metadata.

State and persistence behavior: Message queue metadata persists in kernel IPC objects; this header defines the userspace serialization layout.

Dependencies and integration points: Depends on `asm/ipcbuf.h` and generic msgbuf. Integrates with SysV IPC, x32 ABI compatibility, libc, and checkpoint/restore tools.

Risks and test signals: Risks include x32 layout mismatch with x86_64 expectations and time/long width confusion. Test SysV message queue stat/control calls on i386, x86_64, and x32 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msgbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msr.h

Purpose: Defines userspace ioctls for reading and writing model-specific registers through the x86 MSR character device interface.

Important APIs/types/functions: `X86_IOC_RDMSR_REGS` and `X86_IOC_WRMSR_REGS`.

Control flow: Userspace sends an array of eight `__u32` values to the MSR driver via ioctl; the kernel performs the requested register access and copies results back for reads.

State and persistence behavior: No header-owned state. MSR writes mutate CPU-local or package-wide hardware state and can persist until reset or rewritten.

Dependencies and integration points: Depends on Linux UAPI types and ioctl. Integrates with `/dev/cpu/*/msr`, CPU feature tooling, performance/power management, and low-level diagnostics.

Risks and test signals: Risks include unsafe MSR writes, ioctl ABI mismatch, and CPU-hotplug races. Test `rdmsr`/`wrmsr` tooling, 32-bit userspace, permission checks, and invalid MSR error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/msr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mtrr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mtrr.h

Purpose: Defines the legacy x86 MTRR userspace ioctl ABI, variable/fixed range limits, memory type values, and 32-bit versus 64-bit entry layouts.

Important APIs/types/functions: `struct mtrr_sentry`, `struct mtrr_gentry`, `struct mtrr_var_range`, `mtrr_type`, `MTRR_NUM_FIXED_RANGES`, `MTRR_MAX_VAR_RANGES`, `MTRRphysBase_MSR()`, `MTRRphysMask_MSR()`, `MTRRIOC_*`, and `MTRR_TYPE_*`.

Control flow: Userspace issues MTRR ioctls to add, set, delete, kill, or get memory type ranges. Kernel MTRR code validates ranges, programs CPU MSRs, and handles 32-bit emulation layout differences.

State and persistence behavior: MTRR programming persists in CPU hardware registers until changed or reset. The ABI layout must remain stable for old X server and graphics tooling.

Dependencies and integration points: Depends on Linux UAPI types/ioctl/errno. Integrates with cache attribute management, PAT interactions, CPU MSR programming, graphics framebuffers, and compatibility ioctl handling.

Risks and test signals: Risks include 32-bit/64-bit structure-order confusion, cache-type conflicts with PAT, and unsafe memory-type programming. Test legacy MTRR tools, compat ioctls, framebuffer write-combining setup, CPU hotplug synchronization, and invalid range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mtrr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/perf_regs.h

Purpose: Defines x86 register IDs used by perf sample register masks, including GPR and XMM register numbering.

Important APIs/types/functions: `enum perf_event_x86_regs`, `PERF_REG_X86_32_MAX`, `PERF_REG_X86_64_MAX`, `PERF_REG_X86_XMM*`, `PERF_REG_X86_XMM_MAX`, and `PERF_REG_EXTENDED_MASK`.

Control flow: Perf event setup uses these IDs in user register masks; sampling code maps saved register state to the requested IDs.

State and persistence behavior: No state. Register IDs are a userspace ABI for perf.data and perf_event_open masks.

Dependencies and integration points: Integrates with perf, unwinding, sample decoding, BPF/perf consumers, and extended register sampling.

Risks and test signals: Risks include ID reordering, incorrect 128-bit XMM mask handling, and 32-bit/64-bit register boundary mistakes. Test `perf record --user-regs`, perf.data decoding, XMM sampling, and i386 versus x86_64 masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types.h

Purpose: Routes userspace POSIX type definitions to the correct x86 ABI-specific header: i386, x32, or x86_64.

Important APIs/types/functions: Includes `posix_types_32.h`, `posix_types_x32.h`, or `posix_types_64.h` when not building the kernel.

Control flow: Preprocessor selection depends on `__i386__` and `__ILP32__`; no runtime flow.

State and persistence behavior: No runtime state. Selected typedefs determine userspace ABI structure layouts.

Dependencies and integration points: Integrates with libc, generic UAPI types, IPC/stat/signal headers, and x32 compatibility.

Risks and test signals: Risks are wrong ABI branch selection and namespace pollution for userspace. Test header compilation under i386, x86_64, and x32 targets and ABI struct size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_32.h

Purpose: Defines i386-specific POSIX kernel types before falling back to generic POSIX types.

Important APIs/types/functions: Typedefs for `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_uid_t`, `__kernel_gid_t`, and `__kernel_old_dev_t`, plus inclusion of `asm-generic/posix_types.h`.

Control flow: No runtime flow.

State and persistence behavior: No state. Typedef widths persist as i386 UAPI ABI.

Dependencies and integration points: Integrates with 32-bit SysV IPC, stat, file mode, UID/GID, and old device number layouts.

Risks and test signals: Risks are width changes that break 32-bit binaries. Test i386 userspace header compilation and ABI size checks for IPC/stat structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_64.h

Purpose: Defines x86_64-specific old UID/GID and old device types before generic POSIX type definitions.

Important APIs/types/functions: Typedefs for `__kernel_old_uid_t`, `__kernel_old_gid_t`, and `__kernel_old_dev_t`, plus inclusion of `asm-generic/posix_types.h`.

Control flow: No runtime flow.

State and persistence behavior: No state. Typedef widths persist as x86_64 UAPI ABI.

Dependencies and integration points: Integrates with x86_64 stat, IPC, and legacy UID/GID/device interfaces.

Risks and test signals: Risks are layout changes affecting old ABI fields. Test x86_64 userspace compilation and struct layout assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_x32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_x32.h

Purpose: Defines x32-specific `long` and `unsigned long` kernel typedefs as 64-bit quantities, then reuses the x86_64 POSIX type definitions.

Important APIs/types/functions: `__kernel_long_t`, `__kernel_ulong_t`, and inclusion of `posix_types_64.h`.

Control flow: No runtime flow.

State and persistence behavior: No state. The typedefs preserve the x32 ABI's hybrid ILP32/userspace with selected 64-bit kernel layout fields.

Dependencies and integration points: Integrates with x32 SysV IPC, stat, signal, and generic POSIX types.

Risks and test signals: Risks include treating x32 as ordinary 32-bit or ordinary 64-bit. Test x32 userspace builds and ABI layout checks for time, IPC, and stat structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types_x32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/prctl.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/prctl.h

Purpose: Defines x86 `arch_prctl` command numbers and feature bits for FS/GS base, CPUID faulting, extended xstate permission, vDSO mapping, LAM/tagged addresses, and user shadow stack control.

Important APIs/types/functions: `ARCH_SET_GS`, `ARCH_SET_FS`, `ARCH_GET_FS`, `ARCH_GET_GS`, `ARCH_GET_CPUID`, `ARCH_SET_CPUID`, `ARCH_GET_XCOMP_*`, `ARCH_REQ_XCOMP_*`, `ARCH_XCOMP_TILECFG`, `ARCH_XCOMP_TILEDATA`, `ARCH_MAP_VDSO_*`, `ARCH_GET_UNTAG_MASK`, `ARCH_ENABLE_TAGGED_ADDR`, `ARCH_GET_MAX_TAG_BITS`, `ARCH_FORCE_TAGGED_SVA`, `ARCH_SHSTK_*`, `ARCH_SHSTK_SHSTK`, and `ARCH_SHSTK_WRSS`.

Control flow: Userspace calls `arch_prctl`; kernel dispatches by command to mutate or query thread FS/GS base, CPUID execution policy, dynamic xstate permissions, vDSO placement, LAM tagging, or CET shadow-stack state.

State and persistence behavior: State persists per task or mm: FS/GS base, CPUID faulting mode, xstate permission bits, optional vDSO mapping, LAM mode, and shadow-stack enable/lock/status bits.

Dependencies and integration points: Integrates with TLS, context switching, CPUID faulting, AMX dynamic xstate, vDSO, Linear Address Masking, CET user shadow stacks, ptrace, and signal restore.

Risks and test signals: Risks include command-number collision, security policy bypass, and per-thread state not restored across fork/exec/signal. Test arch_prctl selftests, TLS runtimes, CPUID-faulting tests, AMX permission requests, LAM tagged-address tests, vDSO mapping tests, and shadow-stack enable/lock/unlock/status flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/prctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/processor-flags.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/processor-flags.h

Purpose: Publishes x86 EFLAGS, CR0, CR3, CR4, CR8, legacy Cyrix register, and initial CR0 state bit definitions usable from C and assembly.

Important APIs/types/functions: `X86_EFLAGS_*`, `X86_CR0_*`, `X86_CR3_*`, `X86_CR4_*`, `X86_CR8_TPR`, `CX86_*`, and `CR0_STATE`.

Control flow: Low-level kernel, boot, virtualization, signal, ptrace, and userspace tooling use these constants to test or program processor control state.

State and persistence behavior: The header owns no state; it names CPU register bits whose values persist in task context, vCPU context, or processor control registers.

Dependencies and integration points: Depends on Linux constant macros. Integrates with boot paging, CR4 feature enablement, VMX, SMEP/SMAP/PKE/CET/FRED/LAM, ptrace flag reporting, signal contexts, KVM, and low-level assembly.

Risks and test signals: Risks include wrong bit positions for new features, 32-bit handling of high CR4 bits, and stale reserved assumptions. Test boot on feature-rich CPUs, virtualization CR intercepts, ptrace/signal flag reporting, LAM/CET/FRED config builds, and assembly include paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/processor-flags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace-abi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace-abi.h

Purpose: Defines x86 ptrace register offsets, frame size constants, and architecture-specific ptrace request numbers.

Important APIs/types/functions: i386 register indices `EBX` through `SS`, x86_64 frame offsets `R15` through `SS`, `FRAME_SIZE`, `PTRACE_GETREGS`, `PTRACE_SETREGS`, `PTRACE_GETFPREGS`, `PTRACE_SETFPREGS`, `PTRACE_GETFPXREGS`, `PTRACE_SETFPXREGS`, `PTRACE_GET_THREAD_AREA`, `PTRACE_SET_THREAD_AREA`, `PTRACE_ARCH_PRCTL`, `PTRACE_SYSEMU`, `PTRACE_SYSEMU_SINGLESTEP`, and `PTRACE_SINGLEBLOCK`.

Control flow: Debuggers call ptrace requests; kernel copies register frames according to these offsets and request numbers. Assembly and frame-offset generation can use the same constants.

State and persistence behavior: No state. Register offsets define the ABI for observing and mutating task register state.

Dependencies and integration points: Integrates with ptrace, syscall tracing, TLS/thread-area manipulation, seccomp/syscall emulation tools, debuggers, CRIU, and kernel entry frame layout.

Risks and test signals: Risks include register offset drift, frame-size mismatch, and compat request handling regressions. Test gdb/strace, ptrace selftests, i386 compat tracing, syscall emulation, thread-area get/set, and generated frame offset comparisons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace-abi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace.h

Purpose: Defines the userspace-visible `struct pt_regs` layout for i386 and x86_64 and includes the register offset and processor flag UAPI.

Important APIs/types/functions: `struct pt_regs` for i386 and x86_64, plus included `ptrace-abi.h` and `processor-flags.h`.

Control flow: Kernel ptrace, signal, and core-dump paths copy register frames to userspace using this layout; debuggers inspect or modify fields.

State and persistence behavior: `pt_regs` snapshots represent transient task entry/exception state, but their serialized layout is persistent ABI for ptrace and core dumps.

Dependencies and integration points: Depends on compiler `__user`, ptrace ABI offsets, and processor flags. Integrates with kernel entry, syscall tracing, signal delivery, core dumps, KVM/debug tooling, and userspace debuggers.

Risks and test signals: Risks include field order drift, mismatch with assembly entry frames, and 32-bit compat confusion. Test ptrace GETREGS/SETREGS, coredump notes, signal handlers, syscall tracing, and frame-offset assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sembuf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sembuf.h

Purpose: Defines the x86 SysV semaphore `semid64_ds` userspace layout with ABI-specific time and padding fields.

Important APIs/types/functions: `struct semid64_ds`.

Control flow: SysV semaphore control syscalls copy this structure between kernel and userspace for semaphore set metadata.

State and persistence behavior: Semaphore metadata persists in kernel IPC objects; this header defines serialization, including historical padding differences between x86_32, x86_64, and x32.

Dependencies and integration points: Depends on `asm/ipcbuf.h`. Integrates with SysV IPC, libc, compat syscalls, and checkpoint/restore tools.

Risks and test signals: Risks include padding/layout mismatch and time field width confusion. Test `semctl(IPC_STAT/IPC_SET)` on i386, x86_64, and x32, plus ABI structure size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sembuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup.h

Purpose: Empty legacy placeholder for x86 setup UAPI includes.

Important APIs/types/functions: None.

Control flow: No control flow.

State and persistence behavior: No state.

Dependencies and integration points: Preserves include-path compatibility for code that includes `<asm/setup.h>`.

Risks and test signals: Risk is include compatibility if removed or populated with conflicting symbols. Test `headers_install` and userspace builds including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup_data.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup_data.h

Purpose: Defines extensible x86 boot setup-data node types and payload structures for firmware/device-tree/EFI/Jailhouse/confidential-computing/IMA/RNG seed/kexec handover data.

Important APIs/types/functions: `SETUP_*`, `SETUP_INDIRECT`, `SETUP_TYPE_MAX`, `struct setup_data`, `struct setup_indirect`, `struct boot_e820_entry`, `struct jailhouse_setup_data`, `struct ima_setup_data`, and `struct kho_data`.

Control flow: Early boot walks the linked `setup_data` list from `boot_params.hdr.setup_data`; indirect nodes reference payloads elsewhere; type-specific handlers import extra e820 entries, DTB, PCI, EFI, Apple properties, Jailhouse data, CC blobs, IMA buffers, RNG seeds, or kexec handover metadata.

State and persistence behavior: Setup-data nodes are bootloader-to-kernel handoff state. Kexec handover and IMA payloads can describe data preserved across kernel transitions.

Dependencies and integration points: Depends on Linux UAPI types. Integrates with boot protocol, EFI, device tree, confidential computing, Jailhouse guests, IMA across kexec, RNG seeding, and kexec handover objects.

Risks and test signals: Risks include unknown type handling, indirect pointer validation, length truncation, and packed layout drift. Test boot with extended e820, EFI setup data, CC blob, IMA kexec buffer, RNG seed, KHO metadata, and malformed setup_data chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/setup_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sgx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sgx.h

Purpose: Defines the Intel SGX userspace ABI for enclave creation, page addition, initialization, provisioning, SGX2 page permission/type changes, page removal, vEPC removal, and vDSO enclave entry/exit context.

Important APIs/types/functions: `enum sgx_page_flags`, `SGX_MAGIC`, `SGX_IOC_*`, `struct sgx_enclave_create`, `sgx_enclave_add_pages`, `sgx_enclave_init`, `sgx_enclave_provision`, `sgx_enclave_restrict_permissions`, `sgx_enclave_modify_types`, `sgx_enclave_remove_pages`, `sgx_enclave_user_handler_t`, `struct sgx_enclave_run`, and `vdso_sgx_enter_enclave_t`.

Control flow: Userspace opens SGX devices, issues ioctls to create an enclave, add measured pages, initialize with SIGSTRUCT, request provisioning, and optionally modify or remove pages. Enclave execution enters through the vDSO, which records exit/exception details in `sgx_enclave_run` and can invoke a user handler that chooses EENTER/ERESUME or returns to the caller.

State and persistence behavior: Enclave state persists in EPC pages and kernel enclave metadata. `sgx_enclave_run` is caller-owned transient execution state but is a stable vDSO ABI. SGX2 ioctl results include hardware ENCLS result and byte counts for partial progress.

Dependencies and integration points: Depends on Linux UAPI types/ioctl. Integrates with SGX driver, EPC management, vDSO, enclave runtimes, provisioning device, signal/exception fixups, KVM vEPC handling, and SGX2 page lifecycle.

Risks and test signals: Risks include ioctl layout drift, unsafe userspace pointer handling, partial-count mishandling, vDSO ABI misuse, and exception paths that violate x86-64 ABI assumptions. Test SGX selftests, enclave create/add/init/provision, SGX2 modify/remove flows, vDSO exception handling, user handler returns, 32-bit compat rejection/handling, and vEPC removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/shmbuf.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/shmbuf.h

Purpose: Selects generic SysV shared-memory buffer definitions except for x32, where it defines x86_64-compatible `shmid64_ds` and `shminfo64` layouts.

Important APIs/types/functions: `struct shmid64_ds` and `struct shminfo64` for x32, otherwise inclusion of `asm-generic/shmbuf.h`.

Control flow: SysV shared-memory syscalls copy these structures between kernel and userspace for segment metadata and system limits.

State and persistence behavior: Shared-memory metadata persists in kernel IPC objects; this header preserves userspace serialization for x32 and other x86 ABIs.

Dependencies and integration points: Depends on `asm/ipcbuf.h`, `asm/posix_types.h`, and generic shmbuf. Integrates with SysV IPC, x32 compatibility, libc, and checkpoint/restore tools.

Risks and test signals: Risks include x32 layout mismatch, time/size width errors, and padding incompatibility. Test `shmctl(IPC_STAT/IPC_INFO)` on i386, x86_64, and x32 plus ABI size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/shmbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext.h

Purpose: Defines x86 signal-frame CPU, FPU, and extended xstate layouts for 32-bit and 64-bit userspace, including legacy compatibility structures and magic values for XSAVE-extended signal state.

Important APIs/types/functions: `FP_XSTATE_MAGIC1`, `FP_XSTATE_MAGIC2`, `struct _fpx_sw_bytes`, `_fpreg`, `_fpxreg`, `_xmmreg`, `_fpstate_32`, `_fpstate_64`, `_header`, `_ymmh_state`, `_xstate`, `struct sigcontext_32`, `struct sigcontext_64`, and userspace `struct sigcontext` variants.

Control flow: Signal delivery builds a signal frame containing general registers and a pointer to FPU/XSAVE state. Signal return validates and restores state; userspace signal handlers and context libraries may inspect or modify fields.

State and persistence behavior: Signal frames persist on the userspace stack until handler return. The extended xstate magic fields and size fields describe variable-sized CPU state that must be preserved by user context switching and checkpointing tools.

Dependencies and integration points: Depends on Linux compiler and UAPI types. Integrates with signal delivery/return, XSAVE, AVX/YMM state, AMX and future xfeatures, ptrace/core dumps, libc ucontext, CRIU, and old 32-bit/64-bit binaries.

Risks and test signals: Risks include breaking old sigcontext aliases, mishandling `fpstate` as `_xstate`, not preserving reserved fields, x32 pointer padding mistakes, and SS/FS/GS historical quirks. Test signal selftests with FP/AVX/AMX state, sigreturn validation, 32-bit and x32 handlers, CRIU restore, alternate signal stacks, and old user context libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext32.h

Purpose: Legacy compatibility wrapper that redirects 32-bit sigcontext includes to the unified `sigcontext.h` definitions.

Important APIs/types/functions: Inclusion of `asm/sigcontext.h`.

Control flow: No runtime flow; preprocessing makes older include paths see the current definitions.

State and persistence behavior: No state. Preserves include-level ABI compatibility.

Dependencies and integration points: Integrates with older userspace code, 32-bit signal ABI, and libc headers expecting `<asm/sigcontext32.h>`.

Risks and test signals: Risks are include recursion or missing legacy path. Test userspace builds that include this header directly and 32-bit signal ABI selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/siginfo.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/siginfo.h

Purpose: Provides x32-specific `siginfo` alignment/type overrides before including the generic siginfo UAPI.

Important APIs/types/functions: `__kernel_si_clock_t`, `__ARCH_SI_CLOCK_T`, `__ARCH_SI_ATTRIBUTES`, and inclusion of `asm-generic/siginfo.h`.

Control flow: Signal-generation paths fill generic siginfo structures; x32 uses the alignment/type overrides selected here.

State and persistence behavior: `siginfo_t` is transient signal-delivery state but its layout is a stable userspace ABI.

Dependencies and integration points: Integrates with signal delivery, timers, x32 ABI, libc, ptrace signal injection, and generic siginfo definitions.

Risks and test signals: Risks are x32 alignment mismatch and timer clock type layout changes. Test signal delivery and POSIX timers under x32 plus ABI alignment assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/siginfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/signal.h

Purpose: Defines x86 signal numbers, signal action layout, signal stack type, signal stack sizes, and the x86 `SA_RESTORER` flag.

Important APIs/types/functions: `NSIG`, `sigset_t`, `SIG*` constants, `SIGRTMIN`, `SIGRTMAX`, `SA_RESTORER`, `MINSIGSTKSZ`, `SIGSTKSZ`, i386 and x86_64 userspace `struct sigaction`, and `stack_t`.

Control flow: Userspace registers signal handlers with `sigaction`; kernel signal delivery uses the ABI layout and optional restorer pointer, and alternate signal stack syscalls use `stack_t`.

State and persistence behavior: Signal dispositions and blocked masks persist per task; alternate stacks persist per thread. The header defines the serialized ABI only.

Dependencies and integration points: Depends on Linux UAPI types/compiler and generic signal defs. Integrates with libc, signal syscalls, rt signals, sigreturn trampolines, alternate stacks, ptrace, and i386 compatibility.

Risks and test signals: Risks include mismatched `struct sigaction` between i386 and x86_64, restorer handling bugs, and too-small stack assumptions for modern xstate. Test signal delivery, SA_RESTORER, alternate stacks, real-time signals, i386 compat, and libc header compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/stat.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/stat.h

Purpose: Defines x86 `stat`, `stat64`, and old stat layouts, including i386-specific padding and x86_64 generic-width fields.

Important APIs/types/functions: `STAT_HAVE_NSEC`, `struct stat` for i386 and non-i386, `INIT_STRUCT_STAT_PADDING()`, i386 `struct stat64`, `INIT_STRUCT_STAT64_PADDING()`, `STAT64_HAS_BROKEN_ST_INO`, and `struct __old_kernel_stat`.

Control flow: Kernel stat syscalls copy these structures to userspace; padding macros let kernel code initialize only the ABI padding that matters.

State and persistence behavior: No state. Structures serialize filesystem inode metadata to userspace, including nanosecond timestamps.

Dependencies and integration points: Depends on POSIX types. Integrates with VFS stat family syscalls, libc, 32-bit compatibility, old binaries, and filesystem metadata reporting.

Risks and test signals: Risks include padding leaks, broken i386 inode layout compatibility, time/size truncation, and x32/x86_64 type mismatch. Test stat/stat64/lstat/fstat on i386 and x86_64, ABI struct sizes, padding zeroing, large inode numbers, and nanosecond timestamp reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/statfs.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/statfs.h

Purpose: Defines x86-specific packing for compat `statfs64` before including generic statfs definitions.

Important APIs/types/functions: `ARCH_PACK_COMPAT_STATFS64` and inclusion of `asm-generic/statfs.h`.

Control flow: Filesystem statfs syscalls copy generic structures, with packed compat layout for i386 ABI expectations.

State and persistence behavior: No state. Structures serialize filesystem capacity and ID metadata.

Dependencies and integration points: Integrates with VFS statfs, compat syscalls, libc, and generic statfs UAPI.

Risks and test signals: Risks include compat packing mismatch between i386 and x86_64. Test `statfs64` from 32-bit userspace on 64-bit kernels and ABI size/alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/svm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/svm.h

Purpose: Defines AMD SVM VM-exit reason codes, SEV-ES/SNP VMGEXIT software events, termination reason encoding, and a string mapping list for exit decoding.

Important APIs/types/functions: `SVM_EXIT_*`, `SVM_VMGEXIT_*`, `SVM_VMGEXIT_TERM_REASON()`, `SVM_EXIT_SW`, `SVM_EXIT_ERR`, and `SVM_EXIT_REASONS`.

Control flow: KVM and perf tooling report SVM exits using these constants. SEV-ES/SNP guests use VMGEXIT event codes to communicate MMIO, AP setup, page-state changes, guest requests, SAVIC operations, hypervisor features, and termination.

State and persistence behavior: No state. Exit codes are ABI/trace values that persist in migration logs, trace output, and user tooling expectations.

Dependencies and integration points: Integrates with KVM SVM, perf KVM decoding, SEV-ES GHCB protocol, SNP page-state changes, nested virtualization, and userspace VMM exit handling.

Risks and test signals: Risks include exit-code mismatch with hardware or firmware, missing decode entries, and wrong termination encoding. Test AMD KVM selftests, SEV-ES/SNP guest boot, VMGEXIT MMIO and PSC paths, nested SVM, perf exit decoding, and trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/svm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/swab.h

Purpose: Provides x86 optimized byte-swap helpers for 32-bit and 64-bit values using `bswap` assembly.

Important APIs/types/functions: `__arch_swab32()` and `__arch_swab64()`.

Control flow: Inline helpers emit `bswapl`; 64-bit swaps use either two 32-bit swaps plus exchange on i386 or `bswapq` on x86_64.

State and persistence behavior: No state; helpers are pure value transformations.

Dependencies and integration points: Depends on Linux UAPI types and compiler attributes. Integrates with generic byte-swap code, endian conversions, networking/filesystem parsers, and userspace builds including kernel UAPI.

Risks and test signals: Risks include inline assembly constraint errors or wrong i386 half-ordering. Test compile under i386 and x86_64, constant-folding behavior, and known byte-swap vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ucontext.h

Purpose: Defines x86 ucontext flags for extended FP/XSAVE state and 64-bit signal-context SS restore semantics before including generic ucontext.

Important APIs/types/functions: `UC_FP_XSTATE`, `UC_SIGCONTEXT_SS`, `UC_STRICT_RESTORE_SS`, and generic ucontext inclusion.

Control flow: Signal delivery sets flags in `ucontext`; sigreturn uses them to decide whether extended xstate is present and how strictly to restore SS on x86_64/x32.

State and persistence behavior: Ucontext lives on userspace signal frames and can be saved/restored by context libraries or checkpoint tools.

Dependencies and integration points: Integrates with signal delivery/return, sigcontext, XSAVE, espfix, old DOSEMU/CRIU compatibility, libc `ucontext_t`, and x32.

Risks and test signals: Risks include incorrect SS restore compatibility, missing xstate flag, and old userspace breakage. Test signal selftests, segmented-context sigreturn, CRIU restore, x32 signals, and FP/XSAVE signal frame handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/unistd.h

Purpose: Defines the x32 syscall-number marker bit and selects the ABI-specific generated syscall-number header for userspace.

Important APIs/types/functions: `__X32_SYSCALL_BIT` and includes of `unistd_32.h`, `unistd_x32.h`, or `unistd_64.h`.

Control flow: Userspace preprocessing selects syscall numbers by target ABI. Runtime syscall wrappers use `__X32_SYSCALL_BIT` to identify x32 syscalls.

State and persistence behavior: No state. Syscall numbers are a stable userspace/kernel ABI.

Dependencies and integration points: Integrates with generated syscall headers, libc syscall wrappers, seccomp filters, strace, audit, and x32 compatibility.

Risks and test signals: Risks include missing generated headers, wrong x32 bit type/branch, and syscall-number table drift. Test `headers_install`, libc builds for all x86 ABIs, seccomp/strace decoding, and syscall table selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vm86.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vm86.h

Purpose: Defines the legacy i386 `vm86` userspace ABI for running virtual-8086 code, including return codes, function codes, register frame layouts, interrupt redirection bitmaps, and vm86plus debugger state.

Important APIs/types/functions: `BIOSSEG`, CPU type constants, `VM86_TYPE()`, `VM86_ARG()`, `VM86_*` return/function codes, `struct vm86_regs`, `struct revectored_struct`, `struct vm86_struct`, `VM86_SCREEN_BITMAP`, `struct vm86plus_info_struct`, and `struct vm86plus_struct`.

Control flow: Userspace enters vm86 mode via syscall, kernel runs virtual-8086 code until a signal, unhandled GP fault, software interrupt, STI/popf/iret event, PIC request, or debugger trap requires returning to userspace.

State and persistence behavior: vm86 register state, virtual interrupt flags, interrupt redirection maps, and debugger state persist in userspace-provided structs across syscall entries.

Dependencies and integration points: Depends on processor flags. Integrates with i386 compatibility, BIOS/DOS emulation, signal delivery, interrupt virtualization, and old DOSEMU-style runtimes.

Risks and test signals: Risks include old ABI layout breakage, virtual interrupt flag mistakes, and unsupported behavior on 64-bit-only configurations. Test vm86 userspace programs on 32-bit kernels/compat where supported, signal exits, int redirection, PIC returns, and debugger trap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vm86.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vmx.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vmx.h

Purpose: Defines Intel VMX VM-exit reason codes, exit reason flags, abort codes, and decode lists for KVM/perf tooling.

Important APIs/types/functions: `VMX_EXIT_REASONS_FAILED_VMENTRY`, `VMX_EXIT_REASONS_SGX_ENCLAVE_MODE`, `EXIT_REASON_*`, `VMX_EXIT_REASONS`, `VMX_EXIT_REASON_FLAGS`, and `VMX_ABORT_*`.

Control flow: KVM VMX reports exits and aborts using these constants; perf tooling decodes exit reasons from KVM tracepoints.

State and persistence behavior: No state. Exit codes are hardware/trace ABI values.

Dependencies and integration points: Integrates with KVM VMX, nested VMX, SGX enclave VM-exit reporting, TDX-related exits, perf KVM decode, and userspace VMM diagnostics.

Risks and test signals: Risks include missing new hardware exit codes, decode name drift, and failed-vmentry flag handling. Test Intel KVM selftests, nested VMX, perf exit decoding, SGX/TDX exit paths where available, and invalid VM-entry reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vsyscall.h

Purpose: Defines legacy x86_64 vsyscall numbers and the fixed vsyscall virtual address.

Important APIs/types/functions: `enum vsyscall_num` with `__NR_vgettimeofday`, `__NR_vtime`, `__NR_vgetcpu`, and `VSYSCALL_ADDR`.

Control flow: Legacy userspace can call fixed-address vsyscall entries; kernel may emulate, map, or fault them depending on configuration and security policy.

State and persistence behavior: No header-owned state. The fixed address is an ABI commitment for old binaries.

Dependencies and integration points: Integrates with x86_64 memory layout, vDSO/vsyscall compatibility, signal/fault handling, and seccomp/audit visibility of emulated calls.

Risks and test signals: Risks include breaking old binaries or weakening ASLR/security if mapped executable unexpectedly. Test legacy vsyscall binaries under emulate/native/none modes, `gettimeofday` compatibility, and fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/Makefile

Purpose: Main x86 kernel build manifest. It selects core x86 object files, disables instrumentation for fragile entry/boot/debug paths, emits `vmlinux.lds`, and wires feature-specific objects for tracing, paravirt, KVM guest, ACPI, APIC, CPU, FPU, kexec, perf, CET, unwinders, and platform support.

Important APIs/types/functions: Kbuild variables `always-$(KBUILD_BUILTIN)`, `CPPFLAGS_vmlinux.lds`, `CFLAGS_REMOVE_*`, `KASAN_SANITIZE_*`, `KCSAN_SANITIZE`, `KMSAN_SANITIZE_*`, `KCOV_INSTRUMENT_*`, `CFLAGS_head32.o`, `CFLAGS_head64.o`, `CFLAGS_irq.o`, and many `obj-y`/`obj-$(CONFIG_*)` selections such as `head_$(BITS).o`, `setup.o`, `x86_init.o`, `irq.o`, `fpu/`, `cpu/`, `acpi/`, `apic/`, `kvm.o`, `paravirt.o`, `machine_kexec_$(BITS).o`, `ftrace.o`, `shstk.o`, and 64-bit-specific objects.

Control flow: Kbuild evaluates configuration symbols and bitness, removes unsafe instrumentation from selected objects, and compiles/link-orders architecture objects. Runtime control flow is indirect: object inclusion determines which boot, interrupt, tracing, paravirt, CPU, and platform paths exist in the kernel.

State and persistence behavior: No runtime state. Persistent outputs are built objects and linked image sections. Instrumentation exclusions protect early boot, NMI, kexec, and stacktrace state from compiler-added code that would be unsafe in those contexts.

Dependencies and integration points: Integrates with nearly every x86 kernel subsystem: boot entry, traps, IRQs, APIC, ACPI, PCI DMA, timers, FPU, ptrace, SMP, paravirt, KVM guest, kexec/crash dump, tracing, unwinders, modules, KGDB, perf, CET, and CPU/platform directories.

Risks and test signals: Risks include missing objects under configs, unsafe instrumentation causing boot/kexec hangs, wrong 32/64-bit object selection, and link-order regressions. Test broad x86 defconfig/allmodconfig/tinyconfig builds, boot smoke tests, ftrace/KASAN/KMSAN/KCOV configs, kexec, NMI handling, stack unwinding, paravirt/KVM guest boot, and 32-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/Makefile

Purpose: Selects x86 ACPI kernel objects for boot tables, sleep/wakeup, APEI, CPPC, MADT wakeup/playdead, and processor C-state support.

Important APIs/types/functions: `obj-$(CONFIG_ACPI) += boot.o`, `obj-$(CONFIG_ACPI_SLEEP) += sleep.o wakeup_$(BITS).o`, `obj-$(CONFIG_ACPI_APEI) += apei.o`, `obj-$(CONFIG_ACPI_CPPC_LIB) += cppc.o`, `obj-$(CONFIG_ACPI_MADT_WAKEUP) += madt_wakeup.o madt_playdead.o`, and conditional `cstate.o` when `CONFIG_ACPI_PROCESSOR` is non-empty.

Control flow: Kbuild includes ACPI support objects according to config. Runtime ACPI boot, sleep, error handling, CPPC, MADT wakeup, and C-state behavior exists only when the corresponding objects are linked.

State and persistence behavior: No runtime state in the Makefile. Included objects manage ACPI table-derived state, sleep state, processor idle state, and firmware-first error handling.

Dependencies and integration points: Integrates with x86 ACPI table parsing, suspend/resume, wakeup assembly by bitness, APEI/RAS, CPPC frequency/performance controls, MADT CPU wakeup, and ACPI processor idle.

Risks and test signals: Risks include config gaps and bitness-specific wakeup object omission. Test ACPI-enabled and disabled builds, suspend/resume, APEI configs, CPPC systems, MADT wakeup CPU hotplug, and ACPI processor idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/apei.c -->
# sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/apei.c

Purpose: Implements x86 architecture hooks for ACPI Platform Error Interface handling, especially firmware-first corrected machine checks and conversion of APEI/CPER records into x86 MCE reports.

Important APIs/types/functions: `arch_apei_enable_cmcff()`, `arch_apei_report_mem_error()`, and `arch_apei_report_x86_error()`.

Control flow: APEI HEST parsing calls `arch_apei_enable_cmcff()` for corrected machine-check firmware-first entries. When `CONFIG_X86_MCE` is enabled, it saves the firmware threshold, checks firmware-first flags and hardware bank count, logs enablement, and disables listed MCE banks so firmware handles corrected errors first. Memory and processor error report hooks delegate to MCE/SMCA reporting helpers.

State and persistence behavior: With MCE enabled, persistent effects include saved APEI threshold limits and disabled machine-check banks for firmware-first corrected errors. Without `CONFIG_X86_MCE`, the functions compile to minimal success/delegation behavior where applicable.

Dependencies and integration points: Depends on ACPI APEI/HEST and x86 MCE/TLB flush headers. Integrates with ACPI HEST, corrected machine-check firmware-first mode, CPER memory error reporting, SMCA processor-context reporting, and RAS logging.

Risks and test signals: Risks include disabling the wrong MCE banks, ignoring malformed HEST bank lists, threshold mismatch, and behavior differences when MCE is disabled. Test ACPI APEI firmware-first systems, HEST tables with and without hardware banks, corrected error injection, CPER memory error reporting, SMCA error records, and `CONFIG_X86_MCE` off builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kernel/acpi/apei.c -->
