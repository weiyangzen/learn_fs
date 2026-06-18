# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/RedundantEditLogInputStream.java

## Purpose
`RedundantEditLogInputStream` merges redundant finalized edit-log streams with the same start transaction and fails over when the current stream fails. `JournalSet` uses it when multiple journals contain overlapping segments.

## Important APIs, types, and functions
The class extends `EditLogInputStream`. The constructor validates valid first/last txids and identical first txid, then sorts streams by descending last txid. Overrides expose stream names, first/last txid, close, op reading, version, position, length, in-progress state, max op size, and locality. Internal state includes `curIdx`, `prevTxId`, stream array, previous exception, and state machine values `SKIP_UNTIL`, `OK`, `STREAM_FAILED`, `STREAM_FAILED_RESYNC`, and `EOF`.

## Control flow
`nextOp` fast-forwards to `prevTxId + 1`, reads ops, updates `prevTxId`, detects premature EOF, and fails over to the next stream only if it is not shorter than the failed stream. Recovery mode via `nextValidOp` uses `STREAM_FAILED_RESYNC` to resync or bypass premature EOF at the end.

## State and persistence behavior
The class reads edit logs and tracks read/failover state but never writes. It refuses silent failover to shorter streams because that could lose metadata transactions.

## Dependencies and integration points
It depends on `EditLogInputStream`, `FSEditLogOp`, `HdfsServerConstants`, `IOUtils`, `Preconditions`, `Longs`, and `LogThrottlingHelper`. It is constructed by `JournalSet`.

## Risks and invariants
All wrapped streams must be finalized, non-pre-transactional, and share a start txid. The implementation tries each stream once and does not handle journals containing disjoint subsets of edits. Accessors assume a current stream exists.

## Test signals
`TestRedundantEditLogInputStream` is direct coverage. Test sorting, fast-forwarding, IO failover, shorter-stream rejection, premature EOF, recovery resync, close propagation, and max-op-size propagation.
