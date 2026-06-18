# sources/distributed-fs/eos/unit_tests/mgm/tgc/LruTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/tgc/LruTests.cc

Purpose: tests `Lru`, the least-recently-used file-id queue used by tape garbage collection.

Important APIs and types: `Lru`, `FidQueue`, `fileAccessed`, `fileDeletedFromNamespace`, `getAndPopFidOfLeastUsedFile`, `size`, `empty`, `maxQueueSizeExceeded`, `toJson`, and exceptions `MaxQueueSizeIsZero`, `QueueIsEmpty`, and `MaxLenExceeded`.

Control flow: construction tests validate queue-size rules. Empty-pop throws. Ordered access tests confirm least-recently-used pop order and that re-accessing an existing fid moves it to the most-recent side. Deletion removes namespace-deleted fids. Max-size tests verify queue truncation/exceeded flag semantics. A disabled performance test exists for 500000 files. JSON tests verify MRU-to-LRU hex formatting and max-length exception behavior.

State and persistence: in-memory queue and index only. No namespace I/O; deletion is simulated through API calls.

Dependencies and integration: LRU feeds selection of candidate files for TGC eviction/cleanup. JSON output integrates with status reporting.

Risks and test signals: queue truncation intentionally retains older candidates after over-capacity insertion, so semantics must be understood before changing. JSON string exactness is brittle but useful for API compatibility.
