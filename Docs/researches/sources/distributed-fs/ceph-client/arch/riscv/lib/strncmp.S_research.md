<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strncmp.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/strncmp.S

## Purpose
`strncmp.S` implements bounded string comparison with scalar and optional Zbb accelerated paths.

## Important APIs, Types, And Functions
`strncmp` is exported and aliased as `__pi_strncmp`. It accepts two strings and a count. The Zbb path uses aligned word comparison while respecting the byte limit.

## Control Flow
The scalar path iterates until count is reached, a mismatch occurs, or NUL terminates both equal strings. The Zbb path computes an end pointer, processes aligned full words while no NUL and equal, then falls back to byte comparison near limits, misalignment, or termination.

## State And Persistence
No state is retained.

## Dependencies And Integration Points
It depends on alternative patching, Zbb support, endian handling, and kernel string callers.

## Risks
Bounded behavior must never read past the intended safe range in ways that fault. The optimized path must respect count exactly and handle `count == 0` as equal.

## Test Signals
String tests for zero count, partial prefixes, mismatches before/after count, NUL before count, alignment, and Zbb/non-Zbb coverage are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/strncmp.S -->
