# File Research: sources/cow-pools/bcachefs-tools/include/linux/sort.h

Declares `sort_r()` and provides a simple `sort()` wrapper around libc `qsort()`. Also defines `cmp_int()` and nonatomic aliases.

Full kernel-style heap sort with private comparator support is implemented in `linux/sort.c`.
