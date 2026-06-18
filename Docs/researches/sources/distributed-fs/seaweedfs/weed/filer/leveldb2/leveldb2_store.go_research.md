# sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store.go

## Purpose

`leveldb2_store.go` implements a sharded local LevelDB filer store. It spreads directories across a fixed number of LevelDB databases by MD5 hash, improving write/read concurrency and reducing single-DB hot spots compared with the original LevelDB store.

## Important APIs, Types, and Functions

`LevelDB2Store` holds `dbs`, `dbCount`, and `ReadOnly`. It implements standard filer store methods. Helpers `genKey`, `genDirectoryKeyPrefix`, `getNameFromKey`, and `hashToBytes` encode keys as `md5(directory) + filename` and derive partition ID from the last hash byte.

## Control Flow

Initialization creates the root directory, checks writability, and opens `dbCount` subdirectories named `00`, `01`, etc. with Bloom filters, cache settings, and optional read-only mode. Each metadata operation hashes the directory to choose one partition, then operates within that LevelDB. Listing and child deletion only scan the partition for that directory hash, so all names in a directory remain colocated and sorted by filename suffix.

## State and Persistence Behavior

Metadata is persisted across multiple LevelDB folders. The key no longer stores the directory string, only its MD5 digest plus filename, so collisions are theoretically possible but unlikely. Transactions are no-ops; deletes for one directory use a batch within one partition.

## Dependencies and Integration Points

The file depends on `goleveldb`, MD5 hashing, local filesystem storage, SeaweedFS entry encoding, and the filer store registry. It is suitable for local filer deployments that want directory-level sharding without a remote database.

## Risks and Edge Cases

Changing `dbCount` after data exists changes partition mapping and makes existing entries unreachable. MD5 hash collisions would merge directory keyspaces. `ReadOnly` still calls `MkdirAll`/writability checks during initialization. Iterator errors are not inspected after release. Large single-directory deletes can create large write batches.

## Test Signals

Tests should cover create/find/list with multiple partitions, stable hashing for a fixed db count, read-only initialization behavior, delete-folder children in one partition, and failure when db count changes across restarts.
