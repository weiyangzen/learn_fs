# sources/distributed-fs/seaweedfs/weed/filer/abstract_sql/abstract_sql_store.go

## Purpose
This file implements the common SQL-backed SeaweedFS filer metadata store. Backend-specific SQL generators provide statements, while this store handles filer entry serialization, CRUD, directory listing, transactions, retry hooks, and optional S3 bucket-per-table behavior.

## Important APIs, Types, and Functions
- `SqlGenerator` defines statement factories for insert, update, find, delete, delete-folder-children, list-exclusive/list-inclusive, create-table, and drop-table.
- `AbstractSqlStore` embeds the generator and stores `*sql.DB`, bucket-table support, a protected bucket table cache, and an optional retryable-error callback.
- `BucketAware` methods: `CanDropWholeBucket`, `OnBucketCreation`, and `OnBucketDeletion`.
- Transaction methods: `BeginTransaction`, `CommitTransaction`, `RollbackTransaction`, and internal `getTxOrDB`.
- Filer store methods: `InsertEntry`, `UpdateEntry`, `FindEntry`, `DeleteEntry`, `DeleteFolderChildren`, `ListDirectoryPrefixedEntries`, `ListDirectoryEntries`, and `Shutdown`.
- Table helpers: `isValidBucket`, `CreateTable`, and `deleteTable`.

## Control Flow and State
Operations call `getTxOrDB` to select either a transaction from context key `"tx"` or the base DB. If bucket tables are enabled and the path is under `/buckets/<bucket>`, the method maps the filer path to a bucket table and a short path, lazily creating and caching the table after S3 bucket-name validation. Inserts encode the entry as protobuf bytes, optionally gzip metadata for large chunk lists, then insert by directory hash, name, directory, and metadata. Duplicate insert errors fall back to update. Updates and deletes execute their generated statements and check `RowsAffected`. Finds scan the metadata blob and decode it into `filer.Entry`. Listings query by hashed directory, start name, directory, prefix pattern, and `limit+1`, invoking `eachEntryFunc` until it stops or errors.

## State and Persistence Behavior
The persisted row stores directory hash, name, full directory string, and encoded metadata. The full directory protects against hash collisions in statement predicates. Bucket-table mode persists each bucket's object metadata in a separate SQL table and deletes an entire table when deleting bucket-root children. Transactions are carried through context, and retry wrappers are skipped inside transactions.

## Dependencies and Integration Points
It integrates with the SeaweedFS `filer.FilerStore` interface, `filer.BucketAware`, `util.FullPath`, `filer.Entry` protobuf encoding, `filer_pb.ErrNotFound`, S3 bucket name validation, and backend SQL dialect implementations. `util.RetryUntil` handles retryable database errors when configured.

## Risks and Edge Cases
- The context key `"tx"` is a plain string, which can collide with other context users.
- Duplicate detection depends on error text containing "duplicate entry"; non-English or dialect-specific messages may bypass fallback.
- `RowsAffected` is checked only for API support, not for actual row count.
- Bucket table names come from bucket strings through backend SQL generator code; injection safety depends on generators quoting/validating identifiers.
- Listing returns `limit+1` rows but does not stop by `limit` itself; callers may rely on the extra row to page.
- `DeleteFolderChildren` drops a bucket table when bucket root maps to `/`, which is efficient but broad.

## Test Signals
Coverage should use shared filer store tests for insert/update/find/delete/list, transaction commit/rollback, bucket-table creation/deletion, duplicate insert fallback, compressed metadata decoding, and prefix listings. This file has no local tests in the listed set.
