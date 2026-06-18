# File Research: sources/block-storage/thin-provisioning-tools/src/cache/writeback.rs

Implements offline cache writeback: copy dirty blocks from fast/cache device back to origin device, then optionally clear dirty state in metadata.

Main components:
- `WritebackSelector` trait chooses which mapped cache blocks need copy.
- `V1Selector`: uses dirty bit in v1 mapping entries.
- `V2Selector`: uses separate dirty bitset loaded into `RoaringBitmap`.
- `AllSelector`: used after unclean shutdown to conservatively copy all valid mappings.
- `MappingCounter`: counts valid mappings matching a predicate.
- `WritebackBatcher`: walks mapping array and emits `CopyOp`s to a channel.
- `BitsetUpdater`: low-level cursor for clearing bits in the v2 on-disk dirty bitset.
- `ThreadedCopier`: runs copy batches in a worker thread and accumulates cleaned/read-failed/write-failed bitmaps.
- `CacheWritebackOptions`: metadata, origin, fast device paths, offsets, buffer size, failed-list flag, metadata-update flag, retries, report.

Copy strategy:
- Validates metadata version <= 2 and page-aligned offsets.
- Builds selector based on clean shutdown and metadata version.
- First tries vectored synchronous copy.
- Retries failed blocks with simple block I/O.
- Optionally retries with rescue copier for configured retry count.
- Tracks copied and failed cache blocks in roaring bitmaps.

Metadata update:
- v1 clears dirty flags in mapping array blocks and rewrites checksummed array blocks.
- v2 clears bits in the dirty bitset and rewrites checksummed array blocks.
- Reports fatal if not all blocks copied and returns an error.

Notable details:
- `list_failed_blocks` is stored in options but not used in this file.
- `BitsetUpdater` relies on monotonically increasing cleaned block iteration.
