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
