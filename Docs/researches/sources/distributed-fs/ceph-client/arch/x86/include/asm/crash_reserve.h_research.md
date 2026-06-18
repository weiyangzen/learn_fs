
# sources/distributed-fs/ceph-client/arch/x86/include/asm/crash_reserve.h

Purpose: x86 crashkernel reservation limits and default low-memory sizing.

Important APIs and control flow: defines 16 MiB `CRASH_ALIGN`, low/high reservation maxima by 32/64-bit mode, `DEFAULT_CRASH_KERNEL_LOW_SIZE`, and `HAVE_ARCH_ADD_CRASH_RES_TO_IOMEM_EARLY`. `crash_low_size_default()` returns zero on 32-bit and on 64-bit returns the maximum of SWIOTLB default plus 8 MiB and 256 MiB.

State, dependencies, and risks: state is crashkernel reservation sizing. Dependencies include SWIOTLB sizing and physical address limits for paging mode transitions. Risks include reserving memory above the kdump kernel's addressing mode, underallocating low memory for DMA/SWIOTLB, and architecture-specific alignment waste. Test signals are crashkernel command-line parsing, kdump boot, and 5-level-to-4-level paging jump scenarios.
