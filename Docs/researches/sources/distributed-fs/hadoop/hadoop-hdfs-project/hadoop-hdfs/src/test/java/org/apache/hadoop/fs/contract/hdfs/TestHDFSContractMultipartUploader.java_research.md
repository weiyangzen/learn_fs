<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMultipartUploader.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMultipartUploader.java

Purpose: Adapts multipart uploader contract tests to HDFS with HDFS-specific capability overrides.
Important APIs/types/functions: `TestHDFSContractMultipartUploader` extends `AbstractContractMultipartUploaderTest`; overrides `partSizeInBytes()`, `finalizeConsumesUploadIdImmediately()`, and `supportsConcurrentUploadsToSamePath()`.
Control flow: Cluster setup/teardown wraps inherited multipart upload tests. The class reports 1KB part size, immediate upload-id consumption on finalize, and concurrent uploads to the same path as supported.
State and persistence behavior: State includes multipart upload session metadata and the static HDFSContract cluster.
Dependencies and integration points: Integrates HDFS multipart upload implementation with generic contract coverage.
Risks and edge cases: Incorrect capability overrides would make inherited tests assert the wrong semantics. Concurrent upload support is explicitly advertised and should stay true only if HDFS behavior supports it.
Test signals: Signals are inherited multipart upload completion, abort, conflict, and concurrent-upload tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/contract/hdfs/TestHDFSContractMultipartUploader.java -->
