# sources/distributed-fs/seaweedfs/weed/filer/cassandra2/cassandra_store_kv.go

## Purpose
This file implements KV operations for the Cassandra2 filer store using the `dirhash,directory,name,meta` schema.

## Important APIs, Types, and Functions
- `KvPut` inserts raw value bytes into `filemeta` with TTL 0.
- `KvGet` selects bytes by hash, directory, and name and maps missing or empty values to `filer.ErrKvNotFound`.
- `KvDelete` deletes the KV row.
- `genDirAndName` pads and base64 encodes byte keys into directory/name strings.

## Control Flow and State
The key encoding matches the original Cassandra KV store, but all CQL includes `util.HashStringToLong(dir)`. Put is an upsert-style insert. Get and delete use the same derived key triplet.

## State and Persistence Behavior
KV rows share the Cassandra2 `filemeta` table. The stored value is raw bytes. Directory hash is derived from the base64 first-eight-byte directory string.

## Dependencies and Integration Points
It depends on the Cassandra2 session, gocql errors, filer KV errors, and SeaweedFS hash utilities.

## Risks and Edge Cases
- Like the original Cassandra KV file, missing-key handling is non-obvious and should be covered explicitly.
- Empty values are treated as not found.
- Key padding can make some short binary keys surprising.

## Test Signals
Tests should cover short keys, binary keys, overwrites, missing keys, empty values, and delete. No local tests are listed.
