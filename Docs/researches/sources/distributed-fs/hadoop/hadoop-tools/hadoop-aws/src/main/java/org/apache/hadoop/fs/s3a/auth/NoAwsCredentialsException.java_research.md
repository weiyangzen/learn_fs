# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/NoAwsCredentialsException.java

## Purpose
`NoAwsCredentialsException` is a specific no-credentials-found exception that subclasses `NoAuthWithAWSException` for retry and diagnostic handling.

## Important APIs and control flow
Constructors combine the credential provider name with a supplied or default message and optional cause. The default message constant is `No AWS Credentials`.

## State, dependencies, and integration
State is inherited exception data. It is thrown by IAM metadata credential resolution and marshalled credential conversion when no usable credentials are present.

## Risks and test signals
Provider names are part of the message, so tests should assert diagnostics identify the failing provider. Retry tests should ensure this exception is treated as non-recoverable.
