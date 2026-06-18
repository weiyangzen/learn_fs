# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/token/DelegationTokenIssuer.java

## Purpose

`DelegationTokenIssuer` is the common interface for services that can issue delegation tokens and recursively collect tokens from dependent child services.

## Important APIs, Types, and Functions

Implementations provide `getCanonicalServiceName` and `getDelegationToken`. Defaults include `getAdditionalTokenIssuers`, `addDelegationTokens`, and static `collectDelegationTokens`.

## Control Flow

`addDelegationTokens` ensures a `Credentials` object exists, then calls `collectDelegationTokens`. Collection checks whether credentials already contain a token for the issuer's canonical service, fetches and stores a new token if absent, records new tokens in an output list, then recursively processes additional token issuers.

## State and Persistence Behavior

The interface owns no state. It mutates the supplied `Credentials` object by adding fetched tokens.

## Dependencies and Integration Points

It depends on `Credentials`, `Token`, `Text`, and SLF4J. File systems and services implement it so clients can gather all required delegation tokens before launching distributed work.

## Risks and Edge Cases

Null canonical service names skip token fetching for that issuer. Recursive child issuer graphs are not cycle-protected. Existing credentials suppress token refresh even if stale.

## Test Signals

Tests should cover absent and existing tokens, null service names, null input credentials, child issuer recursion, token list return values, and exception propagation from token acquisition.
