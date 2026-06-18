# File Research: sources/block-storage/thin-provisioning-tools/src/copier/batcher.rs

Batching helper for copy operations.

Key behavior:
- `CopyOpBatcher` accumulates `CopyOp`s up to a configured batch size.
- `push` appends and sends the batch when capacity is reached.
- `complete` sends remaining operations.
- `send_ops` sorts each batch by destination block before sending over a `SyncSender<Vec<CopyOp>>`.

Purpose:
- Larger batches improve chances of adjacent destination ordering and better sequential I/O, especially for spindle devices.
- Used by cache writeback to hand batches to a copy worker thread.
