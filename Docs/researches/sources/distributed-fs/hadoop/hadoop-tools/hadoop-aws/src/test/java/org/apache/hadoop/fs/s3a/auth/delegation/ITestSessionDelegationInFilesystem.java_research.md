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
