## sources/distributed-fs/beegfs/storage/source/components/chunkbalancer/ChunkBalancerFileSyncSlave.cpp

### Purpose
`ChunkBalancerFileSyncSlave.cpp` implements the worker that migrates chunk files for storage balancing. It copies a chunk to the destination, updates metadata stripe information, removes the original chunk, and handles mirrored chunks through buddy group IDs.

### Important APIs, Types, And Functions
The constructor selects `CHUNKFILERESYNCER_FLAG_CHUNKBALANCE`. `syncLoop()` fetches `ChunkSyncCandidateFile` entries, validates that the basename matches `EntryInfo::getEntryID()`, resolves the owning metadata node, selects mirrored or non-mirrored resync mode, calls `ChunkFileResyncer::doResync()`, sends `UpdateStripePatternMsg`, removes secondary buddy copies via `sendRemoveChunkPathsMessage()`, removes the source with `removeChunk()`, and prunes empty parent chunk dirs.

### Control Flow, State, And Persistence
For mirrored chunks, the worker reads from the mirror FD and converts source/destination target IDs to buddy group IDs before updating metadata. Stripe pattern update happens after copy, even when the copy reports `PATHNOTEXISTS`, so metadata learns the copy result. Persistent effects include destination chunk creation, metadata stripe changes, remote secondary deletion, local unlink, and possible parent directory removal.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `ChunkFileResyncer`, metadata and storage node stores, target mappers, buddy group mappers, `ChunkStore`, and chunk-balancing message types. Risks include orphaned chunks if metadata update or deletion fails, source deletion after partial success, confusing local target ID rewrite for mirrored chunks, and a busy loop when the queue is empty. Tests should cover ID mismatch rejection, mirrored migration, non-mirrored migration, metadata communication failure, source/secondary delete failure, and `PATHNOTEXISTS` handling.
