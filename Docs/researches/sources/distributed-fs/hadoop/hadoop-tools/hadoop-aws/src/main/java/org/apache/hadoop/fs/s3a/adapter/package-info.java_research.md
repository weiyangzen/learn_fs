# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/package-info.java

## Purpose
This package descriptor documents the adapter package as the only permitted place for AWS SDK v1 credential-provider classes in S3A.

## Important APIs and control flow
There is no executable code. The package is marked `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`. The documentation states that instantiation must use reflection or be prepared for missing v1 SDK classes.

## State, dependencies, and integration
The package depends only on Hadoop audience/stability annotations. It integrates by setting architectural boundaries for `AwsV1BindingSupport` and `V1ToV2AwsCredentialProviderAdapter`.

## Risks and test signals
The risk is architectural leakage: new code importing v1 SDK classes outside this package would break deployments without the v1 SDK. Static analysis or dependency checks should enforce this boundary.
