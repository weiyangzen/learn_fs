# File Research: sources/block-storage/thin-provisioning-tools/src/thin/migrate/stream.rs

This file defines migration stream abstractions and implementations.

Key elements:
- `ChunkContents` is `Copy`, `Skip`, or `Discard`.
- `Chunk` stores offset, length, and contents.
- `Stream` trait provides `next_chunk()` and `size_hint()`.
- `DevStream` emits a single `Copy` chunk covering an entire file/device.
- `ThinStream` wraps `ThinIterator` and emits:
  - `Copy` chunks for contiguous mapped thin blocks
  - `Skip` chunks for gaps before the next mapped thin block
  - `None` at end of mappings
- `ThinStream::contiguous_run()` advances the btree iterator through adjacent logical thin blocks.
- A `DeltaStream` sketch exists only inside a block comment.

Interactions:
- `ThinStream` is used by migration copy logic in `base.rs`.
- Uses `ThinIterator` from `metadata.rs`.

Risks and notes:
- `ChunkContents::Discard` exists but no active stream emits it in this file.
- `ThinStream::size_hint()` reports mapped data size, not full virtual device size.
- Offsets and lengths are based on metadata data block size units as used by migration copy code.
