# sources/distributed-fs/ceph/src/mon/MonitorDBStore.h

## Purpose
`MonitorDBStore.h` defines the monitor's local persistent key/value store wrapper. It hides the configured `KeyValueDB` backend, gives Paxos services a common transaction format, supports synchronous and serialized asynchronous commits, exposes iterators used by monitor-store synchronization, and stores small out-of-band metadata files such as backend type, creation version, creation time, and minimum monitor release. The class is implemented almost entirely in the header, so callers use it as both the monitor database facade and the transaction builder API.

## Important APIs, Types, and Functions
The core type is `MonitorDBStore`, with members for the filesystem path, `KeyValueDB` instance, optional transaction dump streams, a `Finisher` named `io_work`, and an `is_open` guard. `get_devname()`, `get_path()`, and `get_priority_cache()` expose backend identity and cache integration.

`Op` is the encoded transaction operation. It supports `OP_PUT`, `OP_ERASE`, `OP_COMPACT`, and `OP_ERASE_RANGE` through `Transaction`, carries `prefix`, `key`, `endkey`, and value `bufferlist`, and has versioned encode/decode plus formatter dumping. `Transaction` owns a list of `Op`s and tracks approximate `bytes` and `keys`. It offers typed `put()`/`erase()` helpers for string and `version_t` keys, range erase, prefix/range compaction, append, append-from-encoded, size accounting, and formatter dumping.

`apply_transaction()` converts a `MonitorDBStore::Transaction` to a `KeyValueDB::Transaction`, optionally writes a binary or JSON transaction dump, applies data mutations synchronously, and triggers asynchronous compaction only after the write succeeds. `C_DoTransaction` and `queue_transaction()` serialize asynchronous commits through the `Finisher`; `flush()` blocks until queued IO drains. `StoreIteratorImpl` and `WholeStoreIteratorImpl` implement synchronization chunks as transactions, with optional CRC accumulation under `mon_sync_debug`.

Read/lifecycle APIs include `get_synchronizer()`, prefixed and whole-space `get_iterator()`, value and `version_t` `get()`, `exists()`, `clear_key()`, `clear()`, `_open()`, `open()`, `create_and_open()`, `close()`, compaction helpers, estimated size, `write_meta()`, and `read_meta()`.

## Control Flow
Creation/opening starts with metadata. `open()` reads `kv_backend`, backfills it to `rocksdb` for old stores, calls `_open()`, opens the backend, raises perf-counter priority, starts `io_work`, and marks the store open. `create_and_open()` first writes `ceph_version_when_created` and `created_at`, chooses `g_conf()->mon_keyvaluedb` when no backend metadata exists, creates the backend, starts `io_work`, and marks the store open. `_open()` trims trailing slashes, opens `<path>/store.db`, configures transaction dumping, and initializes RocksDB with monitor-specific options when appropriate.

Callers build a `TransactionRef` using helper methods. Synchronous paths call `apply_transaction()` directly. Asynchronous paths call `queue_transaction()`, which queues `C_DoTransaction`; that callback can inject configured transaction delay, calls `apply_transaction()`, and completes the caller's `oncommit` context without monitor locks held. `close()` asserts no pending work, stops the finisher, clears `is_open`, and drops the DB pointer.

Store synchronization uses `get_synchronizer()` with a start key and sync-prefix set. `WholeStoreIteratorImpl::get_chunk_tx()` walks the whole-space iterator, skips prefixes outside the sync set, appends one PUT operation per selected KV pair until byte/key limits would be exceeded, records the next key in `last_key`, and marks `done` at iterator exhaustion. `get_next_key()` advances to the next synchronizable raw key.

## State and Persistence
Persistent monitor service data lives in the `KeyValueDB` backend under service prefixes and string keys. Transaction encoding is separate from backend encoding and is used for dumping and sync reconstruction. Metadata keys written with `write_meta()` are plaintext files under the monitor store path and are available before the DB is open. `do_dump`, dump file descriptors, and `dump_fmt` are debug state, not cluster state.

The store serializes queued writes through one `Finisher`, so transaction order is preserved for `queue_transaction()`. Compactions are explicitly deferred until after a successful write. `Transaction::bytes` is approximate and used for sync chunk sizing, not durable metadata. `read_meta()` strips trailing whitespace; `get(prefix,key)` returning a `version_t` treats `ENOENT` as zero but aborts on other read errors.

## Dependencies and Integration Points
The class depends on `KeyValueDB`, Ceph `bufferlist` encoding, `Context`, `Finisher`, `PriorityCache`, `safe_io`, block-device lookup, monitor config, debug/logging, and perf counters. It is used by monitor Paxos services for `put_version()`, `put_last_committed()`, health encoding, one-off local metadata, and direct cleanup operations such as removing mkfs bootstrap keys.

## Risks
Error handling is intentionally fatal for unexpected DB write/read failures: failed transaction submission aborts the process, and invalid operation types abort. `close()` requires the caller to flush/drain first. The async transaction callback sleeps inside the finisher when delay injection is enabled, which preserves ordering but can stall all later monitor DB writes. `Transaction::append()` adds the other transaction's full initial byte overhead as well as operations, so byte accounting is approximate.

Iterator chunking writes every synchronized key as a separate PUT operation; that is simple but can be inefficient for large stores. `get_next_key()` advances the iterator before returning the key, so consumers must rely on the documented behavior. Transaction dumping must be configured with valid output paths; binary dump close is unconditional if dumping was enabled.

## Test Signals
Useful tests include encode/decode round trips for `Op` and `Transaction` versions, all operation types through `apply_transaction()`, dump JSON/binary paths, async queue ordering and completion return codes, metadata read/write before open, missing-version `get()` returning zero, synchronization chunks respecting prefix filters and byte/key limits, and lifecycle assertions around `flush()`/`close()`.
