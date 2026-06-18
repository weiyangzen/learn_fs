# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAuthWithAWSException.java

## Purpose
`NoAuthWithAWSException` represents authentication failures that S3A retry policy should fail fast rather than repeatedly retrying credential acquisition.

## Important APIs and control flow
It extends `CredentialInitializationException` and provides message and message-plus-cause constructors. No additional behavior is added.

## State, dependencies, and integration
State is inherited exception message/cause. It is thrown by marshalled credential binding and extended by `NoAwsCredentialsException`.

## Risks and test signals
Retry policy behavior depends on this exception type. Tests should verify auth failures bypass unnecessary retries and translate into useful user-facing diagnostics.
