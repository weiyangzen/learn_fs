# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/audit/AuditFailureException.java

## Purpose
`AuditFailureException` is the base runtime/auth exception used when audit code fails or rejects a request.

## Important APIs and control flow
It extends `CredentialInitializationException`, with constructors for message and message plus cause. This places audit failures in an exception tree recognized by S3A exception translation.

## State, dependencies, and integration
State is inherited exception message/cause. It is thrown by audit spans and translated by `AuditIntegration` into `AccessDeniedException` or `UnsupportedRequestException`.

## Risks and test signals
Because it subclasses a credential initialization exception, retry and translation behavior depends on that hierarchy. Tests should verify audit exceptions raised inside AWS SDK interceptors are detected and translated consistently.
