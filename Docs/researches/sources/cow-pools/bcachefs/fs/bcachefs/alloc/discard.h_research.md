# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/discard.h

Public header for discard and invalidation work.

Exports:
- Fast discard queue APIs: `bch2_fast_discard_bucket_add()`, `bch2_fast_discard_bucket_del()`, text dump helper.
- Normal discard worker entry points and async scheduling.
- Going-read-only discard pressure handling.
- Invalidation worker entry points and per-device/global invalidation scheduling.
- Device/filesystem discard init and exit functions.

Inline policy:
- `should_invalidate_buckets()` computes how many cached buckets should be invalidated to keep roughly `nbuckets / 32` buckets free above stripe watermark reserve, clamped by cached bucket count.

Dependencies:
- Includes `alloc/buckets.h` for usage and reservation helpers.
- Consumed by allocator foreground code to trigger cached-data invalidation under free-space pressure.
