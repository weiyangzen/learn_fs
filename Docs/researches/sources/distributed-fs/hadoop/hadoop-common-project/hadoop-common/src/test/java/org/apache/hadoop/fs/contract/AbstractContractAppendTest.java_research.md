# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractAppendTest.java

Purpose: generic contract tests for filesystems that advertise append support.

Important APIs/types/functions: `AbstractFSContractTestBase`, `SUPPORTS_APPEND`, `FSDataOutputStream`, `FileSystem.append`, `FileSystem.appendFile().build`, `ContractTestUtils.touch`, `createFile`, `dataset`, `readDataset`, `validateFileContent`, `rename`, and path capability `CommonPathCapabilities.FS_APPEND`.

Control flow/state/persistence: setup skips if append unsupported and prepares `test/target`. Tests append to empty files through classic and builder APIs, expect append to nonexistent/missing targets to fail through `handleExpectedException`, append data to existing files and validate concatenated bytes, rename a file while an append stream is open and verify bytes follow the open file handle to the renamed destination, and assert the filesystem declares append capability.

Dependencies/integration points: applies to many filesystem implementations through contract inheritance. Handles delayed create visibility for eventually consistent filesystems by sleeping before write when configured.

Risks/test signals: catches false append support declarations, append builder regressions, incorrect open-stream rename semantics, data concatenation errors, and wrong exception behavior for missing files.
