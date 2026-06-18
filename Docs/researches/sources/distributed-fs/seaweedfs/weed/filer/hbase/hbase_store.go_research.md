# sources/distributed-fs/seaweedfs/weed/filer/hbase/hbase_store.go

## Purpose

`hbase_store.go` implements SeaweedFS filer metadata storage on HBase. It registers `HbaseStore`, creates or verifies the target table with metadata and KV column families, and stores filer entries as encoded bytes keyed by full path.

## Important APIs, Types, and Functions

`HbaseStore` contains a gohbase client, table bytes, KV family name, metadata family name, and column qualifier. It implements the filer store CRUD/list interface with `Initialize`, `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryEntries`, `ListDirectoryPrefixedEntries`, no-op transaction methods, and `Shutdown`.

## Control Flow

Initialization opens a gohbase client, sets family names (`kv`, `meta`) and column `a`, probes the table, and creates it via an admin client if HBase reports `TableNotFound`. Entry insertion encodes attributes/chunks, gzips large chunk lists, and writes to the metadata family with optional HBase TTL. Reads fetch the row from the metadata family, translate `filer.ErrKvNotFound` to `filer_pb.ErrNotFound`, and decode the entry.

Listing uses `NewScanRange` from `dirPath.Child(prefix)` with no explicit stop row, then breaks when returned rows no longer have the expected prefix. Each row is filtered so only direct children of the requested directory are returned. Delete-folder-children scans the same prefix and deletes only direct children, not arbitrary descendants.

## State and Persistence Behavior

Metadata rows are stored under row key `entry.FullPath`, family `meta`, qualifier `a`. Generic KV rows use family `kv` in `hbase_store_kv.go`. Entry TTL is forwarded to HBase puts when positive, using HBase's TTL option. Transactions are no-ops, so multi-step filer operations are not atomic at this layer.

## Dependencies and Integration Points

The file depends on `github.com/tsuna/gohbase`, HBase scanner semantics, SeaweedFS filer entry encoding, and SeaweedFS store registration. It integrates with HBase table administration during startup and the shared filer store interface used by metadata replay and normal filer RPCs.

## Risks and Edge Cases

Scans have no upper stop row and rely on prefix checks to stop. `DeleteFolderChildren` only deletes direct children, so recursive semantics depend on higher layers if needed. HBase durability is set by the lower helper to `AsyncWal`, trading safety for performance. `FindEntry` maps non-not-found read errors through unchanged except for `filer.ErrKvNotFound`; caller behavior should be checked for transient HBase failures.

## Test Signals

Validation should cover table auto-creation, insert/find/delete, TTL propagation, list prefix and start-file behavior, direct-child filtering, scanner close behavior, and failure modes for missing tables or HBase connectivity.
