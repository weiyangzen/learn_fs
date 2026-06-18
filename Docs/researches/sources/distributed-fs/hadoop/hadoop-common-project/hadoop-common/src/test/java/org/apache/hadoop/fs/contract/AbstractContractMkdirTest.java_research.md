# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractMkdirTest.java

Purpose: `AbstractContractMkdirTest` validates `FileSystem.mkdirs()` and directory creation semantics.

Important APIs and types: it uses `FileSystem`, `Path`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `ContractTestUtils.assertMkdirs`, `createFile`, `dataset`, and base assertions. The public constant `MKDIRS_NOT_FAILED_OVER_FILE` is used in failure messages.

Control flow: simple tests create and delete directories recursively and non-recursively. Negative tests create a file at the target or as a parent, call `mkdirs()`, and expect `FileAlreadyExistsException`, `ParentNotDirectoryException`, or a relaxed `IOException`; they then verify the original file content survived. Slash handling tests create paths with and without trailing slashes, qualified and unqualified, including multiple trailing slashes. Ancestor tests verify `mkdirs()` populates all nonexistent ancestors and does not remove existing parent directories during repeated nested calls. The final test confirms `mkdirs()` is idempotent on an existing directory.

State and persistence behavior: tests create directories and small files under contract paths and verify directory hierarchy preservation after creation calls. File-content validation ensures failed `mkdirs()` does not corrupt existing file data.

Dependencies and integration points: behavior is checked through direct `FileSystem.mkdirs()` and through `ContractTestUtils.assertMkdirs()`. The tests depend on `Path` normalization for trailing slash handling.

Risks: filesystems with object-store marker behavior may simulate directories lazily, so ancestor existence and listing semantics must be coherent. Some implementations may return false rather than throw on file collisions, which this contract treats as failure.

Test signals: pass indicates directory creation is idempotent, creates all ancestors, handles trailing slashes, rejects file collisions without corruption, and preserves parent directories across nested `mkdirs()` operations.
