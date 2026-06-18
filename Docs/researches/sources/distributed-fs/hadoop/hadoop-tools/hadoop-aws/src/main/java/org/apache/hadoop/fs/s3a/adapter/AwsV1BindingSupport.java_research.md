# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/AwsV1BindingSupport.java

## Purpose
`AwsV1BindingSupport` isolates optional AWS SDK v1 credential-provider support. It is the sanctioned entry point for code that may need to instantiate v1 providers in an otherwise SDK v2 based S3A module.

## Important APIs and control flow
At class load, `SDK_V1_FOUND` is computed by attempting to load `com.amazonaws.auth.AWSCredentialsProvider` with this class loader. `isAwsV1SdkAvailable()` returns that cached probe result. `createAWSV1CredentialProvider()` rejects immediately with `InstantiationIOException.unavailable()` if v1 classes are missing; otherwise it delegates to `V1ToV2AwsCredentialProviderAdapter.create()`.

## State, dependencies, and integration
State is a static availability boolean. Dependencies include Hadoop `Configuration`, nullable filesystem URI, `InstantiationIOException`, and the adapter class. It is used by `CredentialProviderListFactory` after v2 reflection fails or when explicit v1 mappings require adaptation.

## Risks and test signals
Because availability is cached, classpath changes after class loading are not observed. Tests should cover v1 SDK absent/present behavior, exception kind on absence, and that callers never directly reference v1 classes outside the adapter package.
