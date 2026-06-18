<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strcmp.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strcmp.S

## Purpose
`strcmp.S` implements RISC-V string comparison with an optional Zbb-accelerated aligned path.

## Important APIs, Types, And Functions
`strcmp` is exported and aliased as `__pi_strcmp`. The scalar loop compares bytes. The `strcmp_zbb` alternative uses `orc.b`, `rev8`, and branchless result synthesis when Zbb/toolchain support is present.

## Control Flow
Boot alternatives patch a jump to the Zbb path when available. The scalar path advances byte by byte until mismatch or NUL. The Zbb path uses word loads for aligned strings until a word differs or contains NUL, falling back to byte comparison for misalignment or NUL/mismatch resolution.

## State And Persistence
No state is retained.

## Dependencies And Integration Points
It depends on alternative patching, RISC-V Zbb hwcap/toolchain support, endian handling, and kernel string API users.

## Risks
The optimized path must return negative/zero/positive with correct lexicographic byte order. Word loads require aligned addresses. Endian reversal is required before word comparison on little-endian.

## Test Signals
String selftests with aligned/misaligned inputs, Zbb and non-Zbb boots, and early boot alias use are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strcmp.S -->
