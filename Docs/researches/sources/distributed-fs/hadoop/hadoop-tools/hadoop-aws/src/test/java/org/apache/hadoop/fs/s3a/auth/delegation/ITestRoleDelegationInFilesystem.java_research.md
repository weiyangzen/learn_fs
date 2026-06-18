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
