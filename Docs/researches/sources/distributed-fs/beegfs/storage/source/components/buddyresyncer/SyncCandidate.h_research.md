## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/SyncCandidate.h

### Purpose
`SyncCandidate.h` defines the candidate payloads passed through storage resync and chunk balancing queues. A candidate identifies a relative chunk/directory path and the source target, with optional destination and metadata context for balancing.

### Important APIs, Types, And Functions
`ChunkSyncCandidateDir` stores `relativePath`, `targetID`, optional `destinationID`, copied `EntryInfo`, `isBuddyMirrorChunk`, and copied `FileEvent`. Accessors expose these values, including pointers to the embedded `EntryInfo` and `FileEvent`. `ChunkSyncCandidateFile` derives from the directory candidate and adds no additional fields. `ChunkSyncCandidateStore` aliases `SyncCandidateStore<ChunkSyncCandidateDir, ChunkSyncCandidateFile>`.

### Control Flow, State, And Persistence
The default constructor marks an invalid candidate with `targetID == 0`, which consumers use as a sentinel. Constructors that accept pointers immediately copy `EntryInfo` and `FileEvent`, avoiding dependency on caller lifetimes. There is no persistence beyond in-memory queue storage.

### Dependencies, Integration Points, Risks, And Test Signals
This header integrates buddy resync discovery/sync workers and chunk balancing job queues. Risks include uninitialized optional fields when using the simple constructor, pointer accessors exposing mutable embedded state, and relying on `targetID == 0` as the only invalid marker. Tests should cover simple buddy candidates, balancing candidates with metadata/event copies, default invalid candidates, and queue round-trips.
