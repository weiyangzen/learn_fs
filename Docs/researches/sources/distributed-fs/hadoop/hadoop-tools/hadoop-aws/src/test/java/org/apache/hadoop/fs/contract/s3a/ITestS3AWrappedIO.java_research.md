# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AWrappedIO.java

Purpose: validates S3A through Hadoop's wrapped IO operation helpers.

Important APIs/types/functions: extends `org.apache.hadoop.io.wrappedio.impl.TestWrappedIO`; returns `S3AContract`.

Control flow: all wrapped operation tests are inherited.

State and persistence: inherited tests create/read/delete S3 test paths.

Dependencies and integration: wrapped IO implementation layer and S3A contract.

Risks: local class has no S3A-specific assertions; failures indicate wrapped IO and S3A contract mismatch.

Test signals: integration coverage for generic wrapped IO APIs over S3A.
