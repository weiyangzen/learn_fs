# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractConcatTest.java

Purpose: `AbstractContractConcatTest` validates the Hadoop `FileSystem.concat(Path target, Path[] sources)` contract for filesystems that declare `SUPPORTS_CONCAT`. It is an abstract JUnit 5 test class extending `AbstractFSContractTestBase`, intended to be subclassed by concrete filesystem contract suites.

Important APIs and types: the class uses `Path`, `FileSystem.concat`, `CommonPathCapabilities.FS_CONCAT`, `ContractTestUtils.createFile`, `touch`, `dataset`, `assertFileHasLength`, `validateFileContent`, `readDataset`, and `LambdaTestUtils.intercept`. The test state is four paths prepared in `setup()`: `testPath`, `srcFile`, `zeroByteFile`, and `target`.

Control flow: `setup()` calls `super.setup()`, skips if concat is unsupported, builds a test directory, writes `srcFile` with `TEST_FILE_LEN` bytes, and creates an empty source. The tests then exercise invalid empty-source concat, missing target concat, valid file-on-file concat, self-concat rejection, and path-capability declaration. The valid concat case creates a target with the same dataset, concatenates `srcFile`, expects doubled length, and validates byte ordering as target block followed by source block.

State and persistence behavior: concat mutates the target file and should consume or move source data according to filesystem implementation semantics, but the test only asserts final target contents and length. It relies on the contract test base for test path isolation and cleanup.

Dependencies and integration points: this file integrates optional contract flags (`SUPPORTS_CONCAT`) with runtime capability probing (`FS_CONCAT`). It depends on relaxed exception handling in `AbstractFSContractTestBase.handleExpectedException()` so stores can normalize acceptable error behavior.

Risks: the test only validates one non-empty source and one zero-byte source in error cases; it does not assert whether source paths remain after concat. Filesystems with eventual consistency may need stronger post-concat stabilization in subclasses.

Test signals: pass means concat rejects empty source arrays, missing targets, and self-concat, preserves byte order for a simple append-style concat, and truthfully advertises `fs.concat` path capability.
