## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDelete.java

Purpose: unstable public API for deleting batches of files or objects, especially object-store keys, without promising atomicity or directory marker preservation.

Important APIs and types: extends `IOStatisticsSource` and `Closeable`; exposes `pageSize()`, `basePath()`, and `bulkDelete(Collection<Path>)` returning failed path/message entries.

Control flow: no implementation. Contract requires submitted paths to be absolute, under `basePath`, no more than `pageSize`, and files/objects rather than directories.

State and persistence behavior: implementations may hold store clients/statistics and must be closed to release resources and update IO statistics. Deletions persist in the backing filesystem/object store.

Dependencies and integration points: created by `BulkDeleteSource`; callers can use `BulkDeleteUtils` for validation; support should be advertised through `CommonPathCapabilities.BULK_DELETE`.

Risks: non-atomic and idempotent semantics mean retries can delete newly created objects at the same keys. Large batches can stress object-store write IOPS. Directories are unsupported with undefined outcomes.

Test signals: implementation tests should cover page-size enforcement, base-path validation, partial failures, retry/idempotency behavior, statistics close behavior, and directory inputs.
