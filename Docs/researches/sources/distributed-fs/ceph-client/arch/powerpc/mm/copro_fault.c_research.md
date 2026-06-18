# sources/distributed-fs/ceph-client/arch/powerpc/mm/copro_fault.c

Purpose: handles memory faults and SLB calculations for PowerPC coprocessors such as SPU/AFU devices that access process address spaces.

Important APIs and control flow: `copro_handle_mm_fault()` validates the target `mm`, finds and locks the VMA, checks read/write access against VMA flags, calls `handle_mm_fault()`, translates `VM_FAULT_*` errors to `-ENOMEM` or `-EFAULT`, and unlocks unless the fault completed. Under hash MMU, `copro_calculate_slb()` builds a `copro_slb` ESID/VSID pair for user, vmalloc, IO, and linear-map regions using slice page size and segment-size helpers.

State and dependencies: it mutates normal process page tables through the generic fault path and reads hash context/slice state to construct SLB entries. Dependencies include VMA locking, `radix_enabled()`, region-id helpers, VSID generation, and exported coprocessor ABI structures. Risks are divergence from `do_page_fault()`, underchecking pkeys or execute faults, stale SLB calculations after slice conversion, and incorrect handling of completed/retry faults. Test signals include AFU/SPU page fault tests, invalid access propagation, radix-vs-hash behavior, and SLB calculation for all region IDs.
