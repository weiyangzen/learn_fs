# sources/compression/zlib/crc32.c

Purpose: Implements zlib's CRC-32 calculation, table generation, hardware/braided acceleration paths, and CRC combination APIs.

Important APIs, types, and functions: Public exports are `get_crc_table()`, `crc32_z()`, `crc32()`, `crc32_combine_gen64()`, `crc32_combine_gen()`, `crc32_combine_op()`, `crc32_combine64()`, and `crc32_combine()`. Internal helpers include `byte_swap()`, `multmodp()`, `x2nmodp()`, `make_crc_table()`, `braid()`, `crc_word()`, and `crc_word_big()`. Compile-time controls include `DYNAMIC_CRC_TABLE`, `MAKECRCH`, `HAVE_S390X_VX`, `ARMCRC32`, `Z_TESTN`, `Z_TESTW`, `N`, and `W`.

Control flow: Static builds include generated `crc32.h`; dynamic builds initialize tables through `z_once(&made, make_crc_table)`. `crc32_z()` handles null-buffer initialization, preconditions the CRC, optionally uses ARM CRC32 instructions, otherwise aligns input, processes large spans with N-way braided word CRCs on little or big endian machines, finishes remaining bytes with the byte table, and postconditions the result. `crc32()` delegates to an s390x hook when enabled. Combination functions compute x^(len*8) modulo the polynomial and merge CRCs.

State and persistence: CRC tables and x-power tables are static global data, either compiled in or generated once. The dynamic-table mode uses zlib's once primitive but comments still warn callers to initialize before threaded use in some configurations. `MAKECRCH` turns the file into a generator executable that writes `crc32.h`.

Dependencies and integration points: Includes `zutil.h`, generated `crc32.h` in static-table builds, optional s390x vector hooks, and optional ARM inline assembly. This file is compiled into core zlib and the `zlib1-dll` contrib target.

Risks: Acceleration paths depend on compile-time architecture macros and unaligned/word access assumptions after explicit alignment. Negative lengths for combine generation return zero. Dynamic table generation must be correct before concurrent CRC use. Big-endian and less-common `N`/`W` combinations are more specialized and need regression coverage.

Test signals: Core zlib checks exercise known CRC values and combine behavior; `MAKECRCH` can regenerate table headers. `zlib1-dll` builds include this file, giving additional compile/link coverage for Windows DLL packaging.
