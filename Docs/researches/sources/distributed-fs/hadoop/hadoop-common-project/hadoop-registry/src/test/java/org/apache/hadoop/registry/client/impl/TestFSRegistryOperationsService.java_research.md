# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-registry/src/test/java/org/apache/hadoop/registry/client/impl/TestFSRegistryOperationsService.java

Purpose: tests the filesystem-backed registry implementation using the local filesystem.

Important APIs and functions: class-level `FSRegistryOperationsService` and `FileSystem`; tests cover `mknode`, `bind`, `resolve`, `exists`, `delete`, and `list`. A private `createRecord()` builds simple `ServiceRecord` instances with YARN IDs.

Control flow: test setup creates a local `test` directory and teardown deletes it. Bind tests verify parent creation behavior, overwrite behavior, and `_record` file creation. Delete tests distinguish directory-only children from `_record` files and assert nonrecursive deletion failures.

State and persistence: persists test directories and `_record` files under local path `test`. The registry service itself is static, but the filesystem tree is reset around each test.

Dependencies and integration: integrates Hadoop `FileSystem`, registry service-record serialization, Hadoop path exceptions, and JUnit assertions.

Risks and test signals: provides useful parity checks for the non-ZooKeeper backend. It catches behavior around `_record` pseudo-files, but tests catch broad `IOException` in several places, so precise exception type regressions could slip through.
