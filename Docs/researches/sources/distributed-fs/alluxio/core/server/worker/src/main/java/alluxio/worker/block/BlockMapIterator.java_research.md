# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMapIterator.java

Purpose: `BlockMapIterator` batches worker block-location maps into gRPC `LocationBlockIdListEntry` groups for streamed worker registration.

Important APIs are constructor, `hasNext`, `next`, and `getBatchCount`. Control flow first merges directory-level `BlockStoreLocation` entries into tier/medium-level `BlockStoreLocationProto` lists because the master expects blocks grouped by tier and medium. Iteration tracks current tier index and global block counter, returning up to `WORKER_REGISTER_STREAM_BATCH_SIZE` block IDs per call, possibly spanning multiple tiers. `getBatchCount` computes total batches from merged block count and batch size.

State and persistence are iterator state over copied/merged block ID lists; no persistence. Dependencies include Alluxio configuration, gRPC block list protos, and block store locations. Integration points include `RegisterStreamer` used by `BlockMasterClient.registerWithStream`. Risks include `hasNext` returning true when `mCurrentBlockLocationIndex == size` because of `||` logic if the current iterator is exhausted, potential empty `LocationBlockIdListEntry` if called in edge cases, and memory copy cost for large block maps. No direct tests in this subset.
