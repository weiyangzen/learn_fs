# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/performance/ITestS3AMkdirCost.java

Purpose: integration cost tests for `S3AFileSystem.mkdirs`, documenting expected HEAD/LIST behavior for existing dirs, child/grandchild creation, sibling creation, and mkdir over file failures.

Important APIs/types/functions: `ITestS3AMkdirCost` extends `AbstractS3ACostTest`; it uses `verifyMetrics`, `verifyMetricsIntercepting`, `dir`, `touch`, and metrics `OBJECT_METADATA_REQUESTS` and `OBJECT_LIST_REQUEST` with `OperationCost` constants `FILESTATUS_*`.

Control flow: tests create a base marker directory, run `mkdirs` over it, then create child or grandchild paths and assert the sequence of file and directory probes. After a grandchild exists, sibling creation is asserted to cost less because the immediate parent can be found by listing. The over-file test touches a file and expects `FileAlreadyExistsException`.

State and persistence: real S3 directory markers and file objects are created in the test bucket; no custom teardown beyond base class is defined.

Dependencies/integration: S3A mkdir implementation, directory marker lookup, file status probing, and cost helper infrastructure.

Risks: exact request counts are coupled to current mkdir status-probe order; marker retention policy or parent discovery changes will break assertions.

Test signals: exact HEAD/LIST metric diffs and expected failure when a target path is already a file.
