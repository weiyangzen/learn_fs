# sources/distributed-fs/juicefs/pkg/meta/sql_bak.go

## Purpose

`sql_bak.go` implements the protobuf-based SQL metadata backup and restore path. It complements the older JSON tree dump/load code in `sql.go` with segmented dump/load handlers for format, counters, nodes, chunks, edges, symlinks, sustained open-deleted files, delayed-delete files, slice refs, ACLs, xattrs, quotas, and directory stats. The build tag matches the SQL backends.

## Important APIs, Types, And Functions

`sqlDumpBatchSize` controls row batching at 100,000. `dump` orders all dump segment functions and uses one repeatable-read read-only transaction when `DumpOption.Threads == 1`; multithreaded dumps warn that the database must be externally read-only for consistency. `execTxn` reuses a dump-scoped transaction when present, otherwise uses `roTxn`.

`sqlQueryBatch` partitions id ranges and uses `errgroup` with `opt.Threads` as a concurrency limit. Dump functions map SQL rows to `pkg/meta/pb` messages: `dumpNodes`, `dumpChunks`, `dumpEdges`, `dumpSymlinks`, `dumpCounters`, `dumpSustained`, `dumpDelFiles`, `dumpSliceRef`, `dumpACL`, `dumpXattr`, `dumpQuota`, and `dumpDirStat`. `dumpEdges` also derives `pb.Parent` records for hardlink parent counts.

The restore dispatcher `load` routes segment types to `loadFormat`, `loadCounters`, `loadNodes`, `loadChunks`, `loadEdges`, `loadSymlinks`, `loadSustained`, `loadDelFiles`, `loadSliceRefs`, `loadAcl`, `loadXattrs`, `loadQuota`, and `loadDirStats`. `insertRows` is the common batched insert helper. `insertSliceRefs`, `upsertSliceRef`, and `genMultiSQL` handle backend-specific insert-ignore/upsert behavior for `chunk_ref`.

## Control Flow

Dumping starts by optionally opening a single read-only transaction and installing it in context. Each segment function scans the relevant table, batches protobuf records, and sends `dumpedResult` messages to the output channel. Node dumping first emits trash nodes, then scans normal inode id ranges. Chunk and edge dumping scan by table `id`, while small tables are read whole. Restore reverses that mapping by converting protobuf messages back into xorm beans and writing them in transaction-sized chunks.

## State And Persistence Behavior

The code serializes the SQL backend's normalized state instead of walking only a directory tree. This preserves non-tree metadata such as counters, sustained inodes, deleted files, slice refs with non-default ref counts, ACL rows, xattrs, quotas, and dir stats. Chunk loading inserts chunk rows first, then derives default `sliceRef` rows from chunk slice buffers. Explicit `SliceRefs` segments then upsert non-default reference counts.

## Dependencies And Integration Points

The file depends on xorm sessions from `dbMeta`, protobuf message types in `pkg/meta/pb`, ACL rule encoding/decoding, `errgroup`, `proto.Message`, and the same SQL transaction helpers from `sql.go`. It integrates with the generic metadata dump/load framework through segment constants such as `segTypeNode` and `segTypeQuota`.

## Risks And Edge Cases

Multithreaded dump mode can produce inconsistent backup data unless callers enforce database quiescence. `sqlQueryBatch` logs the row count before `eg.Wait`, so the debug count may be incomplete at log time. Large whole-table reads for symlinks, sustained rows, deleted files, ACLs, xattrs, quotas, and dir stats may be memory-heavy. Restore correctness depends on chunk-ref insertion/upsert semantics matching each backend dialect and on duplicate handling not masking real data corruption.

## Test Signals

No direct tests in `sql_test.go` target this protobuf backup path. Indirect confidence comes from shared metadata dump/load code and SQL backend tests, but backup consistency, multithreaded dump behavior, hardlink parent reconstruction, and chunk-ref upsert behavior need backend-specific integration tests.
