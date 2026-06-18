<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_64.h

Purpose: Supplies 64-bit x86 Xen ABI details: flat segment selectors, hypervisor and m2p virtual ranges, segment-base hypercall selectors, iret stack context, 64-bit CPU register layout, CR3 PFN conversion, vCPU info, and callback address encoding.

Important APIs/types/functions: `FLAT_RING3_CS32`, `FLAT_RING3_CS64`, `FLAT_KERNEL_*`, `FLAT_USER_*`, `__HYPERVISOR_VIRT_*`, `__MACH2PHYS_*`, `SEGBASE_*`, `VGCF_in_syscall`, `struct iret_context`, `struct cpu_user_regs`, `xen_pfn_to_cr3()`, `xen_cr3_to_pfn()`, `struct arch_vcpu_info`, `xen_callback_t`, and `XEN_CALLBACK()`.

Control flow: Xen PV entry/exit and vCPU save/restore code uses these layouts to represent guest registers, syscall versus iret return context, and segment base state. Callback setup passes a RIP-only callback value on 64-bit.

State and persistence behavior: No private state. ABI data persists in vCPU contexts, shared vCPU info, and hypervisor-maintained segment base state.

Dependencies and integration points: Included by `interface.h` on 64-bit builds. Integrates with PV syscall/iret paths, Xen segment-base hypercalls, GDT setup, m2p mapping, and vCPU context exchange.

Risks and test signals: Risks are register layout drift, syscall-return flag mishandling, and 64-bit selector compatibility bugs. Test 64-bit Xen PV boot, syscall and interrupt return paths, segment base updates, save/restore, migration, and ABI comparisons to Xen public headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/xen/interface_64.h -->
