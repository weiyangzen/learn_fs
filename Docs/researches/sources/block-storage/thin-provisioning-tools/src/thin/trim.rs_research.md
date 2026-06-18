# File Research: sources/block-storage/thin-provisioning-tools/src/thin/trim.rs

## Purpose
Implements `thin_trim`: discard unused regions of a thin-pool data device based on the data space-map allocation bitmap in metadata.

## Main Components
- `RangeIterator` iterates allocated ranges from unpacked space-map bitmap blocks.
- `find_first_set()` finds the next nonzero refcount entry in a bitmap slice.
- `find_first_unset()` finds the next zero refcount entry in a bitmap slice.
- `ioctl_blkdiscard()` wraps Linux `BLKDISCARD`.
- `read_bitmaps()` reads all bitmap blocks referenced by the data space-map bitmap index btree.
- `trim_data_device()` validates data device size, iterates allocated ranges, and issues discard calls for gaps between allocated ranges.
- `ThinTrimOptions`, `Context`, `mk_context()`, and `trim()` form the command entry point.

## Behavior
The command reads the thin metadata superblock, unpacks the data space-map root, computes the data block size in bytes, and checks the data device is at least `root.nr_blocks * block_size`. It then reads every bitmap block named by the bitmap index.

`RangeIterator` yields used ranges, not free ranges. `trim_data_device()` tracks `last_seen`; every gap before the next used range is discarded using byte offsets and lengths. After iteration, any trailing free region up to `root.nr_blocks` is also discarded.

Bitmap entries are considered used if they are anything other than `BitmapEntry::Small(0)`. This includes small nonzero counts and non-small/overflow encodings.

## Dependencies and Interactions
The file relies on:
- command engine creation,
- `file_size()` for data-device validation,
- Linux ioctl request construction,
- btree walking/conversion for bitmap index entries,
- space-map bitmap unpacking,
- report debug logging.

## Research Notes
All bitmap blocks are read up front. A comment notes this may exceed 64k bitmap blocks for very large pools, but the implementation still materializes the full vector. `RangeIterator::new()` validates that provided bitmaps cover `nr_blocks`.
