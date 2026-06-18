# sources/distributed-fs/seaweedfs/weed/filer/etcd/etcd_store_kv.go

## Purpose
This file implements SeaweedFS KV operations for the etcd backend.

## Important APIs, Types, and Functions
- `KvPut` stores a raw key/value pair under the configured etcd key prefix.
- `KvGet` retrieves the value or returns `filer.ErrKvNotFound`.
- `KvDelete` deletes the key.

## Control Flow and State
Operations concatenate `store.etcdKeyPrefix` with `string(key)` and call etcd `Put`, `Get`, or `Delete`. Get returns the first KV value if present.

## State and Persistence Behavior
KV state persists directly as etcd keys separate from filer metadata only by caller-provided key namespace and the shared prefix. Values are raw bytes.

## Dependencies and Integration Points
It uses the etcd client in `EtcdStore` and the SeaweedFS KV error contract.

## Risks and Edge Cases
- Raw key bytes are converted to string and concatenated with the same prefix used for metadata, so namespace collisions depend on callers.
- Delete of a missing key is treated as success.
- No transaction or compare-and-swap semantics are exposed.

## Test Signals
Tests should cover put/get/delete, missing key, binary keys, prefix isolation, and backend errors. No enabled local KV tests are listed.
