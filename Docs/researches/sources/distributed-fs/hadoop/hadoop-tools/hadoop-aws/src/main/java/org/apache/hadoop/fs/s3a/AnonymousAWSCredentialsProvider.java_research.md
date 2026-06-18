# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AnonymousAWSCredentialsProvider.java

Purpose: Hadoop-configurable AWS SDK v2 credentials provider for unsigned anonymous S3 access.

Important APIs/types: implements `AwsCredentialsProvider`; public `NAME` constant preserves the configuration class name; `resolveCredentials()` delegates to `AnonymousCredentialsProvider.create().resolveCredentials()`; `toString()` returns the simple class name.

Control flow: S3A instantiates this provider from `fs.s3a.aws.credentials.provider`; when selected, AWS requests are unsigned.

State and persistence behavior: stateless; creates/delegates to an SDK anonymous provider on each resolution.

Dependencies and integration points: used by `AWSCredentialProviderList`, which explicitly treats this class as valid even without access/secret keys. Intended for public datasets.

Risks: unsafe for private buckets; accidental configuration can silently remove request signing and produce access-denied behavior or expose reliance on public access.

Test signals: credential-chain tests should verify anonymous credentials are accepted and class-name based configuration remains compatible.
