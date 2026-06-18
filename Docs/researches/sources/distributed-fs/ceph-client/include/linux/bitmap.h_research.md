# sources/distributed-fs/ceph-client/include/linux/bitmap.h

## Purpose
`bitmap.h` declares and inlines the generic Linux bitmap API: allocation helpers, bitwise set operations, scans, transformations, region allocation, endian-aware array conversions, and small-field reads/writes. It is a central utility header used by block queues, CPU masks, cgroups, allocation maps, and any component that stores dense bit state in arrays of `unsigned long`.

## Important APIs, Types, And Functions
The allocation surface is `bitmap_alloc()`, `bitmap_zalloc()`, node-aware variants, `bitmap_free()`, `DEFINE_FREE(bitmap, ...)`, and device-managed `devm_bitmap_alloc()`/`devm_bitmap_zalloc()`. Core operations include `bitmap_zero()`, `bitmap_fill()`, `bitmap_copy()`, `bitmap_copy_clear_tail()`, logical operations (`bitmap_and()`, `bitmap_or()`, `bitmap_xor()`, `bitmap_andnot()`, `bitmap_complement()`, `bitmap_replace()`), comparisons (`bitmap_equal()`, `bitmap_or_equal()`, `bitmap_intersects()`, `bitmap_subset()`, `bitmap_empty()`, `bitmap_full()`), weights (`bitmap_weight()`, `bitmap_weight_and()`, `bitmap_weight_andnot()`, `bitmap_weight_from()`), ranges (`bitmap_set()`, `bitmap_clear()`), shifts, remapping (`bitmap_remap()`, `bitmap_bitremap()`, `bitmap_onto()`, `bitmap_fold()`), and sparse/dense conversions (`bitmap_scatter()`, `bitmap_gather()`).

The conversion helpers bridge bitmap storage with fixed-width arrays: `bitmap_from_arr32()`, `bitmap_to_arr32()`, `bitmap_from_arr64()`, `bitmap_to_arr64()`, `BITMAP_FROM_U64()`, and `bitmap_from_u64()`. `bitmap_read()` and `bitmap_write()` read or write values up to `BITS_PER_LONG` at arbitrary bit offsets, including cross-word cases. `BITMAP_FIRST_WORD_MASK()`, `BITMAP_LAST_WORD_MASK()`, and `bitmap_size()` define the sizing and tail-mask rules.

## Control Flow And State
Most public functions are `static __always_inline` wrappers that choose a fast single-word path when `small_const_nbits(nbits)` is true, a byte-oriented path when alignment permits `memcpy()`/`memset()`/`memcmp()`, or an out-of-line `__bitmap_*()` implementation in `lib/bitmap.c` for general multiword cases. `bitmap_set()` and `bitmap_clear()` additionally special-case single-bit updates and byte-aligned constant ranges before falling back to `__bitmap_set()`/`__bitmap_clear()`.

`bitmap_scatter()` and `bitmap_gather()` iterate `for_each_set_bit()` over a mask and assign target bits with `__assign_bit()`. Region allocation uses `bitmap_find_free_region()` to scan power-of-two aligned regions, `bitmap_allocate_region()` to test and set a region, and `bitmap_release_region()` to clear it. There is no hidden persistence: state lives only in caller-provided bitmap memory or allocated bitmap storage.

## Dependencies And Integration Points
The header depends on `linux/bitops.h`, `linux/find.h`, `linux/bitmap-str.h`, `linux/align.h`, string primitives, errno values, and type definitions. Architecture-specific bitops and `lib/bitmap.c` supply the heavy implementations. It integrates directly with block queue bitmaps, tag maps, cgroup policy bitmaps, and any subsystem using `DECLARE_BITMAP()`.

## Risks And Test Signals
Primary risks are tail-bit leakage, off-by-one masks, invalid `nbits` to `bitmap_read()`/`bitmap_write()`, endian conversion mistakes on 32-bit big-endian systems, and non-atomic use where callers actually require atomic bitops. Test signals should include single-word and multiword bitmaps, unaligned starts, cross-word reads/writes, `nbits` not divisible by `BITS_PER_LONG`, BE/LE conversion checks, region allocation failure paths, and scatter/gather equivalence tests.
