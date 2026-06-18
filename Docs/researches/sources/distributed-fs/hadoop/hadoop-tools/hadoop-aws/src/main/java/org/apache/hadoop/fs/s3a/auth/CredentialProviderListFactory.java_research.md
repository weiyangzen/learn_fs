# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/CredentialProviderListFactory.java

## Purpose
`CredentialProviderListFactory` constructs ordered S3A AWS credential-provider lists from configuration, default providers, explicit class mappings, and legacy v1-to-v2 mappings.

## Important APIs and control flow
`createAWSCredentialProviderList()` builds the standard chain: environment variables, `IAMInstanceCredentialsProvider`, simple credentials, and temporary credentials. `buildAWSProviderList()` loads configured class names or defaults, applies built-in v1 mappings and user-defined `AWS_CREDENTIALS_PROVIDER_MAPPING`, rejects forbidden class names after mapping, and tries to instantiate v2 providers by reflection. If v2 instantiation fails because the class is not a v2 provider and the v1 SDK is present, it attempts v1 instantiation through `AwsV1BindingSupport`; otherwise it rethrows. `loadAWSProviderClasses()` returns defaults when the configuration key is empty.

## State, dependencies, and integration
State is static maps and logging helpers. Dependencies include AWS SDK v2 credential providers, S3A credential-list classes, `S3AUtils`, `InstantiationIOException`, `AwsV1BindingSupport`, and Hadoop configuration. It integrates with filesystem initialization and assumed-role provider construction.

## Risks and test signals
Provider ordering is security-sensitive and behavior-sensitive. V1 fallback must distinguish "not implementation" from real construction errors. Tests should cover default chain, explicit empty/configured lists, user mappings, built-in v1 mappings, forbidden providers, v1 SDK absent/present fallback, and close behavior of the returned list.
