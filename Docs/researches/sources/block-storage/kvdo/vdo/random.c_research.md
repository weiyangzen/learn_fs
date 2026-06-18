# File Research: sources/block-storage/kvdo/vdo/random.c

Read completely: 19 lines.

This file provides `random_in_range()` and `random_compile_time_assertions()`. `random_in_range()` returns `lo + random() % (hi - lo + 1)`. The compile-time assertion verifies that `RAND_MAX + 1` is a power of two, matching the masking approach in the header implementation of `random()`.

Dependencies: `random.h` and `permassert.h`.

Security/reliability notes: `random_in_range()` has modulo bias unless the range evenly divides `RAND_MAX + 1`, and it assumes `hi >= lo`.
