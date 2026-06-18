# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMkdirWithCreatePerf.java

Purpose: exercises mkdir behavior when S3A create/mkdir performance flags are enabled.

Important APIs/types/functions: extends `AbstractContractMkdirTest`; `createConfiguration()` disables FS caching and enables `"create,mkdir"` performance flags. `testMkdirOverParentFile()` asserts a child directory can be created under a path that is also a file in performance mode.

Control flow: the custom test creates a file at the method path, calls `fs.mkdirs(path/child-to-mkdir)`, verifies the parent file remains intact, validates child existence, then deletes the child.

State and persistence: writes one file and one child directory marker/object under the method path.

Dependencies and integration: uses `KEY_PERFORMANCE_TESTS_ENABLED`, `ContractTestUtils`, and S3A performance flags.

Risks: behavior intentionally violates strict hierarchical expectations; useful only when performance flags are enabled.

Test signals: integration coverage for performance-mode mkdir over file-prefix cases.
