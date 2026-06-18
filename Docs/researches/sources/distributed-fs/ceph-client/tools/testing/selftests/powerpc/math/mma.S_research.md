<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.S

Purpose: PowerPC assembly helper for the MMA selftest. It exercises matrix multiply assist accumulator setup, one signed halfword GER operation, and result extraction into VSX registers.

Important APIs and types: Exports the global `test_mma` entry. It uses `lxvh8x`, raw encodings for `xxsetaccz`, `xvi16ger2s`, and `xxmfacc`, then stores four vector words with `stxvw4x`.

Control flow: The caller passes two 8x16-bit matrices and a 4x4 32-bit output image in argument registers. The routine loads operands, clears the MMA accumulator, performs one rank-2 update, deprimes accumulator state, stores four result vectors, and returns with `blr`.

State and persistence: No persistent software state is kept. The only mutable architectural state is transient VSX/MMA accumulator content and the caller-provided output buffer.

Dependencies and integration points: Integrated only through `mma.c`, the powerpc math Makefile, and hardware with MMA support. It depends on assembler acceptance of VSX mnemonics plus raw opcodes for newer MMA instructions.

Risks: The raw `.long` encodings are opaque to older tools and must match the ISA exactly. Register argument ordering is fragile because the routine directly consumes ABI registers and does not preserve temporary VSX state beyond the selftest contract.

Test signals: A passing `mma` selftest on MMA-capable hardware validates instruction availability, accumulator save/restore behavior, and the expected 4x4 result image.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/mma.S -->
