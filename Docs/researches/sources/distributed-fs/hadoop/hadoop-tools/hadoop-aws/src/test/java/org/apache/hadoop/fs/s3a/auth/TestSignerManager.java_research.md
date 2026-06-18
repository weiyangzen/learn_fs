<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestSignerManager.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestSignerManager.java

## Purpose

`TestSignerManager` is a unit test suite for S3A custom signer registration, signer instantiation, signer initializer lifecycle, per-store signer state lookup, and rejection of unsupported signer names. It exercises the interaction between `SignerManager`, `SignerFactory`, Hadoop `Configuration`, `UserGroupInformation`, custom AWS SDK v2 `Signer` implementations, and S3A delegation-token providers.

## Important APIs, Types, and Functions

- `testPredefinedSignerInitialization()` configures `fs.s3a.custom.signers` with a built-in signer name and verifies initialization does not throw.
- `testCustomSignerFailureIfNotRegistered()` initializes an unregistered custom signer name and verifies `SignerFactory.createSigner()` fails with `InstantiationIOException`.
- `testCustomSignerInitialization()` and `testMultipleCustomSignerInitialization()` register custom signer classes and verify `SignerFactory` returns working signer instances, including Hadoop `Configurable` injection for `SignerForTest1`.
- `testSimpleSignerInitializer()` and `testMultipleSignerInitializers()` validate `AwsSignerInitializer.registerStore()` and `unregisterStore()` call counts.
- `testSignerInitializerMultipleInstances()` simulates three S3A stores across two buckets and two UGIs, then verifies signer lookup is isolated by `(bucket, UGI)` and cleaned up on close.
- `testV2SignerRejected()` and `testUnknownSignerRejected()` assert signer factory rejection paths.
- Nested helpers include `SignerForTest1`, `SignerForTest2`, `SignerInitializerForTest`, `SignerInitializer2ForTest`, `SignerForInitializerTest`, and `DelegationTokenProviderForTest`.

## Control Flow and State

Each test starts from `beforeTest()`, which resets static signer and initializer state. Custom signer config strings are composed as `name:signerClass` or `name:signerClass:initializerClass`, then passed to `SignerManager.initCustomSigners()`. Creation is simulated through `SignerFactory.createSigner()` and request signing through AWS SDK `Signer.sign()`.

The multi-instance test uses `fakeS3AInstanceCreation()` to build a config, token provider, and `SignerManager` for a bucket and UGI. `SignerInitializerForTest.registerStore()` stores a `StoreValue` in a static `HashMap<StoreKey, StoreValue>`, keyed by bucket and UGI. `SignerForInitializerTest.sign()` extracts the bucket from the request host and retrieves the store value for the current UGI. Closing each `SignerManager` removes that store entry.

## State and Persistence Behavior

All state is in-memory test state: static counters, static booleans, and `SignerInitializerForTest.storeCache`. No filesystem or external service persistence is used. Token identifiers are byte arrays embedded in Hadoop `Token` objects to prove delegation token provider propagation.

## Dependencies and Integration Points

The suite integrates Hadoop S3A `CUSTOM_SIGNERS`, `SignerManager`, `SignerFactory`, `AwsSignerInitializer`, `DelegationTokenProvider`, Hadoop UGI, and AWS SDK v2 signer/request APIs. It uses AssertJ and `LambdaTestUtils.intercept()` for assertions.

## Risks and Edge Cases

Important risks covered are malformed or stale signer registrations, forgotten unregister calls, shared static state leaking across stores, UGI-sensitive signer lookup returning another user or bucket's state, and accidental acceptance of removed S3 V2 or unknown signer identifiers. The host parsing in `SignerForInitializerTest` is test-specific and assumes hosts like `s3://bucket/`.

## Test Signals

The file itself is the test signal: counter assertions prove initializer construction/register/unregister behavior, signer `initialized` booleans prove signer invocation, cache-size assertions prove cleanup, and exception intercepts prove unsupported signer paths fail with meaningful `InstantiationIOException`s.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/TestSignerManager.java -->
