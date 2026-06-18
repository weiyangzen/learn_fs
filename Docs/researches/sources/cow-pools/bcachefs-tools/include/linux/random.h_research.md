# File Research: sources/cow-pools/bcachefs-tools/include/linux/random.h

This header implements random byte/value helpers using the Linux `getrandom` syscall when available, otherwise reading from an external `urandom_fd`. `get_random_bytes()` asserts the requested byte count was returned.

It defines typed `get_random_*()` helpers and bounded uniform-ish helpers `get_random_u32_below()` and `get_random_u64_below()`. The bounded functions use multiply-high rejection sampling to reduce modulo bias, with optimized branches for 8-bit, 16-bit, 32-bit, and 64-bit ceilings.
