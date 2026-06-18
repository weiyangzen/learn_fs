<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperationsImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperationsImpl.java

Purpose: adapter from the broad S3A `OperationCallbacks` interface to the narrow `MarkerToolOperations` interface.

Important APIs/types/functions: constructor stores `OperationCallbacks`; `listObjects()` delegates to `operationCallbacks.listObjects()`; `removeKeys()` delegates to `operationCallbacks.removeKeys(keysToDelete, deleteFakeDir)`.

Control flow: created by S3A filesystem/tooling and used by `MarkerTool` for scan and cleanup operations.

State/persistence: holds callback reference only.

Dependencies/integration: `OperationCallbacks`, S3A status types, AWS service exceptions, and multi-object delete exceptions.

Risks/test signals: adapter is thin; tests should verify exact delegation and exception propagation, especially `deleteFakeDir` flag preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperationsImpl.java -->
