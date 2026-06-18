# sources/distributed-fs/ceph-client/lib/test_bitmap.c

## Purpose
Implements an extensive bitmap API module selftest. It validates bitmap mutation, copying, parsing, printing, region allocation, scatter/gather, array conversion, iteration macros, range scans, bit reads/writes, compile-time constant folding, zero-length behavior, and simple performance timing.

## APIs, Control Flow, and State
The file uses the kselftest module harness and helper assertions that increment `total_tests` and `failed_tests`. `selftest()` runs many focused tests: `test_zero_clear()`, `test_fill_set()`, `test_copy()`, `test_bitmap_region()`, `test_replace()`, `test_bitmap_sg()`, arr32/arr64 round trips, hex and list parsing, list printing, memory-optimization equivalence, `bitmap_cut()`, buffered print helpers, constant-evaluation build assertions, `bitmap_read()`/`bitmap_write()`, read/write timing, weight tests, zero-nbits calls, nth-bit search, set/clear bit iterators, bitrange iterators, clump iteration, and wraparound iteration. Static expected bitmaps and strings cover little slices, multiword layouts, all/empty inputs, malformed ranges, overflow, and very large printed lists.

State is test-only: static buffers in `__initdata`, expected vectors in `__initconst`, and kselftest counters. The module does not persist runtime state after loading.

## Dependencies, Integration, Risks, and Tests
Depends on `linux/bitmap.h`, module/kselftest harness, printk, slab, string helpers, and uaccess headers. It integrates with kernel selftest module loading and validates shared bitmap primitives used by CPU masks, nodemasks, allocators, drivers, and filesystems. Risks include architecture-sensitive expectations around word size and tail clearing, very large expected strings being brittle, performance logs not enforcing thresholds, and NULL pointer zero-nbits tests relying on APIs not dereferencing pointers in that case. Test signals are direct: kselftest pass/fail counters, detailed `pr_err`/`pr_warn` lines, build-time `BUILD_BUG_ON()` failures, and timing output for parser/read/write loops.
