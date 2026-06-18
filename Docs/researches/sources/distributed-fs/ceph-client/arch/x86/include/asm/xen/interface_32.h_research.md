<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_32.h

Purpose: Supplies 32-bit x86 Xen ABI details: flat segment selectors, trap instruction, hypervisor and machine-to-physical virtual ranges, 32-bit CPU register layout, vCPU info, callback shape, and CR3 PFN packing.

Important APIs/types/functions: `FLAT_RING1_*`, `FLAT_RING3_*`, `FLAT_KERNEL_*`, `FLAT_USER_*`, `TRAP_INSTR`, `__MACH2PHYS_*`, `__HYPERVISOR_VIRT_START`, `struct cpu_user_regs`, `tsc_timestamp_t`, `struct arch_vcpu_info`, `struct xen_callback`, `XEN_CALLBACK()`, `xen_pfn_to_cr3()`, and `xen_cr3_to_pfn()`.

Control flow: PV boot and hypercall paths use these constants to build selectors, callbacks, and CR3 values. Xen trap entry uses `int $0x82`; vCPU context code serializes `cpu_user_regs` for hypervisor interactions.

State and persistence behavior: State is ABI layout only. Callback addresses and CR3-encoded PFNs are stored in Xen vCPU contexts and shared structures outside this header.

Dependencies and integration points: Included by `interface.h` under `CONFIG_X86_32`. Integrated with PV trap handling, GDT selector setup, vCPU initialization, TSC timestamp ABI, and p2m/m2p virtual windows.

Risks and test signals: Risks include selector constants or CR3 packing regressions that break 32-bit PV guests. Test 32-bit Xen PV boot, context save/restore, callback delivery, high page-table base encoding, and compatibility with Xen public headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_32.h -->
