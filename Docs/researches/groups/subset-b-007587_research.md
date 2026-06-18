# subset-b-007587 Research

Grouped research for the S3A signer, delegation-token, Kerberos fixture, and committer integration test files listed in work item `subset-b-007587`.

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/AbstractDelegationIT.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/AbstractDelegationIT.java

## Purpose

`AbstractDelegationIT` is the shared base class for S3A delegation-token integration tests. It centralizes token lookup, token creation, delegated filesystem instantiation, provider-list binding, delegation-token binding configuration, UGI reset, and token-file persistence.

## Important APIs, Types, and Functions

- `lookupToken(Credentials, URI, Text)` finds the S3A token for a URI through `S3ADelegationTokens.lookupS3ADelegationToken()`, asserts token kind, decodes the identifier, and logs it.
- `mkTokens(S3AFileSystem)` calls `fs.addDelegationTokens(YARN_RM, cred)` and returns credentials populated with S3A tokens.
- `newS3AInstance(URI, Configuration)` constructs and initializes an uncached `S3AFileSystem`.
- `assertBoundToDT(S3AFileSystem, Text)` verifies an FS's `S3ADelegationTokens` is bound to a delegation token of the expected kind.
- `assertTokenCreationCount()` checks the delegation-token support creation counter.
- `enableDelegationTokens(Configuration, String)` clears base/bucket overrides and sets `DELEGATION_TOKEN_BINDING`.
- `bindProviderList()` removes bucket overrides for `AWS_CREDENTIALS_PROVIDER` and writes an explicit provider list.
- `saveDT(File, Token<?>)` persists a single token through Hadoop `Credentials.writeTokenStorageToStream()`.
- `instantiateDTSupport(Configuration)` creates `S3ADelegationTokens`, binds it to the test filesystem's URI/store context/delegation operations, and initializes it.

## Control Flow and State

Subclasses call `enableDelegationTokens()` from their configuration setup, then use `instantiateDTSupport()` or `mkTokens()` during tests. Token lookup starts from Hadoop `Credentials`, resolves the S3A service token for a URI, checks kind, and decodes an `AbstractS3ATokenIdentifier`.

## State and Persistence Behavior

The class writes token files only via `saveDT()`, wrapping the token into a temporary `Credentials` object. It also resets global UGI state with `UserGroupInformation.reset()`, which is important because Kerberos and credential caches are JVM-global test state.

## Dependencies and Integration Points

It depends on `AbstractS3ATestBase`, `S3AFileSystem`, `S3ADelegationTokens`, `DelegationConstants`, Hadoop `Credentials`, `Token`, UGI, and S3A test utilities for clearing bucket overrides. It is used by session, role, MR, and filesystem delegation tests.

## Risks and Edge Cases

The helpers assume the target S3A filesystem has delegation-token support configured and present. Failure to clear bucket overrides can mask the binding under test, so `enableDelegationTokens()` and `bindProviderList()` deliberately remove base/bucket-scoped values first. `instantiateDTSupport()` binds to the live test FS, so it requires superclass setup to have completed.

## Test Signals

The base class has no tests of its own; its signals are consumed by subclasses through token-kind assertions, decoded identifier validation, creation-count checks, and successful round-trip loading of persisted tokens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/AbstractDelegationIT.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/CountInvocationsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/CountInvocationsProvider.java

## Purpose

`CountInvocationsProvider` is a deliberately failing AWS credentials provider used by delegation-token tests to prove that delegated-token credential chains override ordinary configured providers. If it is invoked, it increments counters and throws, making unexpected fallback visible.

## Important APIs, Types, and Functions

- Implements AWS SDK v2 `AwsCredentialsProvider`.
- `NAME` exposes the provider class name for configuration strings.
- Static `COUNTER` tracks global invocations across all provider instances.
- `instanceCounter` tracks invocations per instance.
- `resolveCredentials()` increments both counters, logs a message, and throws `CredentialInitializationException`.
- `getInvocationCount()` and `getInstanceCounter()` expose counters for assertions.

## Control Flow and State

Tests bind this provider into `fs.s3a.aws.credentials.provider`, then execute a delegated S3A operation. A successful delegation path should never call `resolveCredentials()`, leaving the global counter unchanged. If S3A incorrectly falls back to normal credentials, the provider throws and the test fails.

## State and Persistence Behavior

State is purely in-memory through `AtomicLong` counters. The static counter persists across provider instances in the same JVM and can therefore be used to compare before/after counts in a test.

## Dependencies and Integration Points

It integrates with S3A's AWS credentials provider loading and AWS SDK v2 credential interface. It is referenced by `ITestSessionDelegationInFilesystem` through `CountInvocationsProvider.NAME`.

## Risks and Edge Cases

Because the global counter is static and not reset in this class, tests should compare deltas rather than assume zero. The provider never returns credentials by design.

## Test Signals

The signal is negative: an unchanged invocation count proves the delegated-token provider chain was selected; a thrown `CredentialInitializationException` or increased count points to incorrect credential fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/CountInvocationsProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/Csvout.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/Csvout.java

## Purpose

`Csvout` is a small test utility for writing delimited rows, used by delegation-token load tests to record timing outcomes. It is closer to TSV/CSV line writing than a full CSV implementation.

## Important APIs, Types, and Functions

- Constructor takes a `Writer`, field separator, and end-of-line string.
- `write(Object)` writes a single field, adding the separator unless at the start of a line.
- `write(Object...)` writes multiple fields in order.
- `newline()` writes the configured EOL and resets line-start state.
- `close()` closes the wrapped writer.

## Control Flow and State

The only internal state is `isStartOfLine`. It starts true, flips false after the first field, and resets true on `newline()`. `write(Object...)` loops through fields and delegates to `write(Object)`.

## State and Persistence Behavior

Persistence is delegated to the supplied `Writer`, typically a `FileWriter` in `ILoadTestSessionCredentials`. The class does not flush explicitly and does not own escaping or quoting policy.

## Dependencies and Integration Points

It uses only `java.io.Closeable`, `IOException`, and `Writer`. Load-test outcomes call it through a fluent `write(...).newline()` API.

## Risks and Edge Cases

It does not escape separators, EOLs, quotes, or null objects. Callers must pre-quote strings and avoid separator-containing fields. A null field would throw `NullPointerException` via `o.toString()`.

## Test Signals

There are no direct unit tests in this file. It is indirectly tested when load tests produce readable timing files with schema and rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/Csvout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestRoleCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestRoleCredentials.java

## Purpose

`ILoadTestRoleCredentials` reuses the session-credential STS load test with the role delegation-token binding. It measures the cost and throttling behavior of assume-role credential creation relative to plain session token creation.

## Important APIs, Types, and Functions

- Extends `ILoadTestSessionCredentials`.
- Annotated with `@LoadTest` and `@ScaleTest`.
- `getDelegationBinding()` returns `DELEGATION_TOKEN_ROLE_BINDING`.
- `getFilePrefix()` returns `role`, causing CSV files to use the role prefix.

## Control Flow and State

All execution flow is inherited from `ILoadTestSessionCredentials`: setup configures delegation tokens and an executor, tests call `fetchTokens()`, many concurrent calls invoke `fileSystem.getDelegationToken()`, and outcomes are written to CSV. This subclass changes only the binding and output filename prefix.

## State and Persistence Behavior

The inherited load test writes timing CSV files under the test data directory. It uses the same executor, completion service, and outcome aggregation as the session variant.

## Dependencies and Integration Points

It depends on role-token binding configuration and, in practice, on S3A test configuration that can assume a configured role. It is part of the high-cost load/scale test path rather than ordinary unit test execution.

## Risks and Edge Cases

Because role credentials require STS AssumeRole, this test can trigger AWS STS throttling and may affect a shared AWS account. It inherits the load-test warning profile from the parent.

## Test Signals

Signals are CSV rows and logged summary stats for total requests, successful requests, throttled requests, duration distributions, and effective operations per second.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestRoleCredentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestSessionCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestSessionCredentials.java

## Purpose

`ILoadTestSessionCredentials` is a load/scale test that creates many S3A delegation tokens backed by AWS STS session credentials to observe latency and throttling behavior. It is intentionally high impact and documented as potentially disruptive to a shared AWS account.

## Important APIs, Types, and Functions

- `createScaleConfiguration()` enables the configured delegation-token binding, increases S3A connection count to at least `THREADS`, and disables S3A error retries.
- `getDelegationBinding()` defaults to `DELEGATION_TOKEN_SESSION_BINDING`.
- `setup()` assumes session tests are enabled, verifies canonical service name, and creates a local data directory.
- `testCreate10Tokens()` fetches 10 tokens and logs CSV content.
- `testCreateManyTokens()` fetches 50,000 tokens.
- `fetchTokens(int, File)` submits token-fetch callables to a 100-thread executor and records outcomes.
- Nested `Outcome` records id, wall-clock start, nano timer, and optional exception, then writes rows and schema through `Csvout`.

## Control Flow and State

The test builds a fixed thread pool and `ExecutorCompletionService`. For each token request it submits a task that calls `fileSystem.getDelegationToken("Count ")`, captures any `IOException`, and returns an `Outcome`. The main thread consumes completed outcomes, writes each CSV row, and aggregates three `NanoTimerStats` groups: overall, successful, and throttled.

## State and Persistence Behavior

It writes CSV timing files named `session-<tokens>.csv` under `GenericTestUtils.getTestDir("kerberos")`. The executor is a field and is not explicitly shut down in the file, relying on test lifecycle/JVM handling. S3A remote state is limited to STS calls and token creation, not object writes.

## Dependencies and Integration Points

The test uses `S3AScaleTestBase`, `S3AFileSystem.getDelegationToken()`, delegation constants, Hadoop executor utilities, Guava `ThreadFactoryBuilder`, `NanoTimerStats`, Apache Commons IO for reading the short CSV, and live AWS STS behavior.

## Risks and Edge Cases

The documented risk is AWS STS throttling that can affect other users in the same AWS account. Disabling retries makes throttling visible but also makes the workload less resilient. CSV writing is simple and only externally quotes the exception message. Very large runs may be slow and generate large output files.

## Test Signals

Signals are per-request CSV rows containing success flag, start/end/duration, and error message; logged aggregate timer stats; throttled-event counts; and effective operations per second.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestSessionCredentials.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestDelegatedMRJob.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestDelegatedMRJob.java

## Purpose

`ITestDelegatedMRJob` verifies that MapReduce job submission collects S3A delegation tokens for all S3A resources used by a job: input path, output path, and an extra cache-file resource. It runs as a parameterized integration test across session, full-credentials, and role delegation-token bindings.

## Important APIs, Types, and Functions

- `params()` returns parameter tuples for session, full, and role token bindings and token kinds.
- `setupCluster()` starts `MiniKerberizedHadoopCluster`; `teardownCluster()` stops it.
- `createConfiguration()` patches YARN/Kerberos config, configures fast RM failure, sets an external ORC job resource, clears its bucket endpoint override, and enables the selected delegation-token binding.
- `setup()` logs into the cluster principal, probes role ARN when needed, sets UGI config/security, and starts `MiniMRYarnCluster`.
- `testCommonCrawlLookup()` checks the extra job resource exists and is encrypted.
- `testJobSubmissionCollectsTokens()` builds a `MockJob` WordCount job, adds S3 input/output/cache resources, submits it, and validates submitted credentials contain tokens for each filesystem URI.

## Control Flow and State

The class-level MiniKDC fixture is shared across parameterized runs. Each test logs in a principal, starts a one-node MiniMR YARN cluster, creates a mock MapReduce job, and submits it through a mocked client-side protocol. The job remains in `RUNNING` state under `MockJob`, but its submitted credentials are available for inspection. Teardown deletes destination output, terminates YARN, tears down the S3A test base, and closes user filesystems.

## State and Persistence Behavior

Persistent test effects are S3A output directories under `destPath` and local MiniKDC/YARN state. The credentials object is in-memory. Static `cluster` holds the Kerberos fixture across tests. Filesystem caching is disabled in class setup to avoid stale token state.

## Dependencies and Integration Points

This file integrates `MiniKerberizedHadoopCluster`, `MiniMRYarnCluster`, `MockJob`, MapReduce WordCount classes, `TokenCache`-style job resource token collection, public dataset utilities, role-test utilities, and S3A delegation-token bindings.

## Risks and Edge Cases

The test depends on live S3 paths, public dataset availability, Kerberos-secure UGI, and role ARN configuration for role mode. It explicitly uses an extra S3 cache resource to cover token extraction from localized resources, a historically fragile path in YARN resource localization.

## Test Signals

Success is signaled by `MockJob` submission with `RUNNING` status, credentials containing token kinds matching source/destination/extra-resource URIs, and encrypted metadata on the extra public ORC resource.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestDelegatedMRJob.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestRoleDelegationInFilesystem.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestRoleDelegationInFilesystem.java

## Purpose

`ITestRoleDelegationInFilesystem` reruns the session delegation-in-filesystem integration suite using role-based delegation tokens and adds role-specific permission validation.

## Important APIs, Types, and Functions

- Extends `ITestSessionDelegationInFilesystem`.
- `setup()` calls the parent setup and probes for an assumed-role ARN.
- `getDelegationBinding()` returns `DELEGATION_TOKEN_ROLE_BINDING`.
- `getTokenKind()` returns `ROLE_TOKEN_KIND`.
- `verifyRestrictedPermissions(S3AFileSystem)` expects `readExternalDatasetMetadata()` to fail with `AccessDeniedException`.

## Control Flow and State

The control flow is inherited from the session filesystem delegation tests: Kerberos users are created, a base FS issues a token, credentials are attached to the current UGI, and new delegated filesystems are opened without ordinary AWS secrets. This subclass changes token kind/binding and turns the external-dataset metadata probe into a negative permission assertion.

## State and Persistence Behavior

State mirrors the parent class: Kerberos users, UGI credentials, S3A delegated FS instances, and temporary token files in inherited tests. No additional state is introduced.

## Dependencies and Integration Points

It depends on role delegation binding, role ARN discovery through `RoleTestUtils.probeForAssumedRoleARN()`, and AWS access policy behavior that restricts delegated role credentials to the target bucket.

## Risks and Edge Cases

The key risk is environmental: the configured role policy must deny the external public dataset while allowing target-bucket operations. If the role is over-permissive, the negative test fails; if under-permissive, inherited filesystem operations fail.

## Test Signals

The primary role-specific signal is an intercepted `AccessDeniedException` when delegated role credentials are used against the external dataset. Inherited signals cover token binding, token reuse, encryption propagation, YARN/CLI token pickup, and MPU-safe filesystem operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestRoleDelegationInFilesystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestRoleDelegationTokens.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestRoleDelegationTokens.java

## Purpose

`ITestRoleDelegationTokens` reruns the session delegation-token suite with the role token binding, then verifies behavior unique to role tokens: session credentials do not propagate as new role tokens, role ARN is required only when creating a new token, and S3A can generate a role policy model.

## Important APIs, Types, and Functions

- Extends `ITestSessionDelegationTokens`.
- `getDelegationBinding()` returns `DELEGATION_TOKEN_ROLE_BINDING`; `getTokenKind()` returns `ROLE_TOKEN_KIND`.
- `setup()` calls parent setup and requires an assumed role ARN.
- `verifyCredentialPropagation()` intercepts `DelegationTokenIOException` with `E_NO_SESSION_TOKENS_FOR_ROLE_BINDING`.
- `testBindingWithoutARN()` starts `S3ADelegationTokens` without a role ARN and verifies token creation fails with `RoleTokenBinding.E_NO_ARN`.
- `testCreateRoleModel()` calls `S3AFileSystem.listAWSPolicyRules()` for read/write access and serializes the resulting `RoleModel.Policy` as JSON.

## Control Flow and State

The parent creates and starts delegation-token support, creates tokens, and tests save/load and credential propagation. This subclass overrides the propagation path to assert failure because role bindings cannot create role tokens from plain session credentials. It separately creates a second `S3ADelegationTokens` instance without ARN to prove initialization/start are allowed but token creation is not.

## State and Persistence Behavior

State is inherited from the session suite: an active `S3ADelegationTokens` instance per test, temporary token files, and live S3A FS configuration. `testBindingWithoutARN()` uses try-with-resources for a temporary token-support instance.

## Dependencies and Integration Points

It integrates role token binding, `RoleTokenBinding`, `MarshalledCredentials`, `S3ADelegationTokens`, `EncryptionSecrets`, `RoleModel`, and filesystem-generated IAM policy rules.

## Risks and Edge Cases

Role token tests are sensitive to missing or misconfigured role ARN and policy permissions. The distinction between starting a binding without ARN and creating a token without ARN is intentional and guards lazy validation behavior.

## Test Signals

Signals include expected `DelegationTokenIOException` for session-to-role propagation, expected `IllegalStateException` for missing ARN during token creation, non-empty policy rules, and inherited token-kind/save-load assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestRoleDelegationTokens.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestSessionDelegationInFilesystem.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestSessionDelegationInFilesystem.java

## Purpose

`ITestSessionDelegationInFilesystem` is a Kerberos-backed integration suite that verifies S3A delegation tokens are issued by a filesystem, stored in UGI credentials, picked up by newly initialized delegated filesystems, usable through Hadoop/YARN token utilities, and correctly reject binding mismatches. It focuses on session-token binding and is the base for role-token filesystem tests.

## Important APIs, Types, and Functions

- Class-level `setupCluster()` and `teardownCluster()` manage `MiniKerberizedHadoopCluster`.
- `createConfiguration()` enables Kerberos, disables FS caching and S3 Express create session, configures session delegation binding, removes credential/encryption overrides, optionally propagates encryption settings, and sets YARN RM principal.
- `setup()` resets UGI, creates Alice/Bob users, sets Alice as login user, initializes the S3A FS, verifies no token is already present, and instantiates delegation-token support.
- `testGetDTfromFileSystem()` verifies `getDelegationToken()` kind, service, and S3A metrics.
- `testAddTokensFromFileSystem()`, `testCanRetrieveTokenFromCurrentUserCreds()`, and `testDTCredentialProviderFromCurrentUserCreds()` verify token collection and UGI credential lookup.
- `testDelegatedFileSystem()` creates credentials from one FS, removes ordinary AWS secrets, binds a failing provider, opens new delegated FS instances, verifies DT binding, encryption propagation, restricted-permission behavior, filesystem operations, token reuse, and no fallback provider invocation.
- `testDelegationBindingMismatch1()` and `testDelegationBindingMismatch2()` assert meaningful failures when local and remote token bindings disagree.
- `readExternalDatasetMetadata()` creates an S3 client from delegated FS credentials and HEADs an external bucket.
- `testYarnCredentialPickup()`, `testHDFSFetchDTCommand()`, and `testDTUtilShell()` validate Hadoop token-cache, `hdfs fetchdt`, and `dtutil` integration.
- `testFileSystemBoundToCreator()` verifies token user identity is the FS creator, not the current `doAs` caller.

## Control Flow and State

Setup creates secure UGI state before the S3A filesystem is initialized, so the FS owner is Alice. Tests then issue tokens, add them to current-user credentials, remove all normal AWS credentials from a new configuration, and instantiate new S3A filesystems that must bind to the existing token. Delegated operations include directory checks, touch, delete, mkdir, rename, and cleanup. CLI tests write token files, print/renew/cancel them, and decode identifiers.

## State and Persistence Behavior

The suite manipulates JVM-global UGI state and closes all filesystems for Alice, Bob, and current user during teardown. It writes temporary token files under the MiniKDC work directory. S3A test paths are created and deleted in the target bucket. It uses static `cluster` state for the MiniKDC.

## Dependencies and Integration Points

The file integrates MiniKDC/Kerberos, Hadoop `DelegationTokenFetcher`, `DtUtilShell`, YARN `TokenCache`, S3A delegation-token support, S3A credential provider chains, S3A encryption settings, public dataset utilities, AWS SDK v2 `S3Client`, and S3A metrics/statistics.

## Risks and Edge Cases

Risks include global UGI contamination, filesystem caching hiding token changes, ordinary AWS credentials accidentally masking delegated-token behavior, encryption settings failing to propagate, S3 Express/session behavior requiring disabled create-session, and mismatched bindings producing hard-to-diagnose startup failures. The external-dataset HEAD is live AWS behavior and role subclasses invert its expected result.

## Test Signals

Signals include token-kind assertions, metric deltas for token invocation and issue counts, decoded token identity and encryption secrets, unchanged `CountInvocationsProvider` counter, successful delegated filesystem operations, expected `TOKEN_MISMATCH` failures, successful YARN/HDFS/dtutil token acquisition, and owner/user assertions for Alice and Bob.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestSessionDelegationInFilesystem.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestSessionDelegationTokens.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestSessionDelegationTokens.java

## Purpose

`ITestSessionDelegationTokens` verifies session delegation-token creation, serialization, decoding, credential conversion, propagation from temporary AWS session credentials, renewer preservation, and S3A delegation-token support startup behavior.

## Important APIs, Types, and Functions

- `getDelegationBinding()` returns `DELEGATION_TOKEN_SESSION_BINDING`; `getTokenKind()` returns `SESSION_TOKEN_KIND`.
- `createConfiguration()` enables the selected delegation binding.
- `setup()` assumes session tests are enabled, resets UGI, creates and starts `S3ADelegationTokens`.
- `testCanonicalization()` asserts the filesystem canonical URI and service name match.
- `testSaveLoadTokens()` creates a token with KMS encryption secrets, saves it, loads it through `Credentials.readTokenStorageFile()`, decodes and validates it, and compares identifier, origin, expiry, and encryption secrets.
- `testCreateAndUseDT()` creates a DT, binds a second token-support instance to it, validates AWS session credentials, round-trips marshalled credentials, checks user-agent UUID, and calls `verifyCredentialPropagation()`.
- `testCreateWithRenewer()` verifies the renewer is embedded in the decoded identifier.
- `verifyCredentialPropagation()` configures `TemporaryAWSCredentialsProvider`, writes marshalled session secrets into a config, starts new token support, creates/binds a token, resolves credentials, compares them to the original session, and verifies origin text.
- `testDBindingReentrancyLock()` verifies an unbound started token-support instance is not incorrectly marked bound.

## Control Flow and State

Tests instantiate token support against the live test S3A FS. Token creation returns a Hadoop `Token<AbstractS3ATokenIdentifier>` whose identifier is decoded to a `SessionTokenIdentifier`. Credential propagation uses a second `S3ADelegationTokens` instance and a new config seeded with temporary credentials, then asks for a bound-or-new DT and credential provider resolution.

## State and Persistence Behavior

The suite writes temporary token storage files and keeps a per-test `delegationTokens` service, closed in teardown. It resets UGI before and after each test to limit global credential contamination.

## Dependencies and Integration Points

It integrates S3A token identifiers, `EncryptionSecrets`, `MarshalledCredentials`, AWS SDK v2 session credentials, `TemporaryAWSCredentialsProvider`, Hadoop token storage, and S3A token service canonicalization.

## Risks and Edge Cases

Important edge cases are canonical service-name changes, loss of encryption secrets during token serialization, propagation accidentally using Hadoop credential providers, role-binding subclasses rejecting session-token propagation, and token support being marked bound when no token exists.

## Test Signals

Signals include decoded identifier validation, equality of original and loaded identifiers, matching expiry/origin/encryption fields, non-empty AWS session credential parts, matching marshalled credentials after propagation, user-agent UUID content, renewer equality, and unbound-state assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ITestSessionDelegationTokens.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/MiniKerberizedHadoopCluster.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/MiniKerberizedHadoopCluster.java

## Purpose

`MiniKerberizedHadoopCluster` is a reusable test fixture for Kerberos-secure Hadoop/YARN/MR integration tests. It creates a MiniKDC, keytab, test principals, SSL config, and configuration patches needed for secure HDFS and YARN services.

## Important APIs, Types, and Functions

- Extends Hadoop `CompositeService`.
- Constants include `ALICE`, `BOB`, `HTTP_LOCALHOST`, and platform-aware `LOCALHOST_NAME`.
- Constructor loads default HDFS/YARN/MR configs and optionally enables JVM Kerberos/SPNEGO debug flags.
- `serviceInit()` patches generic config, creates the work directory and `MiniKdc`, and records the Kerberos instance host.
- `serviceStart()` starts MiniKDC, creates principals for Alice, Bob, HTTP, and login user in one keytab, and sets up SSL config files through `KeyStoreTestUtil`.
- `patchConfigWithHDFSBindings()` enables Kerberos and configures HDFS secure principals, keytabs, HTTPS-only policy, block tokens, and data-transfer protection.
- `patchConfigWithYARNBindings()` enables Kerberos and configures RM/NM/JH principals, keytabs, hosts/ports, timeline disablement, and retry behavior.
- `createAliceUser()`, `createBobUser()`, `loginPrincipal()`, `loginUser()`, `resetUGI()`, `assertSecurityEnabled()`, and `closeUserFileSystems()` support test lifecycle.

## Control Flow and State

The service must be initialized and started before cluster-specific config patch methods are called; those methods use `Preconditions.checkState(STATE.STARTED)`. Starting creates principals and SSL resources. Tests then login users from the generated keytab and set UGI state before creating secure filesystems or MR/YARN services.

## State and Persistence Behavior

Persistent local state lives under `GenericTestUtils.getTestDir("kerberos")`: the MiniKDC work directory, `keytab.bin`, and SSL keystore config. JVM-global UGI state is intentionally resettable. The fixture stores principal names and SSL config filenames in fields.

## Dependencies and Integration Points

It integrates `MiniKdc`, UGI, HDFS/YARN/MR configuration constants, `KeyStoreTestUtil`, `KDiag`, `CompositeService`, local filesystem paths, and secure-service setup expected by S3A delegation-token tests.

## Risks and Edge Cases

Secure Hadoop miniclusters are sensitive to principal formats, hostnames, HTTPS-only settings, keytab paths, and native/security checks. The class explicitly notes that full secure Hadoop+YARN+MR setup is complicated and partly constrained by local FS permission behavior. Windows host handling uses `127.0.0.1` instead of `localhost`.

## Test Signals

The fixture's consumers signal success by creating Alice/Bob UGIs, asserting `UserGroupInformation.isSecurityEnabled()`, starting MiniMR/YARN or HDFS with patched configs, fetching delegation tokens under Kerberos, and closing per-user filesystems cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/MiniKerberizedHadoopCluster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/TestS3ADelegationTokenSupport.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/TestS3ADelegationTokenSupport.java

## Purpose

`TestS3ADelegationTokenSupport` is a unit test suite for S3A delegation-token identifier classes. It verifies token kinds, issue dates, encode/decode behavior, owner/renewer/authentication metadata, marshalled credentials, URI preservation, and encryption secret round trips.

## Important APIs, Types, and Functions

- `classSetup()` initializes `externalUri` from the public dataset default path.
- `testSessionTokenKind()` and `testFullTokenKind()` verify default identifier kinds.
- `testSessionTokenIssueDate()` verifies session identifiers have nonzero issue dates.
- `testSessionTokenDecode()` constructs a `SessionTokenIdentifier` with owner, renewer, URI, credentials, SSE-S3 encryption secrets, and origin; wraps it in a Hadoop `Token`; decodes it; and validates credentials, UGI identity, auth method, origin, issue date, and encryption secrets.
- `testSessionTokenIdentifierRoundTrip()`, `testSessionTokenIdentifierRoundTripNoRenewer()`, `testRoleTokenIdentifierRoundTrip()`, and `testFullTokenIdentifierRoundTrip()` serialize/deserialize identifiers and compare URI, credentials, renewer, and encryption fields.
- Nested `SessionSecretManager` supplies deterministic token password handling and identifier factory.

## Control Flow and State

Most tests construct token identifiers directly, then use either Hadoop `Token.decodeIdentifier()` or `S3ATestUtils.roundTrip()` to exercise Writable serialization. The decoded identifiers are validated and compared against original fields.

## State and Persistence Behavior

There is no filesystem or network persistence. Serialization is in-memory round trip. The static `externalUri` is initialized once.

## Dependencies and Integration Points

It depends on S3A token identifier types, `MarshalledCredentials`, `MarshalledCredentialBinding`, `EncryptionSecrets`, Hadoop `Token`, UGI, `SecretManager`, Apache Commons Base64, and public dataset test constants.

## Risks and Edge Cases

The suite covers empty/null renewer normalization, encryption context preservation, token authentication method assignment, default issue date generation, and consistency across session, role, and full-credential identifiers. It does not cover live STS or filesystem binding.

## Test Signals

Signals are direct equality assertions on token kind, issue date, URI, marshalled credentials, renewer, owner, auth method, origin, and encryption method/key/context, plus non-null AWS credentials conversion from marshalled credentials.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/TestS3ADelegationTokenSupport.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractCommitITest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractCommitITest.java

## Purpose

`AbstractCommitITest` is the shared base for S3A committer integration tests. It prepares committer-friendly S3A configuration, creates test helpers and report directories, manages multipart upload assertions, constructs MapReduce task contexts, and validates S3A `_SUCCESS` marker content and statistics.

## Important APIs, Types, and Functions

- `createConfiguration()` disables FS caching, clears committer/buffer overrides, enables magic committer default, sets multipart threshold/size to minimum, uses array fast-upload buffer, configures summary report directory, and enables experimental IOStatistics collection.
- `setup()` creates a local reports directory and initializes `CommitterTestHelper`.
- `bindCommitter()` writes committer factory and committer name options.
- `rmdir()` deletes paths through their configured filesystem.
- `randomJobId()` builds a MapReduce-compatible job id from current date/randomness and `test.unique.fork.id`.
- `abortMultipartUploadsUnderPath()`, `assertMultipartUploadsPending()`, `assertNoMultipartUploadsPending()`, and `countMultipartUploads()` wrap S3A multipart upload test utilities.
- `verifySuccessMarker()`, `validateSuccessFile()`, and `loadSuccessFile()` load `_SUCCESS`, validate committer name/job id/file count, log metrics/diagnostics, aggregate job IOStatistics, and also read it through manifest committer tooling.
- `CloseWriter` safely closes `RecordWriter`s.
- `taskAttemptForJob()` creates a MapReduce `TaskAttemptContext` from a YARN job id.

## Control Flow and State

Subclasses inherit configuration setup before creating S3A filesystems. Per-test setup creates report output and helper state. Commit tests write data, commit jobs, then call success-marker and MPU assertions. Static `JOB_STATISTICS` aggregates IO stats from all loaded success files and is logged in `@AfterAll`.

## State and Persistence Behavior

Local report files are written under the project build directory. S3A test output and multipart uploads are created in the target bucket by subclasses. The base cleans only through helper calls used by subclasses; it also maintains static aggregate IO statistics.

## Dependencies and Integration Points

It integrates S3A committer constants, multipart test utilities, `SuccessData`, manifest success data/printer, Hadoop MapReduce contexts, YARN id builders, S3A filesystem instrumentation, AssertJ, and contract test utilities.

## Risks and Edge Cases

Committer tests rely on real multipart upload support, correct cleanup of pending MPUs, and non-empty S3A success data. `randomJobId()` assumes the fork id ends in four digits. The success-file validation intentionally fails if `_SUCCESS` is zero bytes, because that indicates a non-S3A committer path.

## Test Signals

Signals include presence and nonzero size of `_SUCCESS`, valid `SuccessData`, matching committer and job id, minimum committed file count, manifest-printer loadability, logged IOStatistics/diagnostics, and absence/presence of pending MPUs under tested prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractCommitITest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractITCommitProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractITCommitProtocol.java

## Purpose

`AbstractITCommitProtocol` is the main abstract integration suite for S3A committers. It exercises the full MapReduce output committer lifecycle across normal commits, task/job aborts, duplicate attempts, speculative attempts, failure injection, output-format integration, AM-like workflows, parallel jobs, UUID propagation, and committer factory binding.

## Important APIs, Types, and Functions

- Abstract extension points: `suitename()`, `createCommitter(Path, TaskAttemptContext)`, `getCommitterName()`, `createFailingCommitter()`, and validation hooks for work paths and task output paths.
- Setup builds unique `jobId`, task attempt IDs, verifies multipart support, derives an isolated output dir, aborts old MPUs, and deletes old output.
- `JobData` stores `Job`, `JobContext`, `TaskAttemptContext`, `AbstractS3ACommitter`, configuration, and optional written path.
- `newJob()`, `startJob()`, `setup()`, `commit()`, `commitTask()`, `commitJob()`, and `abortJobQuietly()` model MR job/task setup, write, commit, and cleanup.
- `writeTextOutput()` and `writeMapFileOutput()` write deterministic output through `LoggingTextOutputFormat` or `MapFileOutputFormat`.
- `validateContent()`, `getPart0000()`, `validateMapFileOutputContent()`, and `validateStorageClass()` assert final output.
- Tests cover recovery unsupported, commit lifecycle, storage class, duplicate commit, two task attempts, injected job commit failure/retry, no-output commit, map-file output, abort variants, concurrent subdir commits, output format integration, AM workflow, parallel jobs to adjacent/same destinations, self-generated UUIDs, required propagated UUIDs, and factory binding.

## Control Flow and State

Each test starts with a clean S3 output directory and no pending MPUs. `startJob()` creates a job, contexts, and committer, runs `setupJob()` and `setupTask()`, registers cleanup, and optionally writes output. Task commit promotes task data/metadata to job-commit-visible state, while job commit makes final output visible and writes `_SUCCESS`. Abort paths cancel task/job state and pending uploads. Parallel-job tests deliberately interleave task writes and job commits to validate isolation through unique paths and UUIDs.

## State and Persistence Behavior

The suite creates S3 objects, pending multipart uploads, committer metadata, MapFile directories, and success markers under per-method output paths. It keeps a list of jobs to abort during teardown and always attempts MPU cleanup under the output dir. It also checks that no S3A committer thread pools leak after all tests.

## Dependencies and Integration Points

It integrates S3A committer implementations, `AbstractS3ACommitter`, `MagicS3GuardCommitter`, `S3ACommitterFactory`, `CommitterFaultInjection`, MapReduce `OutputFormat` and `OutputCommitter`, `LoggingTextOutputFormat`, `MapFileOutputFormat`, S3A storage-class metadata, IOStatistics, Spark write UUID config, and Hadoop contract test helpers.

## Risks and Edge Cases

The suite targets high-risk commit semantics: output must not be visible after task commit alone; duplicate task commit should fail or be safely handled; a later speculative attempt must supersede earlier output; job commit retry can expose partially completed state; aborts must be idempotent and MPU-clean; two jobs to the same destination must not delete each other's active uploads when configured; generated UUIDs must not be used by independent task-only committers; and factory binding must select the configured committer.

## Test Signals

Signals include final file content equality, storage class equality, success marker validation with committer UUID, no pending MPUs after commit/abort, expected `FileNotFoundException` or `PathCommitException` failures, task commit IOStatistic counters, absence of leaked committer threads, isolation of parallel job output filenames, UUID source/config assertions, and factory-created class equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractITCommitProtocol.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractYarnClusterITest.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractYarnClusterITest.java

## Purpose

`AbstractYarnClusterITest` is the base class for full MapReduce-on-YARN S3A committer integration tests. It manages shared MiniYARN and optional MiniDFS clusters, creates job configurations, applies committer binding/staging options, and exposes scale-test sizing.

## Important APIs, Types, and Functions

- Static `ClusterBinding` holds a cluster name, optional `MiniDFSClusterService`, and `MiniMRYarnCluster`.
- `createCluster(JobConf, boolean)` prepares test config, disables MR history cleanup and NM disk health checks, optionally starts HDFS, starts MiniYARN with two node managers, and returns binding.
- `teardownClusters()` and `terminateCluster()` stop shared clusters.
- `getClusterFS()` returns HDFS if present, otherwise local FS from YARN config.
- `setup()` initializes superclass state, reads scale-test flag, lazily creates cluster binding, and validates it.
- `newJobConf()` starts from YARN config, adds the S3A test config resource, and calls `applyCustomConfigOptions()`.
- `createJob()` creates a named MR job and patches committer configuration.
- `patchConfigurationForCommitter()` sets unique filename policy, S3A committer factory/name, scale-test flag, and local staging temp directory.
- Extension points: `committerName()`, `demandCreateClusterBinding()`, `applyCustomConfigOptions()`, `customPostExecutionValidation()`, and `isUniqueFilenames()`.

## Control Flow and State

Subclasses lazily create a static cluster binding on first setup. Each test gets a JUnit `@TempDir` staging directory, then job configs are derived from the running YARN cluster and patched with the S3A committer and staging options. Scale mode changes mapper/file counts from 1/10 to 10/100.

## State and Persistence Behavior

The cluster binding is static and shared across test methods until `@AfterAll` teardown. Local staging directories are per-test temporary directories. If HDFS is requested, it is a service in the binding and provides the cluster filesystem; otherwise local FS is used.

## Dependencies and Integration Points

It integrates `MiniMRYarnCluster`, optional `MiniDFSClusterService`, S3A committer constants, Hadoop `JobConf`/`Job`, JUnit `@TempDir`, S3A test configuration propagation, and scale-test flags.

## Risks and Edge Cases

Static cluster binding can cause isolation issues if multiple subclasses share the same JVM, so subclasses are expected to control explicit setup/teardown. MiniYARN disk health checks are disabled to avoid false failures in constrained CI. Local staging must be visible to workers for staging committers.

## Test Signals

Signals are produced by subclasses running actual MR jobs. This base contributes validation through successful cluster startup, non-null binding, correct committer config, correctly chosen test file/key counts, and later success-data validation hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/AbstractYarnClusterITest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjection.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjection.java

## Purpose

`CommitterFaultInjection` is a small interface that marks failing committer test implementations and defines which lifecycle operations can be forced to fail.

## Important APIs, Types, and Functions

- `COMMIT_FAILURE_MESSAGE` is the common failure text.
- `setFaults(Faults...)` configures active fault points.
- `Faults` enum covers `abortJob`, `abortTask`, `cleanupJob`, `commitJob`, `commitTask`, `getWorkPath`, `needsTaskCommit`, `setupJob`, and `setupTask`.

## Control Flow and State

Implementations are expected to store the configured enum set and throw when a matching lifecycle method is invoked. `AbstractITCommitProtocol` casts failing committers to this interface to inject `commitJob` failure and validate retry behavior.

## State and Persistence Behavior

The interface itself has no state. Implementations maintain in-memory fault sets.

## Dependencies and Integration Points

It is used by `CommitterFaultInjectionImpl` and abstract/protocol committer subclasses that need to provide failing variants.

## Risks and Edge Cases

The enum includes lifecycle points that may not be implemented by every failing committer wrapper. Tests relying on a specific fault require the committer under test to honor that enum member.

## Test Signals

The signal is an expected injected `IOException` with `COMMIT_FAILURE_MESSAGE`, followed by test-specific assertions about retry or cleanup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjection.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjectionImpl.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjectionImpl.java

## Purpose

`CommitterFaultInjectionImpl` is a concrete `PathOutputCommitter` used to simulate failures at specific output committer lifecycle methods. It is a generic fault-injection implementation for committer tests.

## Important APIs, Types, and Functions

- Constructor takes output path, job context, `resetOnFailure`, and initial faults.
- `setFaults(Faults...)` replaces the active fault set.
- `maybeFail(Faults)` throws `Failure` if the condition is active and optionally removes it first.
- Lifecycle overrides call `maybeFail()` for `getWorkPath`, `setupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, `abortTask`, `commitJob`, and `abortJob`.
- `Failure` extends `IOException` and uses `COMMIT_FAILURE_MESSAGE`.

## Control Flow and State

Each lifecycle method checks the `faults` set before returning or doing nothing. If `resetOnFailure` is true, the first failure at a given condition consumes that condition, allowing retry to succeed. `getOutputPath()` and non-faulting methods return null/no-op values because this class is not intended as a functional committer.

## State and Persistence Behavior

The fault set and reset flag are in-memory only. There is no filesystem state beyond the superclass constructor binding.

## Dependencies and Integration Points

It depends on Hadoop `PathOutputCommitter`, `JobContext`, `TaskAttemptContext`, and `JobStatus.State`. It is used directly or as a helper by failing S3A committer implementations.

## Risks and Edge Cases

Because it returns null paths and does not perform real commit logic, it is suitable only for targeted lifecycle failure tests. The `cleanupJob` enum member is declared in the interface but not handled here by an override.

## Test Signals

Tests observe `CommitterFaultInjectionImpl.Failure` at configured lifecycle points and, when `resetOnFailure` is used, successful retry after the first injected exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterFaultInjectionImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterTestHelper.java

## Purpose

`CommitterTestHelper` provides focused helper assertions and utilities for S3A committer tests, especially magic-committer marker files and multipart upload cleanup/listing.

## Important APIs, Types, and Functions

- Constructor requires an `S3AFileSystem`.
- `JOB_ID` is a fixed test job id used for magic path construction.
- `getFileSystem()` returns the bound test filesystem.
- `assertIsMarkerFile(Path, long)` verifies the path exists, has zero length, and exposes the magic marker xattr with the expected data length.
- `assertFileLacksMarkerHeader(Path)` verifies the magic marker length xattr is absent.
- `makeMagic(Path)` builds a magic path under `__magic_job-<JOB_ID>/base/<filename>` relative to the destination file's parent.
- `assertIsMagicStream(FSDataOutputStream)` asserts the stream advertises `STREAM_CAPABILITY_MAGIC_OUTPUT`.
- `abortMultipartUploadsUnderPath(Path)` clears pending MPUs through `MultipartTestUtils`.
- `listMultipartUploads(String)` returns pending MPU descriptions for a prefix.

## Control Flow and State

The helper is constructed during test setup and delegates all operations to the bound `S3AFileSystem`. Assertions typically follow a write or commit operation to validate marker-file behavior. Cleanup methods are used in teardown and pre-test setup.

## State and Persistence Behavior

The only local state is the filesystem reference. It inspects or mutates remote S3 state by checking files/xattrs and clearing multipart uploads.

## Dependencies and Integration Points

It integrates S3A magic committer constants, `CommitOperations.extractMagicFileLength()`, `MultipartTestUtils`, contract path existence checks, AssertJ, and S3A stream capability APIs.

## Risks and Edge Cases

Magic marker xattr extraction depends on S3A internals. `makeMagic()` assumes the magic path layout with fixed `JOB_ID` and `BASE`. MPU cleanup is broad under the provided path and should only be used on isolated test prefixes.

## Test Signals

Signals include zero-byte marker file status, expected magic file length xattr, absence of magic marker header on ordinary pending files, stream capability presence, and empty/non-empty MPU listings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/CommitterTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperationCost.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperationCost.java

## Purpose

`ITestCommitOperationCost` is an S3A performance/cost integration test suite for magic committer operations. It asserts that specific magic-path operations avoid unnecessary S3 HEAD/LIST/delete requests and produce expected metric deltas.

## Important APIs, Types, and Functions

- Extends `AbstractS3ACostTest`.
- `setup()` assumes multipart upload support and creates a `CommitterTestHelper`.
- `teardown()` aborts MPUs under the method path.
- `methodSubPath()` builds a path under the per-method test directory.
- `fileSystemIOStats()` returns pretty-printed FS IOStatistics.
- `testMagicMkdirs()` verifies mkdir/delete behavior under `__magic_job-<JOB_ID>/subdir`, including no bulk deletes and no parent marker recreation.
- `testCostOfCreatingMagicFile()` creates a file through a magic path, verifies no HEAD/LIST on create, magic stream capability, MPU initiation, marker/manifest PUTs on close, listing pending commits, loading pending commit without HEAD/LIST, and committing without extra probes/deletes.
- `testCostOfSavingLoadingPendingFile()` writes a synthetic `SinglePendingCommit` under a magic path, verifies save cost, verifies no marker header, and loads it from a `FileStatus` without HEAD/LIST.

## Control Flow and State

The tests use `verifyMetrics()` around a single filesystem or commit operation and assert expected statistic deltas. Magic file creation starts an S3A output stream, writes bytes, closes it, locates the pending commit manifest, loads it as `SinglePendingCommit`, then commits it via `CommitOperations`. The pending-file test constructs a minimal valid `SinglePendingCommit` manually before saving/loading it.

## State and Persistence Behavior

The suite creates and deletes S3 test paths under `methodPath()`, initiates multipart uploads for magic streams, writes pending commit manifests, and aborts any leftover MPUs in teardown. The active stream is stored in a field so it can be aborted on failure.

## Dependencies and Integration Points

It integrates S3A cost-test metrics, S3A statistics constants, magic committer path constants, `CommitterTestHelper`, `CommitOperations`, `PersistentCommitData`, `SinglePendingCommit`, S3A `FSDataOutputStream` abort semantics, and IOStatistics logging.

## Risks and Edge Cases

Cost assertions are sensitive to implementation changes in S3A request patterns. Magic-path behavior deliberately skips existence checks, so incorrect use outside isolated test paths could overwrite or bypass checks. The synthetic pending commit uses fake upload id/etag state only for save/load cost validation, not real MPU completion.

## Test Signals

Signals are metric assertions: no HEAD/LIST for magic create/save/load/commit paths, expected MPU initiation count, expected marker PUT counts, expected delete/list/metadata counts for magic mkdir/delete, one pending commit located, successful pending commit load, absent marker header on ordinary pending files, and cleanup of active streams/uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestCommitOperationCost.java -->
