# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/CredentialInitializationException.java

Purpose: non-retryable AWS SDK client exception for credential setup failures.

Important APIs/types: extends `SdkClientException`; constructors accept message with optional cause using SDK builders; overrides `retryable()` to `false`.

Control flow: credential providers throw this when configuration is invalid or initialization cannot succeed. `AWSCredentialProviderList` and S3A exception translation treat it specially and map it to access denied.

State and persistence behavior: standard exception message/cause only.

Dependencies and integration points: public/stable Hadoop API for S3A credential providers. Integrates with AWS SDK retry metadata and Hadoop `AccessDeniedException` translation.

Risks: using this for transient credential-service outages would suppress retries. It should be reserved for deterministic setup failures.

Test signals: credential-provider tests should verify fail-fast retryability and translation to access denied.
