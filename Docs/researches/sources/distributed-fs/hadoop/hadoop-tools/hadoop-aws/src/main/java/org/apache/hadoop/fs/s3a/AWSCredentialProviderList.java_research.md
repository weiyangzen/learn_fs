# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/AWSCredentialProviderList.java

Purpose: S3A credential-provider chain with Hadoop-specific diagnostics, dynamic provider composition, anonymous-provider handling, and reference-counted close behavior.

Important APIs/types: implements `AwsCredentialsProvider` and `AutoCloseable`. Constructors accept empty, collection, or named varargs provider sets. Public methods include `setName`, `add`, `addAll`, deprecated no-op `refresh`, `resolveCredentials`, `getProviders`, `checkNotEmpty`, `listProviderNames`, `share`, `getRefCount`, `isClosed`, `close`, `size`, and static `maybeTranslateCredentialException`.

Control flow: `resolveCredentials()` rejects closed or empty lists, optionally reuses `lastProvider`, then iterates providers. It accepts credentials with access and secret keys, or credentials from anonymous providers. `NoAwsCredentialsException` is logged without stack and only captured as last exception when no stronger exception exists; other `SdkException` instances replace the last exception; non-SDK exceptions are wrapped as `SdkException` when they have messages. If no provider succeeds, `CredentialInitializationException` is rethrown, otherwise a `NoAuthWithAWSException` is raised with provider diagnostics.

State and persistence behavior: mutable in-memory provider list, optional cached `lastProvider`, `reuseLastProvider`, `name`, atomic `refCount`, and atomic `closed`. `share()` increments references; `close()` decrements and only closes nested `Closeable`/`AutoCloseable` providers when the count reaches zero. No persistent storage is written, but nested providers may manage background refresh threads.

Dependencies and integration points: integrates with S3A credential provider configuration, Hadoop auth exceptions, AWS SDK v2 providers, anonymous credentials, `S3AUtils.closeAutocloseables`, and exception translation to `AccessDeniedException`.

Risks: provider list mutation is not generally synchronized except around share/close; concurrent add/resolve patterns would be unsafe. Reusing `lastProvider` can keep using a provider whose credentials later fail until that provider itself throws. Closing while shared incorrectly can leak background resources or close providers still in use.

Test signals: tests should cover empty-list failure, anonymous credentials acceptance, exception prioritization, cached-provider reuse, reference-counted close, closed-list failure, and translation of credential initialization errors to access denied.
