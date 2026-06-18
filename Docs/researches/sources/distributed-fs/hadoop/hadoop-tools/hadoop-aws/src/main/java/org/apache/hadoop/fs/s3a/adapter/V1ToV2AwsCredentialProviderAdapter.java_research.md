# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/adapter/V1ToV2AwsCredentialProviderAdapter.java

## Purpose
This adapter wraps a v1 `com.amazonaws.auth.AWSCredentialsProvider` and exposes it as an AWS SDK v2 `AwsCredentialsProvider`, allowing legacy provider classes to be used by S3A during the SDK v2 migration.

## Important APIs and control flow
`resolveCredentials()` calls the wrapped v1 provider, converts v1 credentials to v2 credentials, and wraps v1 `SdkClientException` in Hadoop's `CredentialInitializationException`. `convertToV2Credentials()` maps session credentials to `AwsSessionCredentials`, anonymous credentials to v2 anonymous credentials, and other credentials to `AwsBasicCredentials`. `close()` propagates to `Closeable` or `AutoCloseable` providers. Static `create(conf, className, uri)` uses `S3AUtils.getInstanceFromReflection()` with constructors or `getInstance`.

## State, dependencies, and integration
The sole state is the wrapped v1 provider. The class depends on AWS SDK v1 and v2 auth APIs, `S3AUtils`, and `InstantiationIOException`. It is package-local behind `AwsV1BindingSupport` and used by credential-provider list construction.

## Risks and test signals
Credential conversion must preserve session tokens and anonymous semantics. Reflection errors need to retain the correct instantiation kind so v2/v1 fallback messages are accurate. Tests should cover conversion for basic, session, and anonymous credentials, close propagation, v1 exception wrapping, and reflection constructor precedence.
