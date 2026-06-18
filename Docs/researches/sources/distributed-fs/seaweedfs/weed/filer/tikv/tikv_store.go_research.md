# sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store.go

## Purpose

`tikv/tikv_store.go` implements a TiKV-backed transactional filer metadata store behind the `tikv` build tag. It was read as a complete 466-line file.

## Important APIs, Types, and Functions

`TikvStore` owns a `txnkv.Client`, `onePC`, `batchCommitSize`, and `keyPrefix`. It implements filer store CRUD, folder-child batch deletion, prefixed listing, transactions, `TxnWrapper`, key hashing helpers, and `Shutdown`.

## Control Flow

Initialization configures TiKV security, PD addresses, key prefix, one-phase commit, and batch delete size. Entry keys are `keyPrefix + sha1(dir) + name`. Operations get a transaction from context or create one, run the operation, and auto-commit unless participating in an outer transaction. Directory deletion scans by prefix and deletes in batches. Listing iterates lexicographic keys, filters start/include/prefix, lazily deletes expired entries, and invokes callbacks.

## State and Persistence Behavior

Metadata persists in TiKV under hashed directory prefixes. Transactions are real TiKV transactions when `BeginTransaction` is used; otherwise each operation creates and commits its own transaction.

## Dependencies and Integration Points

Depends on `tikv/client-go/v2/txnkv`, TiKV security config, SeaweedFS entry serialization, `filer_pb.ErrNotFound`, and `glog`.

## Risks and Edge Cases

`isNotExists` checks `err.Error() == "not exist"`, which is brittle. Directory hash collisions are possible in theory. `KvPut` in the companion file does not apply keyPrefix. TTL cleanup during list calls `DeleteEntry` while iterating in a transaction, which can interact with transaction context.

## Test Signals

No TiKV-specific tests in this subset. Needed coverage includes transaction commit/rollback, batch deletion, prefix listing, TTL cleanup, key prefixing, and missing-key errors.
