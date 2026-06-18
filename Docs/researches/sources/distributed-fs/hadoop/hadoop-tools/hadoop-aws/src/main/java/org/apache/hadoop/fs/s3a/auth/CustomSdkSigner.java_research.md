# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CustomSdkSigner.java

## Purpose
`CustomSdkSigner` is a test-support AWS SDK signer used to validate S3A custom signer configuration and special service signing behavior.

## Important APIs and control flow
The constructor increments an instantiation counter. `sign()` increments an invocation counter, parses the host, and delegates to `Aws4Signer` for KMS hosts or `AwsS3V4Signer` for S3 hosts. `parseBucketFromHost()` extracts the bucket-like prefix and rebuilds S3 access point/outposts/object-lambda hosts into an ARN form. Static getters expose counters and `description()`. Nested `Initializer` implements `AwsSignerInitializer` with debug logging for register/unregister.

## State, dependencies, and integration
State includes static counters and per-instance S3/AWS4 signer delegates. Dependencies include AWS SDK signers, ARN builder, execution attributes, Hadoop configuration, delegation-token provider, and UGI. It integrates with `fs.s3a.custom.signers` and signing algorithm configuration.

## Risks and test signals
`parseBucketFromHost()` assumes dotted host structure and does not support path-style access, so malformed hosts can fail. Tests should cover S3, KMS, access point/outposts/object-lambda hosts, counter increments, initializer calls, and client-side encryption/KMS signing.
