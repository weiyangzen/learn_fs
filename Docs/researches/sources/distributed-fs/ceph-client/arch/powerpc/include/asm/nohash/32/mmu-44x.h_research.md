# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/nohash/32/mmu-44x.h

Purpose: defines 44x/47x software-loaded TLB bit fields, context type, early TLB reservations, page-size selections, and patch-site symbols for nohash 32-bit MMU code.

Important APIs/types/functions: macros cover MMUCR TID/STS, 44x TLB word indexes and EPN/RPN/ERPN/attribute/permission/page-size bits, 47x TLB0/TLB1/TLB2 equivalents, `PPC44x_TLB_SIZE`, `mm_context_t`, `tlb_44x_hwater`, `tlb_44x_index`, patch symbols, early debug TLB constants, `PPC_PIN_SIZE`, selected `PPC44x_TLBE_SIZE`, `PPC47x_TLBE_SIZE`, `mmu_virtual_psize`, `mmu_linear_psize`, and PGD/PTE assembly offset masks.

Control flow: low-level TLB miss/refill and setup code uses these constants to compose TLB entries, track high-water/index state, reserve early debug mappings, and pin lowmem mappings.

State and persistence: runtime state includes TLB entries, software high-water/index variables, mm context IDs, active flags, and vDSO pointer. Hardware TLB state persists until invalidated or overwritten.

Dependencies and integration points: depends on `asm-const.h`, selected page-size Kconfig, nohash MMU handlers, early debug, and vDSO context management.

Risks: bit definitions are hardware ABI; mismatched 44x/47x formats cause translation faults. Unsupported `PAGE_SIZE` triggers a build error. Early debug consumes an extra TLB entry and changes available pinned mappings.

Test signals: boot 44x and 47x kernels with supported page sizes, run TLB miss/refill stress, early debug mapping tests, vDSO mapping checks, and lowmem pinning validation.
