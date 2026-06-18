## sources/distributed-fs/ceph-client/arch/powerpc/include/asm/copro.h

Purpose: declares helpers for coprocessor address translation and fault handling on PowerPC systems that expose coprocessor-side memory access.

Important APIs/types/functions: `struct copro_slb` stores ESID/VSID pairs, `copro_handle_mm_fault()` handles a coprocessor fault against an `mm_struct`, and `copro_calculate_slb()` derives an SLB entry for an effective address.

Control flow: implemented elsewhere; callers pass an mm, effective address, DSISR-like status, and receive fault status or SLB values. The header defines the interface between coprocessor fault code and core MM.

State and persistence: no local state. It reads and updates process address-space state through `mm_struct` and fault handling, while SLB values are transient translation descriptors.

Dependencies and integration: depends on `linux/mm_types.h` and integrates with PowerPC MM, SLB management, and accelerator/coprocessor drivers.

Risks and test signals: incorrect SLB computation or fault result propagation can expose wrong address spaces, mishandle permissions, or livelock a coprocessor. Test signals include coprocessor driver fault tests, mmap/unmap stress while devices access memory, page fault accounting, and MMU context teardown races.
