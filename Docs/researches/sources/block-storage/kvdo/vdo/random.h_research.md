# File Research: sources/block-storage/kvdo/vdo/random.h

Read completely: 55 lines.

This header wraps Linux kernel randomness for the VDO/UDS code. It declares `random_in_range()` and `random_compile_time_assertions()`, defines `fill_randomly()` as a direct `get_random_bytes()` wrapper, defines `RAND_MAX` as `2147483647`, and implements `random()` by filling a `long` and masking it with `RAND_MAX`.

Dependencies: Linux `get_random_bytes()`, local compiler/type definitions.

Security/reliability notes: the API mimics C library `random()`/`RAND_MAX` naming inside kernel code. The masked `random()` only returns 31 random bits even when `long` is wider.
