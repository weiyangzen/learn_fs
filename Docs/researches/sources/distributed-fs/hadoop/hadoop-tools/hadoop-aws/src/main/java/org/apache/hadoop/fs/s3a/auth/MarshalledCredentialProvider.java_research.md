# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/MarshalledCredentialProvider.java

## Purpose
`MarshalledCredentialProvider` is an AWS credentials provider backed by a prebuilt `MarshalledCredentials` object, primarily for delegation-token bindings rather than direct user configuration.

## Important APIs and control flow
The constructor requires a component name, non-null filesystem URI, configuration, marshalled credentials, and required credential type. It extends `AbstractSessionCredentialsProvider`; `createCredentials()` converts the stored marshalled credentials through `MarshalledCredentialBinding.toAWSCredentials()`.

## State, dependencies, and integration
State includes the marshalled credentials, required type, and component name. It depends on `AbstractSessionCredentialsProvider`, `MarshalledCredentialBinding`, and S3A credential exceptions. It integrates with delegation token providers that need to expose token credentials to AWS SDK clients.

## Risks and test signals
The constructor deliberately rejects null URI to prevent accidental direct configuration misuse. Tests should cover full/session credential conversion, type mismatch errors, empty credential errors, lazy initialization inherited from the base class, and message component labeling.
