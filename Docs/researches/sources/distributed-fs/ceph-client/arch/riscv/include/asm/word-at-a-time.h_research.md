<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/word-at-a-time.h

Purpose: Implements word-at-a-time byte scanning primitives for RISC-V string operations.

Important APIs/types/functions: Defines `WORD_AT_A_TIME_CONSTANTS`, `has_zero()`, `prep_zero_mask()`, `create_zero_mask()`, `find_zero()`, and related zero-byte helpers.

Control flow: String routines load machine words and use arithmetic/bit operations to detect zero bytes efficiently.

State and persistence: No persistent state.

Dependencies and integration points: Used by generic string helpers such as strlen/strnlen and user string routines.

Risks: Endian or word-size mistakes produce overreads or wrong string lengths.

Test signals: KUnit string tests, endian/word-size builds, KASAN/UBSAN, and user string boundary tests.

Source read size: 76 lines, 1766 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/word-at-a-time.h -->
