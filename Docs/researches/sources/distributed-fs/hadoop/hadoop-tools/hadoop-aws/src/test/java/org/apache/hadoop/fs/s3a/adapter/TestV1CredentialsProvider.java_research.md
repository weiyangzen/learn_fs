# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/adapter/TestV1CredentialsProvider.java

## Purpose

`TestV1CredentialsProvider.java` verifies S3A compatibility with legacy AWS SDK v1 credential-provider declarations while producing AWS SDK v2 credential providers for the modern client stack.

## Important APIs, Types, and Functions

The tests drive `CredentialProviderListFactory.createAWSCredentialProviderList()` with `AWS_CREDENTIALS_PROVIDER`. `testV1V2Mapping()` checks known v1 provider class-name aliases map to v2/provider equivalents. `testV1Wrapping()` verifies arbitrary v1 providers are wrapped by `V1ToV2AwsCredentialProviderAdapter`. Nested classes model v1 providers with default constructor, `Configuration` constructor, and failing static factory method.

## Control Flow

Configuration strings are built as comma-separated provider class names. The factory creates `AWSCredentialProviderList`, then `assertCredentialProviders()` walks provider instances in order and checks assignability.

## State and Persistence Behavior

State is limited to configuration and instantiated provider lists. No credentials are resolved from real external sources in these tests.

## Dependencies and Integration Points

This bridges `com.amazonaws.auth.AWSCredentialsProvider` from SDK v1 with `software.amazon.awssdk.auth.credentials.AwsCredentialsProvider` from SDK v2, including S3A aliases for anonymous, environment, and IAM/container credentials.

## Risks and Edge Cases

Compatibility risks are ordering changes, alias regressions, and recursive/fallback instantiation hiding a real provider construction error.

## Test Signals

Signals are ordered provider class checks and propagation of `InstantiationIOException` containing the simulated `ClassNotFoundException` text.
