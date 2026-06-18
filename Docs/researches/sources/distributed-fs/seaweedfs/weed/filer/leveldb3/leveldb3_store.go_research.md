# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store.go

## Purpose

`leveldb3_store.go` implements a bucket-aware local LevelDB filer store. It stores normal metadata in a default LevelDB and maps S3 bucket contents under `/buckets/<bucket>/...` into separate per-bucket LevelDB databases so whole buckets can be opened, closed, or dropped independently.

## Important APIs, Types, and Functions

`LevelDB3Store` holds the root directory, a map of database name to `*leveldb.DB`, a lock guarding the map, and `ReadOnly`. Store methods mirror LevelDB2. `findDB`, `createDB`, and `closeDB` manage bucket database selection. Key helpers use `md5(directory) + filename` within the selected DB.

## Control Flow

Initialization opens the default `_main` database. `findDB` returns default DB for paths outside `/buckets/`; for bucket paths it extracts the bucket name, rewrites the path to the bucket-local short path, and lazily creates the bucket DB if needed. CRUD/list/delete operations call `findDB`, encode/decode entries, and operate on the chosen DB. Deleting folder children at a bucket root closes and removes the entire bucket DB directory; otherwise it scans and batch-deletes direct children in the selected DB.

## State and Persistence Behavior

The store persists metadata in one LevelDB folder per bucket plus `_main`. Bucket-local keys use short paths, while entries retain full SeaweedFS paths when decoded for callers. Transactions are no-ops. Whole-bucket deletion removes a filesystem directory with `os.RemoveAll` after closing the DB.

## Dependencies and Integration Points

The file depends on LevelDB, filesystem directories, MD5 hashing, SeaweedFS bucket path conventions, and `filer.BucketAware` implemented in the companion bucket file. It integrates with S3 bucket lifecycle paths that can notify the store about bucket creation/deletion.

## Risks and Edge Cases

Bucket name extraction depends on `/buckets/` path shape. `findDB` may create a bucket DB during reads/listing for a missing bucket. Whole-bucket deletion uses `RemoveAll`, so incorrect bucket names or root paths would be destructive. Changing the path convention or hash algorithm would make existing data unreachable. Iterator errors are not checked after release.

## Test Signals

Needed tests include normal and bucket path CRUD, lazy bucket DB creation, whole-bucket drop, concurrent `findDB`/`createDB`, listing path rewrites, and behavior for `/buckets/<bucket>` with and without children.
