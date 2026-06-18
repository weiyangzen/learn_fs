# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/auth/AbstractSessionCredentialsProvider.java

## Purpose
`AbstractSessionCredentialsProvider` is a lazy, caching base class for providers that create full or session AWS credentials from Hadoop configuration.

## Important APIs and control flow
`init()` is synchronized and one-shot: if not initialized, it calls subclass `createCredentials(Configuration)` through `Invoker.once()`, stores credentials or initialization exception, and marks initialized in `finally`. `resolveCredentials()` triggers initialization, unwraps AWS SDK exceptions when possible, wraps other IO failures in `CredentialInitializationException`, and rejects null credentials. `hasCredentials()` and `getInitializationException()` expose test state. The nested `NoCredentials` class returns null keys to mean no credentials offered.

## State, dependencies, and integration
State includes volatile credentials, an `AtomicBoolean initialized`, and volatile initialization exception. It depends on AWS SDK `AwsCredentials`, Hadoop retry utilities, and `CredentialInitializationException`. It is extended by `MarshalledCredentialProvider` and similar session providers.

## Risks and test signals
Initialization is marked attempted even when credential creation fails; subsequent calls rethrow stored failure rather than retrying. Tests should cover lazy init, failure caching, SDK exception unwrapping, null credential rejection, and concurrency.
