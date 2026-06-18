# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractBulkDeleteTest.java

Purpose: generic contract tests for the `BulkDelete` API, including wrapper/reflection paths used by libraries supporting multiple Hadoop versions.

Important APIs/types/functions: `AbstractFSContractTestBase`, `FileSystem.createBulkDelete`, `BulkDelete.bulkDelete`, `WrappedIO.bulkDelete_delete`, `DynamicWrappedIO.bulkDelete_pageSize`, `CommonPathCapabilities.BULK_DELETE`, `touch`, `intercept`, and helper `assertSuccessfulBulkDelete`.

Control flow/state/persistence: setup initializes FS, base path named after the test class, `DynamicWrappedIO`, page size, and directory creation. Tests validate page size, list-size preconditions, successful deletion through wrapped and direct FS APIs, capability declaration, rejection of paths outside base or non-absolute paths, success for nonexistent paths, undefined-but-nonfatal directory/file combinations, failure entries for non-empty parent directories, success for empty directories and empty lists, duplicate path handling, deep descendant deletion, and child path batches. Tests skip cases needing more paths than the implementation page size.

Dependencies/integration points: contract spans default and store-specific bulk delete implementations. Reflection wrappers validate compatibility behavior for applications using `WrappedIO` instead of direct compile-time APIs.

Risks/test signals: catches security boundary errors around base path validation, page-size enforcement mistakes, capability mismatches, incorrect treatment of directories/nonexistent paths, duplicate path handling, and divergence between direct and wrapped API behavior.
