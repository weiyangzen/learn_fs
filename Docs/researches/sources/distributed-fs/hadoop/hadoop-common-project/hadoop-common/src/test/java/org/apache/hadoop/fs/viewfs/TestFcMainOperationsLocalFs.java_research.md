# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestFcMainOperationsLocalFs.java

Purpose: Runs the generic `FileContextMainOperationsBaseTest` suite against a local viewfs `FileContext`.

Important APIs/types/functions: `FileContextMainOperationsBaseTest`, `ViewFsTestSetup.setupForViewFsLocalFs`, `ViewFsTestSetup.tearDownForViewFsLocalFs`, `listCorruptedBlocksSupported`.

Control flow: `setUp` initializes inherited `fc` with a viewfs-local context and then calls base setup. `tearDown` calls base cleanup and viewfs cleanup. The override `listCorruptedBlocksSupported` returns `false`, disabling inherited expectations not supported by local viewfs.

State/persistence: Local FS/viewfs test state is managed by helpers. Fields `fclocal` and `targetOfTests` are declared but unused in this class.

Dependencies/integration: Bridges the broad FileContext main-operations contract to viewfs local mounts.

Risks: Behavioral coverage is inherited, so local failures require tracing into the base class. Unsupported corrupted-block listing is explicitly documented by the override.

Test signals: Inherited FileContext main operation assertions, with corrupted-block listing disabled.
