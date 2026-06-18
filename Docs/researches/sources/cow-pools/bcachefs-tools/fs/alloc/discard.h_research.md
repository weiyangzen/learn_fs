# File Research: sources/cow-pools/bcachefs-tools/fs/alloc/discard.h

Public header for discard and cached-bucket invalidation work.

Exports:
- Fast discard queue APIs: `bch2_fast_discard_bucket_add()`, `bch2_fast_discard_bucket_del()`, and `bch2_fast_discards_to_text()`.
- Discard diagnostics via `bch2_discards_to_text()`.
- Normal discard scheduling and worker entry points: `bch2_do_discards_async()`, `bch2_do_discards_going_ro()`, `bch2_do_discards_work()`, and `bch2_do_discards_fast_work()`.
- Invalidation worker entry points: `bch2_do_invalidates_work()`, `bch2_dev_do_invalidates()`, and `bch2_do_invalidates()`.
- Per-device and filesystem discard init/exit functions.

Important inline policy:
- `should_invalidate_buckets()` targets roughly `nbuckets / 32` free buckets beyond stripe watermark reserve and clamps the result by cached-bucket count.

Role:
- Used by foreground allocation to trigger discards, generation cleanup, and cached-data invalidation when free-space pressure makes those actions useful.
