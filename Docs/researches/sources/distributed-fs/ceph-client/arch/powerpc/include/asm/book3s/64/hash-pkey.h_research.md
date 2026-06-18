# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/book3s/64/hash-pkey.h

Purpose: maps PowerPC memory protection key state into hash-MMU PTE bits.

Important APIs/types/functions: provides hash-specific helpers for translating VMA flags to PTE pkey bits and extracting pkey fields from PTE flags, using the `H_PTE_PKEY_BIT*` definitions supplied by the active hash page-size header.

Control flow: inline helpers are conditional on memory-key/MMU support and operate by masking and shifting PTE flag bits. There is no runtime state machine here.

State and persistence: pkey state is persisted in PTE flag bits and per-mm key allocation data defined elsewhere.

Dependencies and integration points: included by `book3s/64/pkeys.h`; depends on hash page-size headers and `mmu_has_feature(MMU_FTR_PKEY)`. It integrates with mprotect/pkey syscalls and access-permission checks.

Risks: hash pkey bit placement differs between 4K and 64K modes. Incorrect mapping can grant or deny memory access unexpectedly. Radix support is intentionally not implemented through this hash helper.

Test signals: pkey allocation and mprotect tests on hash MMU, read/write/execute denial checks, and builds for both 4K and 64K page sizes.
