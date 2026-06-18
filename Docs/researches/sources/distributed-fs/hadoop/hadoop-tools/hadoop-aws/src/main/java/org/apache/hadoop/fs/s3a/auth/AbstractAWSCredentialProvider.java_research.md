# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractAWSCredentialProvider.java

## Purpose
`AbstractAWSCredentialProvider` is a base class for S3A credential providers that need the filesystem URI and Hadoop configuration in their constructor.

## Important APIs and control flow
The constructor stores nullable `URI` and `Configuration`. `getConf()` and `getUri()` expose them. The class implements AWS SDK v2 `AwsCredentialsProvider` but leaves `resolveCredentials()` to subclasses.

## State, dependencies, and integration
State is immutable URI/configuration references. Subclasses include profile and session credential providers. It integrates with `S3AUtils.getInstanceFromReflection()` constructor selection used by credential-provider factories.

## Risks and test signals
The configuration is stored by reference, not copied, so later mutations can be visible to subclasses. Tests should verify reflection can instantiate URI+Configuration providers and that null URIs are tolerated when documented.
