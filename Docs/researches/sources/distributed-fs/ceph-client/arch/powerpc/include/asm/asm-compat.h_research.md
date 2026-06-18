# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/asm-compat.h

Purpose: provides assembly mnemonic and register-size compatibility macros shared by C inline assembly and assembly files across 32-bit and 64-bit PowerPC.

Important APIs/types/functions: selects `PPC_LL`, `PPC_STL`, `PPC_LCMPI`, `PPC_LONG`, `PPC_LONG_ALIGN`, `PPC_LONG_SHIFT`, `PPC_LONG_SIZE`, `PPC_LONG_ALIGN_BYTES`, and load-reserve/store-conditional forms such as `PPC_LLARX`, `PPC_STLCX`, `PPC_LDARX`, and `PPC_STDCX`. It also defines `stringify_in_c()` for embedding macro-expanded opcodes in C asm strings.

Control flow: compile-time `#ifdef CONFIG_PPC64` or `__powerpc64__` selects 64-bit mnemonics and sizes; otherwise 32-bit forms are used. No runtime control flow exists.

State and persistence: no state is stored. The macros affect generated code and ABI layout assumptions.

Dependencies and integration points: included by atomic, bitops, bug, barriers, and assembly code that needs one source to build for ppc32 and ppc64.

Risks: an incorrect macro here can corrupt atomics, exception code, or data layout across the architecture. The file is sensitive to assembler syntax and the distinction between kernel config and compiler predefined architecture macros.

Test signals: build 32-bit and 64-bit PowerPC configurations, inspect inline assembly for expected `lwz/stw/lwarx/stwcx.` or `ld/std/ldarx/stdcx.` forms, and run atomic/locking stress tests.
