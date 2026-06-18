# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/TemporaryAWSCredentialsProvider.java

## Purpose
`TemporaryAWSCredentialsProvider` supplies AWS session credentials from S3A/Hadoop configuration. It is intended for credential chains where construction must not fail merely because credentials are absent.

## Important APIs, Types, and Functions
Public constants are `NAME` and `COMPONENT`. Constructors accept `Configuration` alone or `(URI, Configuration)`. The core override is `createCredentials(Configuration)`.

## Control Flow and State
The provider delegates common session-provider behavior to `AbstractSessionCredentialsProvider`. `createCredentials()` loads `MarshalledCredentials` from filesystem configuration, requires `SessionOnly`, raises `NoAwsCredentialsException` if session credentials are absent, and converts valid credentials to AWS SDK credentials.

## State and Persistence Behavior
State is inherited and represents loaded session credentials. Credentials are read from configuration/credential providers and kept in memory; there is no automatic remote refresh in this class.

## Dependencies and Integration Points
Dependencies include AWS SDK `AwsCredentials`, `AbstractSessionCredentialsProvider`, `MarshalledCredentialBinding`, `MarshalledCredentials`, `NoAuthWithAWSException`, and `NoAwsCredentialsException`. The class name is stable for `fs.s3a.aws.credentials.provider`.

## Risks and Test Signals
Risks include treating long-lived basic credentials as empty, missing/expired session token behavior, construction compatibility in provider chains, and URI-specific lookup precedence. Tests should verify session-only validation, empty/basic-only failure, conversion to AWS credentials, provider-chain behavior, and bucket-specific credential loading.
