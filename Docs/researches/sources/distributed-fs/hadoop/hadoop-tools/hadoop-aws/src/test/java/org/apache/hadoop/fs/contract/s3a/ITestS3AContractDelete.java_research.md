# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractDelete.java

Purpose: binds Hadoop's generic delete contract suite to the S3A filesystem.

Important APIs/types/functions: extends `AbstractContractDeleteTest`; only overrides `createContract(Configuration)` to return `new S3AContract(conf)`.

Control flow: all delete scenarios are inherited from the contract framework.

State and persistence: inherited tests create and delete S3 objects under contract test paths.

Dependencies and integration: S3A contract binding and Hadoop contract-test framework.

Risks: because it has no local overrides, S3A-specific delete edge cases must be represented in the base contract or separate tests.

Test signals: integration coverage for standard Hadoop delete semantics on S3A.
