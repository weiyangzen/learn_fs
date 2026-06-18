# sources/distributed-fs/seaweedfs/weed/filer/elastic/v7/elastic_store_kv.go

## Purpose
This build-tagged file implements KV operations for the Elasticsearch filer store using a dedicated KV index.

## Important APIs, Types, and Functions
- `KvPut` marshals `ESKVEntry{Value}` and indexes it by raw key string.
- `KvGet` gets a document by raw key string and unmarshals the value.
- `KvDelete` deletes by raw key string and treats `"deleted"` and `"not_found"` as success.

## Control Flow and State
KV put writes to `indexKV` using `indexType` and document id `string(key)`. KV get maps Elasticsearch not found to `filer.ErrKvNotFound`; other failures are logged and also returned as not found. Delete checks the delete result and returns an error for unexpected outcomes.

## State and Persistence Behavior
Values persist as JSON documents with a binary field under `.seaweedfs_kv_entries`, whose mapping disables normal indexing and marks `Value` as binary.

## Dependencies and Integration Points
It depends on the `elastic` build tag, olivere Elasticsearch client, jsoniter, glog, and SeaweedFS KV error semantics.

## Risks and Edge Cases
- Raw binary keys are converted to string document ids and may not be safe or portable for all byte sequences.
- Non-not-found get errors are collapsed to `ErrKvNotFound`, which hides backend failures.
- `Type(indexType)` remains in use for ES8 compatibility via the v7 client and may be sensitive to server version.

## Test Signals
Build-tagged integration tests should cover binary keys, missing keys, overwrite, delete not found, and backend error propagation.
