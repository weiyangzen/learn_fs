# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/qjournal/server/TestJournaledEditsCache.java

Purpose: Tests `JournaledEditsCache`, the in-memory cache used by `Journal` to serve recent edit logs through RPC for in-progress tailing.

Important APIs/types/functions: `JournaledEditsCache`, `storeEdits`, `retrieveEdits`, `CacheMissException`, `getCapacity`, `DFS_JOURNALNODE_EDIT_CACHE_SIZE_KEY`, `DFS_JOURNALNODE_EDIT_CACHE_SIZE_FRACTION_KEY`, `EditLogFileOutputStream.writeHeader`, and `QJMTestUtil` transaction helpers.

Control flow: Setup sizes the cache for 100 single-transaction edits. Tests store segments and retrieve leading, trailing, boundary, off-boundary, over-end, and multi-segment ranges. Capacity tests force eviction or oversized-batch behavior. Layout-version tests verify headers and cache misses for mixed layouts. Gap, uninitialized, malformed input, and config tests validate error paths.

State and persistence behavior: Cache buffers and layout metadata are in-memory only. Temporary test directory cleanup is incidental.

Dependencies and integration points: Supports `Journal.getJournaledEdits` and QJM RPC tailing, relying on edit-log serialization and layout headers.

Risks: Boundary bugs can return missing, duplicate, or uncommitted edits. Mixed layout versions must not be merged.

Test signals: Passing confirms slicing, miss amounts, eviction, gap detection, malformed request rejection, header correctness, and capacity config precedence.
