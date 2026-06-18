# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractDeleteTest.java

Purpose: `AbstractContractDeleteTest` validates delete semantics for files, empty directories, non-empty directories, deep paths, and nonexistent paths.

Important APIs and types: it uses Hadoop `Path`, `FileSystem.delete(Path, boolean)`, `ContractTestUtils.writeTextFile`, and assertion helpers from `AbstractFSContractTestBase` such as `assertDeleted`, `assertPathDoesNotExist`, `assertPathExists`, and `assertIsDirectory`.

Control flow: tests first construct filesystem state, then call delete with recursive or non-recursive flags. Empty directories must delete with either flag. Missing paths must return false for both recursive and non-recursive delete after `rejectRootOperation()` validates the path is not root. Non-empty directory non-recursive delete is expected to raise `IOException`; recursive delete must remove the directory and child. Deep-directory deletion removes the requested subtree while preserving its parent. File deletion removes a single file.

State and persistence behavior: all filesystem mutations are under contract-generated paths. The tests persist small text files to make directories non-empty and then verify post-delete namespace shape.

Dependencies and integration points: root operation rejection is delegated to `ContractTestUtils.rejectRootOperation()` to guard against accidental destructive tests. Expected exception processing is delegated to `handleExpectedException()`.

Risks: the tests require missing delete to return false rather than throw, which is Hadoop contract behavior but may need adapter logic for foreign stores. Non-recursive deletion of non-empty directories accepts only `IOException`, so implementations returning false may fail even if they preserve data.

Test signals: pass indicates delete returns correct booleans for nonexistent paths, enforces recursive requirements for non-empty directories, removes files and target subtrees, and does not delete ancestors unexpectedly.
