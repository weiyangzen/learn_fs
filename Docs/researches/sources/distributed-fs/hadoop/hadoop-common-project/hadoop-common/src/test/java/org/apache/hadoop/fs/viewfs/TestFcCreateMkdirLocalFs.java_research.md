# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/viewfs/TestFcCreateMkdirLocalFs.java

Purpose: Runs the generic `FileContextCreateMkdirBaseTest` suite against a local viewfs `FileContext`.

Important APIs/types/functions: `FileContextCreateMkdirBaseTest`, `ViewFsTestSetup.setupForViewFsLocalFs`, `ViewFsTestSetup.tearDownForViewFsLocalFs`, overridden `setUp` and `tearDown`.

Control flow: `setUp` assigns inherited `fc` to a viewfs-local `FileContext` and then invokes base setup. `tearDown` invokes base cleanup and removes viewfs local setup.

State/persistence: Local filesystem mount/test state is managed by `ViewFsTestSetup` and the inherited `fileContextTestHelper`.

Dependencies/integration: Validates viewfs `FileContext` behavior for create and mkdir semantics through a reusable base test suite.

Risks: No direct assertions in this class; all behavioral coverage is inherited. Setup/teardown ordering is important because the base class expects `fc` to be initialized before `super.setUp`.

Test signals: Inherited create/mkdir tests run using the viewfs local context.
