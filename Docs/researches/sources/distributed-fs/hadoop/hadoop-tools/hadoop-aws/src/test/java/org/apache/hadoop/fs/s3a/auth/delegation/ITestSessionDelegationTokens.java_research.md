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
