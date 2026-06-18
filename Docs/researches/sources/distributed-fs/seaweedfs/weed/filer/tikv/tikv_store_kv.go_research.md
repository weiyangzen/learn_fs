# sources/distributed-fs/seaweedfs/weed/filer/tikv/tikv_store_kv.go

## Purpose

`tikv/tikv_store_kv.go` implements generic KV operations for the TiKV store. It was read as a complete 49-line file.

## Important APIs, Types, and Functions

`KvPut`, `KvGet`, and `KvDelete` use `store.getTxn(ctx)` and `TxnWrapper.RunInTxn` to set/get/delete keys. Missing gets map through `isNotExists` to `filer.ErrKvNotFound`.

## Control Flow

Each operation either joins an existing transaction from context or opens and commits its own transaction.

## State and Persistence Behavior

KV data persists under raw keys passed by the caller, unlike metadata keys that use `store.getKey` keyPrefix. This can be intentional global KV behavior or a namespace inconsistency.

## Dependencies and Integration Points

Depends on TiKV `txnkv.KVTxn`, `TikvStore` transaction wrapper, and filer KV errors.

## Risks and Edge Cases

No keyPrefix is applied here, so multiple stores sharing TiKV can collide. Missing-key detection uses brittle string matching. No TTL or CAS semantics.

## Test Signals

Generic store tests should cover put/get/update/delete and transaction integration; explicit prefix isolation tests are advisable.
