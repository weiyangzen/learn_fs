# File Research: sources/block-storage/lvm2/lib/misc/lvm-maths.c

This file provides simple integer math helpers.

APIs:
- `gcd(unsigned long n1, unsigned long n2)` using Euclidean algorithm.
- `lcm(unsigned long n1, unsigned long n2)` as `(n1 / gcd(n1, n2)) * n2`, returning 0 if either input is 0.

Risk:
- `lcm()` can overflow `unsigned long`; callers must ensure range safety.
