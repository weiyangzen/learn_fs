# sources/distributed-fs/ceph-client/arch/mips/mm/maccess.c

Purpose: architecture policy hook for kernel nofault reads.

Important APIs/functions: `copy_from_kernel_nofault_allowed(const void *unsafe_src, size_t size)` returns true only when the source address has the top address bit set, treating that as kernel space.

Control flow: simple address check, no memory access.

State and persistence: no state.

Dependencies and integration: built when EVA is disabled. Used by generic nofault memory access helpers to reject user-like source addresses.

Risks and test signals: address-space split assumptions must match MIPS kernel layout. Test kernel text/data/vmalloc addresses accepted and user addresses rejected on 32-bit and 64-bit non-EVA configurations.
