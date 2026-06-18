# File Research: sources/cow-pools/bcachefs-tools/include/linux/prandom.h

This header maps pseudo-random APIs to the stronger `get_random_bytes()` interface. `prandom_bytes()` calls `get_random_bytes()`, and typed `prandom_int`, `prandom_long`, `prandom_u32`, and `prandom_u64` helpers fill a local value.

`prandom_u32_max(max)` returns `prandom_u32() % max`, so it may be biased and should not be confused with the rejection-sampling bounded helpers in `random.h`.
