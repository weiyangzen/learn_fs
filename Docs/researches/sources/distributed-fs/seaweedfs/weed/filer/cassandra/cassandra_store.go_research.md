# sources/distributed-fs/seaweedfs/weed/filer/cassandra/cassandra_store.go

## Purpose
This file implements the original Cassandra-backed SeaweedFS filer store. It stores metadata in a `filemeta` table keyed by directory and name, supports optional super-large-directory key rewriting, and implements standard filer CRUD/list methods.

## Important APIs, Types, and Functions
- `CassandraStore` holds cluster config, session, and `superLargeDirectoryHash`.
- `Initialize` reads keyspace, hosts, credentials, large-directory config, local DC, and timeout.
- `initialize` configures gocql auth, keyspace, timeout, token-aware host policy, local quorum, session, and super-large-directory hashes.
- Transaction methods are no-ops.
- Store methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.

## Control Flow and State
Insert/update derive directory and name from full path, rewrite large-directory entries to `dirHash+name` with empty name, encode metadata, optionally gzip large chunk metadata, and execute an insert with TTL. Find and delete apply the same key rewrite. Directory deletion deletes by `directory`. Listing scans `filemeta` for one directory and name greater than or greater/equal to the start name, ordered ascending and limited by `limit+1`.

## State and Persistence Behavior
Rows are stored as `(directory, name, meta)` with TTL from `entry.TtlSec`. Super-large-directory mode avoids huge Cassandra partitions by moving file names into the directory key, but listing/deleting such directories returns without doing work. Consistency is local quorum.

## Dependencies and Integration Points
It uses `github.com/apache/cassandra-gocql-driver/v2`, `filer.Entry` encoding, `filer_pb.ErrNotFound`, glog, and SeaweedFS store registration. The expected Cassandra schema must support the queried primary key and ordering.

## Risks and Edge Cases
- Super-large directories cannot be listed or folder-deleted through normal paths.
- Four-character MD5 prefixes for large-directory hashes can collide; initialization fatal-checks configured directories only.
- No transaction support despite implementing transaction methods.
- Prefix listing is unsupported.
- `KvGet` in the companion file has suspicious error mapping; store-level semantics should be tested.

## Test Signals
No local tests are listed. Shared filer tests should cover CRUD, TTL, listing order, unsupported prefixed listing, large-directory behavior, and session shutdown.
