# sources/distributed-fs/ceph-client/arch/x86/xen/mmu_hvm.c

Purpose: Installs HVM-specific Xen MMU hooks for page-table lifetime notification and vmcore RAM classification.

Important APIs/types/functions: With vmcore support, `xen_vmcore_pfn_is_ram()` queries `HVMOP_get_mem_type` so kdump avoids ballooned/MMIO-DM pages. `xen_hvm_exit_mmap()` notifies Xen via `HVMOP_pagetable_dying` when an mm's page table is being destroyed. `is_pagetable_dying_supported()` probes the hypercall. `xen_hvm_init_mmu_ops()` installs `pv_ops.mmu.exit_mmap` and registers the vmcore callback.

Control flow and state: Initialization probes support once and conditionally changes the MMU op table. The vmcore callback is registered globally when configured. No separate private state is kept.

Dependencies and integration points: It depends on HVM hypercalls, generic `pv_ops.mmu`, crash dump vmcore callbacks, and Xen HVM memory-type semantics.

Risks and test signals: Missing pagetable-dying notifications can leave stale hypervisor shadow state; wrong vmcore classification can fault or corrupt crash dumps. Signals include HVM guest process churn, Xen logs for pagetable dying support, kdump vmcore reads with ballooned pages, and no warnings from `HVMOP_get_mem_type`.
