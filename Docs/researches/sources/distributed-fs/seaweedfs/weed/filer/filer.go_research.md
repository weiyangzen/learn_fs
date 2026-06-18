<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer.go

## Purpose
Defines the central `Filer` type and core metadata operations: construction, peer bootstrap/aggregation, store setup, entry creation/update/find/listing, TTL expiry, empty-directory cleanup, attributes, and shutdown.

## Important APIs and Types
`Filer` holds store, master client, deletion queues, metadata log buffer, config, remote storage, singleflight groups, lock manager, deletion retry queue, empty folder cleaner, and persisted log cache. Key methods include `NewFiler`, `MaybeBootstrapFromOnePeer`, `AggregateFromPeers`, `SetStore`, `CreateEntry`, `ensureParentDirectoryEntry`, `UpdateEntry`, `FindEntry`, `doListDirectoryEntries`, `DeleteEmptyParentDirectories`, `IsDirectoryEmpty`, `Shutdown`, `GetEntryAttributes`, and `IsDirectoryKeyObject`.

## Control Flow and State
`NewFiler` initializes clients, queues, config, lock manager, persisted-log cache, and starts deletion processing. `CreateEntry` handles root no-op, name-length checks, directory TTL reset, atime defaults, optional existing-entry reuse, inode assignment, parent creation, insert/update, metadata notification, and stale chunk deletion. `FindEntry` returns root, filters expired TTL/S3-expiry entries, deletes expired metadata/data, and falls back to lazy remote fetch on misses. Listing calls lazy remote listing, filters expired entries after iteration, then may clean empty parents.

## Persistence Behavior
Metadata persists through `VirtualFilerStore`. Store identity is persisted in KV key `filer.store.id`. Metadata events are appended to `LocalMetaLogBuffer`, which later flushes to filer system-log files. Data deletion is asynchronous via `fileIdDeletionQueue`.

## Dependencies and Integration Points
Integrates with masters through `wdclient.MasterClient`, peer metadata aggregation, distributed lock ring updates, S3 bucket naming, empty-folder cleanup, remote storage lazy fetch/list, stats, and store wrappers.

## Risks
Create/update correctness depends on callers holding proper path locks. TTL deletion during find/list has side effects in read paths. Parent auto-creation promotes files to directories to support S3 flat-key semantics, which is surprising for POSIX-like users. Shutdown assumes `Store` and `LocalMetaLogBuffer` are initialized. Lazy remote fallbacks trade consistency for availability.

## Test Signals
Inode behavior is covered by `filer_inode_test.go`; lazy remote miss/fetch/listing by `filer_lazy_remote_test.go`; wrapper context semantics by wrapper tests. This file's peer aggregation, TTL deletion, and empty-parent cleanup have limited direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer.go -->
