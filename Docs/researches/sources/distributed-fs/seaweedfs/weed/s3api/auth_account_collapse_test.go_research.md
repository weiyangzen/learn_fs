# sources/distributed-fs/seaweedfs/weed/s3api/auth_account_collapse_test.go

## Purpose

`s3api/auth_account_collapse_test.go` protects S3 IAM account ownership behavior for account-less identities. It was read as a complete 131-line file.

## Important APIs, Types, and Functions

Tests are `TestAccountForUnscopedIdentity`, `TestUnscopedIdentitiesGetDistinctAccounts`, `TestCheckAccessByOwnershipDeniesNonOwner`, `TestUnscopedIdentityAccountResolvesByName`, and `TestUnscopedIdentityReusesConfiguredAccount`.

## Control Flow

Tests reset the memory store, write temporary JSON configs, initialize IAM, look up identities by access key, and assert account IDs/display names. Ownership access is tested with an in-memory `BucketRegistry` and HTTP requests carrying `AmzAccountId`.

## State and Persistence Behavior

Temporary config files and in-memory IAM/account stores are used. The tests verify synthesized accounts are registered and do not collapse to admin except for conventional admin/empty identity.

## Dependencies and Integration Points

Depends on IAM config loading, memory account store, S3 bucket ownership checks, AWS S3 owner type, and S3 constants/errors.

## Risks and Edge Cases

Regressions here can make non-admin unscoped users inherit admin ownership or fail ACL owner resolution. Tests do not cover persistent IAM stores.

## Test Signals

Strong regression coverage for account isolation, owner access denial, account-name lookup, and configured-account reuse.
