# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractUnbuffer.java

Purpose: binds generic unbuffer contract tests to S3A.

Important APIs/types/functions: extends `AbstractContractUnbufferTest`; returns `S3AContract`.

Control flow: inherited tests validate `FSDataInputStream.unbuffer()` behavior.

State and persistence: inherited tests create/read S3 objects.

Dependencies and integration: S3A contract and Hadoop stream unbuffer contract.

Risks: no local overrides; any S3A-specific stream cleanup semantics must be in the base contract or separate tests.

Test signals: integration coverage for S3A input stream unbuffer support.
