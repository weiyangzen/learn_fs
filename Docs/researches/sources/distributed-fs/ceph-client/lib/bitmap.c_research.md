<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap.c -->
# sources/distributed-fs/ceph-client/lib/bitmap.c

## Purpose
Provides core generic bitmap operations for equality, set logic, shifting, cutting, setting/clearing, allocation, remapping, NUMA mapping, and array conversion.

## APIs, Types, and Functions
Exports many helpers including `__bitmap_equal()`, `__bitmap_or_equal()`, `__bitmap_complement()`, `__bitmap_shift_right()`, `__bitmap_shift_left()`, `bitmap_cut()`, `__bitmap_and()`, `__bitmap_or()`, `__bitmap_xor()`, `__bitmap_andnot()`, `__bitmap_replace()`, `__bitmap_intersects()`, `__bitmap_subset()`, weight helpers, `__bitmap_set()`, `__bitmap_clear()`, `bitmap_find_next_zero_area_off()`, `bitmap_remap()`, `bitmap_bitremap()`, optional `bitmap_onto()` and `bitmap_fold()` under `CONFIG_NUMA`, allocation/devm allocation helpers, and 32/64-bit array conversion helpers.

## Control Flow, State, and Persistence
Most operations iterate over full `unsigned long` words and mask the final partial word with `BITMAP_LAST_WORD_MASK()` when results must ignore unused tail bits. Shift helpers handle word and intra-word offsets separately. `bitmap_cut()` removes a bit range and shifts later bits downward. Set/clear helpers build first/last masks and apply whole words between. `bitmap_find_next_zero_area_off()` scans for aligned zero ranges, retrying after occupied bits. Remap functions use the ordinal of set bits in an old-domain bitmap to map into a new-range bitmap, with modulo wrapping if the new map is smaller. Allocation helpers wrap `kmalloc_array()` and devres cleanup. Array conversion handles `BITS_PER_LONG` 32/64 differences and clears tail bits. State is entirely caller-owned except devm cleanup registrations.

## Dependencies and Integration
Depends on `linux/bitmap.h`, bitops/find-bit helpers, device-managed resources, slab allocation, export support, and NUMA configuration. It is always built by `lib/Makefile` and underpins cpumasks, nodemasks, ID maps, drivers, filesystems, and scheduler/resource code.

## Risks and Test Signals
Risks include in-place use where not supported (`bitmap_remap()`, `bitmap_onto()`, `bitmap_fold()` early-return), tail-bit mishandling, zero-size or shift >= nbits edge cases, modulo-by-zero if callers misuse `bitmap_fold()` with `sz == 0`, alignment arithmetic overflow in zero-area search, and endian/word-size conversion mistakes. Test signals include `CONFIG_TEST_BITMAP`, random bitmap algebra property tests, partial-word boundaries, overlapping source/destination cases, 32-bit and 64-bit builds, NUMA mapping examples, devm cleanup, and fuzzing shift/cut/remap parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/bitmap.c -->
