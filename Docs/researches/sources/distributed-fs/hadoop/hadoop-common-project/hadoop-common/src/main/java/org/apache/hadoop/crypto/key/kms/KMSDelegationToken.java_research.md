# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/KMSDelegationToken.java

## Purpose
`KMSDelegationToken` centralizes the token kind and identifier type for Hadoop KMS delegation tokens.

## Important APIs and types
It defines `TOKEN_KIND_STR` as `"kms-dt"` and `TOKEN_KIND` as a `Text`. The nested `KMSDelegationTokenIdentifier` extends `DelegationTokenIdentifier`, initializes the superclass with the KMS token kind, and overrides `getKind()` to return it. The outer class is final with a private constructor.

## Control flow
There is no runtime flow beyond constructing identifiers. KMS client and server token code refer to the constants for selection and renewal.

## State and persistence
No mutable state exists. Token identifier serialization behavior comes from the superclass.

## Dependencies and integration points
It depends on Hadoop `Text` and `DelegationTokenIdentifier`. `KMSClientProvider.TokenSelector`, `KMSTokenRenewer`, and delegation-token auth paths use this token kind.

## Risks
Token-kind string compatibility is externally visible; changing it would break stored credentials and renewal selection. The class intentionally contains no server-side policy.

## Test signals
Tests should assert token kind constants, identifier `getKind()`, and integration with token selector/renewer matching.
