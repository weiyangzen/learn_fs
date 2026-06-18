# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/KeyProviderDelegationTokenExtension.java

## Purpose
`KeyProviderDelegationTokenExtension` adapts a `KeyProvider` to Hadoop's `DelegationTokenIssuer` contract when the provider can issue, select, renew, and cancel delegation tokens. It gives filesystems and clients a uniform way to obtain KMS tokens without hard-coding provider classes.

## Important APIs and types
The class extends `KeyProviderExtension<DelegationTokenExtension>` and implements `DelegationTokenIssuer`. Nested `DelegationTokenExtension` extends both the marker extension interface and `DelegationTokenIssuer`, adding `renewDelegationToken()`, `cancelDelegationToken()`, and a visible-for-testing `selectDelegationToken(Credentials)` method. `DefaultDelegationTokenExtension` returns null or zero for all operations.

## Control flow
`createKeyProviderDelegationTokenExtension()` checks whether the supplied provider implements `DelegationTokenExtension`. If so, it delegates to the provider; otherwise it wraps the provider with the no-op default. `getCanonicalServiceName()` and `getDelegationToken()` simply forward to the selected extension.

## State and persistence
State is the wrapped key provider and extension instance inherited from `KeyProviderExtension`. There is no token cache or persistence in this wrapper.

## Dependencies and integration points
It depends on Hadoop security `Credentials`, `Token`, and `DelegationTokenIssuer`. `KMSClientProvider` and `LoadBalancingKMSClientProvider` implement the extension so KMS delegation tokens can flow through generic key-provider consumers.

## Risks
The default no-op behavior can mask missing token support if callers do not check for null tokens. Renew/cancel methods are present on the extension interface but not publicly forwarded by this wrapper except through the underlying extension type, so callers needing those operations must retain or cast appropriately.

## Test signals
Tests should verify native extension selection, no-op fallback results, forwarding of canonical service and token acquisition, and integration with KMS providers that implement renew/cancel/select methods.
