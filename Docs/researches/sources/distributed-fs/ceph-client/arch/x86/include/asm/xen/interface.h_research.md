<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface.h

Purpose: Defines the common x86 portion of Xen's guest ABI: guest-handle types, machine-to-physical virtual ranges, trap-table entries, shared-info architecture fields, vCPU context layout, PMU context layout, and emulated-instruction prefixes.

Important APIs/types/functions: `DEFINE_GUEST_HANDLE*`, `set_xen_guest_handle`, `xen_pfn_t`, `xen_ulong_t`, `MACH2PHYS_*`, `MAX_VIRT_CPUS`, reserved GDT macros, `struct trap_info`, `struct arch_shared_info`, `struct vcpu_guest_context`, `VGCF_*` flags, PMU structs `xen_pmu_amd_ctxt`, `xen_pmu_intel_ctxt`, `xen_pmu_regs`, `xen_pmu_arch`, `PMU_*`, `XEN_EMULATE_PREFIX`, and `XEN_CPUID`.

Control flow: This header defines data passed to hypercalls and shared pages. Boot and vCPU setup fill `vcpu_guest_context`; trap setup sends `trap_info` arrays; p2m management updates `arch_shared_info`; PMU interrupt handling exchanges `xen_pmu_arch` with Xen; selected instructions can be forced through Xen emulation by prefix macros.

State and persistence behavior: ABI state persists in shared info pages, vCPU contexts, p2m generation counters, trap tables, GDT/LDT frame references, control/debug registers, and PMU cached contexts. `p2m_generation` uses odd/even updates to let external readers detect in-progress changes.

Dependencies and integration points: Pulls in 32-bit or 64-bit subheaders and `pvclock-abi.h`. Integrated with Xen hypercalls, PV boot, PVH/HVM context setup, perf/PMU virtualization, trap/IDT setup, p2m/m2p translation, and toolstack save/restore.

Risks and test signals: Risks are packed layout drift, pointer-handle size mismatch, stale p2m generation handling, and differences between PV/HVM/PVH context semantics. Test Xen guest boot on 32-bit and 64-bit, save/restore/migration, PMU sampling, trap callback setup, p2m inspection from dom0, and ABI size checks against Xen headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface.h -->
