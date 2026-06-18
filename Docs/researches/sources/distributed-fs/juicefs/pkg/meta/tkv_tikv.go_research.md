# sources/distributed-fs/juicefs/pkg/meta/tkv_tikv.go

## Purpose
`tkv_tikv.go` adapts TiKV transaction KV storage to JuiceFS metadata, enabled unless `notikv` is set. It also provides TiKV-specific changelog sharding and GC handling.

## Important APIs, Types, and Functions
Important types are `tikvTxn`, `tikvClient`, `logMergeHeap`, and `logMergeItem`. Key functions include `newTikvClient`, `tiKVChangeLogShards`, `logKey`, `scanLogRange`, `rewind`, `simpleTxn`, `txn`, `scan`, `reset`, and `gc`.

## Control Flow and State
Client creation parses `tikv://`-style addresses, configures TLS security from query parameters, sets PingCAP logging level, parses `gc-interval`, creates a txnkv client, optionally enables TSO follower proxy and max TSO batch wait, and wraps the KV store in a path prefix. Normal writes begin a TiKV transaction, optionally at a context-provided startTS, run the closure, then enable 1PC and async commit before commit. `simpleTxn` begins with `math.MaxUint64` startTS for latest point reads and rejects writes. Scans use low-priority snapshots and restart after GC-too-early errors.

## State and Persistence Behavior
Metadata persists in TiKV under the configured prefix. Transaction ids are TiKV start timestamps and are used for changelog ordering. Changelog keys are sharded as `XLOG<shard><id>` with a configurable shard count, and scans merge shard iterators using a heap. `config("startTS")` exposes a timestamp for consistent V2 dumps. `gc` advances TiKV safe point according to `gcInterval`.

## Dependencies and Integration Points
It depends on PingCAP/TiKV client-go, PD options, oracle timestamp helpers, and `prefixClient`. It integrates with `tkv.go` changelog/dump logic, slice cleanup GC, and external TiKV tests.

## Risks and Test Signals
Risks include service dependency complexity, GC-too-early scan restarts, changelog shard merge bugs, timestamp rewind windows missing logs, TLS/query misconfiguration, and write-conflict string matching. Tests include `TestTiKVClient` and shared metadata behavior, but TiKV changelog sharding and GC need targeted integration tests.
