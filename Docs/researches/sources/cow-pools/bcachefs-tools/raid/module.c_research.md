# File Research: sources/cow-pools/bcachefs-tools/raid/module.c

## Purpose
RAID implementation initialization and self-test support.

## Initialization
`raid_init()` selects default implementations:
- Portable integer implementations by default.
- SSE2 implementations when available.
- SSSE3 implementations for higher parity and recovery when available.
- AVX2 implementations when available.
- Uses CPU heuristics to choose extended-register or non-extended variants.
- Sets default mode to `RAID_MODE_CAUCHY`.

## Reference Generation
`raid_gen_ref()` computes parity byte-by-byte using generic GF multiplication and the selected generator matrix. It serves as correctness oracle for tests.

## Self-Test
`raid_selftest()`:
- Allocates aligned buffers.
- Uses the GF multiplication table as deterministic test data.
- Computes reference parity for maximum parity.
- Tests parity generation for each parity level.
- Tests recovery of ending data failures.
- Tests recovery with mixed data/parity failures.
- Tests data-only recovery using selected parity blocks.
- Tests scan detection with corrupted data/parity.
- Verifies no-parity scan failure.

## Dependencies
Uses `internal.h`, `memory.h`, and `cpu.h`, plus all generated/optimized RAID implementations through dispatch tables.
