# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/tlbflush.h

Purpose: selects the correct Book3S TLB flush header for 32-bit or 64-bit builds.

Important APIs/types/functions: includes the 64-bit or 32-bit `tlbflush.h` implementation based on architecture configuration.

Control flow: compile-time include dispatch only.

State and persistence: no state; it exposes the active TLB flush API to common code.

Dependencies and integration points: used by page-table and mmu_gather code across Book3S variants.

Risks: selecting the wrong header would dispatch to unavailable or semantically wrong hash/radix flush functions.

Test signals: 32-bit and 64-bit build coverage and runtime unmap/mprotect tests on both modes.
