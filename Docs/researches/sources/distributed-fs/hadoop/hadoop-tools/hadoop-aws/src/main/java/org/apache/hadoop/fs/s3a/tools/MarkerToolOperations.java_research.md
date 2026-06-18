<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperations.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperations.java

Purpose: narrow operations interface required by `MarkerTool`, decoupling the tool from the full S3A operation callback surface.

Important APIs/types/functions: `listObjects(Path,String)` returns a `RemoteIterator<S3AFileStatus>` including the key itself if found. `removeKeys(List<ObjectIdentifier>,boolean)` deletes S3 keys and can throw translated IO, AWS service, invalid request, or multi-delete exceptions. Retry annotations document mixed/translated retry behavior.

Control flow: `MarkerTool` calls `listObjects()` during scan and `removeKeys()` during purge.

State/persistence: interface only. Implementations may mutate remote S3 state on deletion.

Dependencies/integration: AWS SDK `ObjectIdentifier`, Hadoop `RemoteIterator`, S3A status/exception types, and retry annotations.

Risks/test signals: incorrect list semantics can miss root/path marker objects; delete behavior must reject root mistakes. Tests should mock this interface to drive marker scan and purge behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/tools/MarkerToolOperations.java -->
