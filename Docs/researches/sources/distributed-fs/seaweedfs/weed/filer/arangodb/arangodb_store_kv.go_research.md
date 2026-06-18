# sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_kv.go

## Purpose
This file implements SeaweedFS KV operations for the ArangoDB store using a dedicated KV collection.

## Important APIs, Types, and Functions
- `KvPut` creates or updates a document keyed by `hashString(".kvstore."+string(key))`.
- `KvGet` reads the document and returns decoded metadata bytes or `filer.ErrKvNotFound`.
- `KvDelete` removes the document and maps errors to not found after logging.

## Control Flow and State
`KvPut` builds a `Model` with the hashed key, a synthetic directory field, and `Meta` converted by `bytesToArray`. It first checks `DocumentExists`, then updates or creates. `KvGet` reads into `Model` and converts `Meta` back to bytes. `KvDelete` removes by the same hash.

## State and Persistence Behavior
KV data persists in `KVMETA_COLLECTION` and uses the same uint64-array binary representation as entry metadata. The key is not stored reversibly except in the synthetic directory field, and document identity is an MD5 hex string.

## Dependencies and Integration Points
Depends on the ArangoDB driver, helper hash/conversion functions, and SeaweedFS KV error contract.

## Risks and Edge Cases
- Using `string(key)` for binary keys can embed unusual bytes in `Directory`, although the document key is hashed.
- `DocumentExists` plus create/update is a read-before-write race under concurrent writers.
- `KvDelete` treats all errors as not found after logging, which can hide connectivity or permission failures from callers.

## Test Signals
Tests should cover binary keys, overwrite, missing key, delete idempotence, and concurrent put races. No local tests are listed.
