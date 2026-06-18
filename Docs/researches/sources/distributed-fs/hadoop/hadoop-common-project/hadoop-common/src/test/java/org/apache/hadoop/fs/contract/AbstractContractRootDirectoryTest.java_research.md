# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractRootDirectoryTest.java

Purpose: `AbstractContractRootDirectoryTest` exercises dangerous operations against `/`, gated by `TEST_ROOT_TESTS_ENABLED`, and is annotated `@RootFilesystemTest` to signal that it should only be used on transient filesystems.

Important APIs and types: it uses `FileSystem`, `Path`, `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, AssertJ, `LambdaTestUtils.eventually`, and root-focused `ContractTestUtils` helpers such as `deleteChildren`, `listChildren`, `treeWalk`, `dumpStats`, and `assertDeleted`.

Control flow: `setup()` skips unless root tests are enabled. Tests create `/testmkdirdepth1`, attempt recursive and non-recursive deletion of an empty root, attempt non-recursive deletion of a non-empty root, attempt recursive deletion of a root containing a file, reject creating a file over root, list an emptied root, compare simple root listings across `listStatus`, `listLocatedStatus`, `listFiles`, and `listStatusIterator`, and compare recursive root `listFiles` with a tree walk.

State and persistence behavior: this class deliberately mutates root-level namespace state. Non-recursive empty-root cleanup uses retry logic to remove children and tolerate object-store listing lag before deleting root. Tests always assert root remains a directory and clean up created files in `finally` where applicable.

Dependencies and integration points: root behavior depends on filesystem-specific policy; some stores may allow recursive root delete to remove children while others preserve them. The class integrates with test tags to separate high-risk root tests from ordinary contract tests.

Risks: data-loss risk is explicit; this class must never run against a valuable filesystem. Object stores can expose stale children after deletion, hence `OBJECTSTORE_RETRY_TIMEOUT`. Root listing comparisons may be expensive or unstable on large shared roots.

Test signals: pass indicates root remains a directory after delete/create attempts, non-recursive deletion protects non-empty root, root listing APIs are mutually consistent, recursive file listings match tree walk, and root-level cleanup behaves according to contract expectations.
