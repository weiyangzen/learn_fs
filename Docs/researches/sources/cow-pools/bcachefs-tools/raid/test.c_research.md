# File Research: sources/cow-pools/bcachefs-tools/raid/test.c

This file implements RAID self-test helpers for combination generation, insertion/sorting helpers, parity generation, and data recovery.

Test coverage:
- `raid_test_combo()` verifies combination and permutation iterators against recursive binomial/power counts.
- `raid_test_insert()` checks `raid_insert()` keeps arrays sorted across all permutations.
- `raid_test_sort()` checks `raid_sort()` sorts all permutations.
- `raid_test_rec()` tests recovery functions across all data-failure and parity-selection combinations for the chosen mode.
- `raid_test_par()` tests parity generation functions against reference parity output.

Mode handling:
- Cauchy mode tests all 6 parity levels.
- Vandermonde mode tests 3 parity levels.

Backend handling:
- Always tests generic int implementations.
- Adds SSSE3/AVX2/SSE2 variants only when compiled and detected at runtime through CPU feature helpers.

Memory/test pattern:
- Uses RAID memory helpers to allocate aligned vectors.
- Fills deterministic pseudo-random data with fixed seeds.
- Uses saved parity/data buffers and separate test buffers to compare reconstructed output.

Failure behavior:
- Returns `0` on success and `-1` on any mismatch/allocation failure.
