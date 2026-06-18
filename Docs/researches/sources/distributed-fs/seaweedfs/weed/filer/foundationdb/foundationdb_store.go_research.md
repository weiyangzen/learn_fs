# sources/distributed-fs/seaweedfs/weed/filer/foundationdb/foundationdb_store.go

## Purpose

`foundationdb_store.go` implements SeaweedFS's filer metadata store on FoundationDB behind the `foundationdb` build tag. It registers `FoundationDBStore` as a filer store, maps file entries into FoundationDB directory subspaces, provides a separate KV subspace, and adds FoundationDB-specific safeguards around transaction size, transaction duration, directory-list limits, and optional write batching.

## Important APIs, Types, and Functions

The exported store surface is the filer store contract: `GetName`, `Initialize`, `BeginTransaction`, `CommitTransaction`, `RollbackTransaction`, `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, directory listing methods, `KvPut`, `KvGet`, `KvDelete`, and `Shutdown`. `FoundationDBStore` holds the opened `fdb.Database`, `seaweedfsDir`, `kvDir`, configurable directory prefix, timeout fields, and batching controls.

The private `writeOp` and `writeBatcher` types buffer put/delete operations into FoundationDB transactions. `genKey` packs `(dirPath, fileName)` into the metadata subspace using a pooled `tuple.Tuple`; `extractFileName` unpacks scan keys back to names.

## Control Flow

Initialization sets defaults for cluster file, API version, timeout strings, directory prefix, and disabled-by-default batching, validates durations, calls `fdb.APIVersion`, opens the database, creates/open the metadata and KV directory subspaces, and starts `writeBatcher` only when configured. Entry writes encode attributes and chunks, optionally gzip large chunk lists, reject values larger than the 10 MB FDB transaction limit, then either write into an ambient context transaction, submit through the batcher, or run a one-operation transaction.

Reads use an ambient transaction when present, otherwise `ReadTransact`; not-found nil values are translated to `filer_pb.ErrNotFound`. Listings compute an FDB range over the directory tuple prefix, optionally bracket a filename prefix with `fdb.Strinc`, apply a capped limit, decode each value, and call the filer list callback. `DeleteFolderChildren` intentionally ignores any outer transaction and recursively deletes children in batches of 100 entries using independent transactions.

## State and Persistence Behavior

Metadata is persisted under `directoryPrefix` as tuple keys `(directory, filename)` and encoded `filer.Entry` bytes. Generic KV state is persisted under `directoryPrefix/kv` as tuple-packed byte keys. Context transactions hold uncommitted mutations until explicit commit, but recursive folder deletion is not atomic with a caller transaction. Optional batching preserves durability before returning because `submit(..., wait=true)` waits for the batch transaction result.

## Dependencies and Integration Points

The file depends on Apple's FoundationDB Go bindings, FDB directory layers, tuple packing, SeaweedFS filer entry encoding, and SeaweedFS utility gzip helpers. It integrates with SeaweedFS's store registry, metadata replication/replay through the shared filer store interface, and any component using the filer KV API for offsets or auxiliary state.

## Risks and Edge Cases

FDB's transaction limits drive most risk: a single oversized entry is rejected, and large recursive deletes are reliable but non-atomic. Directory listings are capped to 1000 even when callers pass larger limits, so pagination must be correct. Prefix scans rely on tuple ordering and `Strinc`; malformed keys are skipped with warnings. The context transaction is stored via `context.Value`, so callers must use the returned context. Batcher shutdown closes the stop channel and flushes pending ops, but write latency increases by the configured interval.

## Test Signals

Useful tests cover config parsing, API-version/cluster availability, key round trips, not-found error translation, transaction double-begin/commit/rollback states, batched versus non-batched insert benchmarks, KV benchmarks, and large/nested `DeleteFolderChildren` behavior both inside and outside ambient transactions.
