# sources/distributed-fs/ceph-client/mm/kasan/report_hw_tags.c

## Purpose

`report_hw_tags.c` provides the hardware tag-based KASAN implementation of the report helper API. It reads architectural memory tags rather than byte-addressable shadow memory and formats pointer-tag versus memory-tag diagnostics.

## Important APIs, Types, and Functions

The exported helper set is `kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_metadata_fetch_row()`, and `kasan_print_tags()`. It uses `hw_get_mem_tag()`, `KASAN_TAG_INVALID`, `KASAN_GRANULE_SIZE`, and `META_BYTES_PER_ROW`.

## Control Flow

For normal hardware-tag faults, the faulting address is already the first bad granule, so `kasan_find_first_bad_addr()` simply strips the pointer tag and returns the address. Allocation-size recovery walks object granules with `hw_get_mem_tag()` until it sees `KASAN_TAG_INVALID` or reaches `cache->object_size`. Metadata-row fetching synthesizes report rows by reading each granule's hardware tag. `kasan_print_tags()` prints the pointer tag and the hardware memory tag for the bad address.

## State and Persistence Behavior

No storage is owned here. The effective state is in architectural memory tags associated with kernel memory and in slab cache object size metadata. Freed or invalid-tagged objects may cause allocation-size discovery to return 0.

## Dependencies and Integration Points

This file is selected for `CONFIG_KASAN_HW_TAGS` and is called by the common report engine. It depends on architecture support for memory tagging and on common KASAN tag helpers such as `get_tag()` and `kasan_reset_tag()` from the shared headers.

## Risks and Edge Cases

The implementation assumes common report code calls it only for normal memory-access reports where hardware already supplied the precise failing address. It cannot reconstruct fine-grained shadow poison classes like generic KASAN, so final bug type comes from tag-mode stack-ring evidence in `report_tags.c`.

## Test Signals

Signals include hardware tag fault reports with pointer and memory tags, correct object-size reporting before invalid tags, async report behavior from `report.c`, and architecture/MTE tests that verify tag suppression during report printing.
