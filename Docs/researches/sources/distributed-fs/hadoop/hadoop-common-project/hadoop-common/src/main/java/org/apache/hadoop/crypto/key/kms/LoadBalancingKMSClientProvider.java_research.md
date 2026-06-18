# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/crypto/key/kms/LoadBalancingKMSClientProvider.java

## Purpose
`LoadBalancingKMSClientProvider` wraps multiple `KMSClientProvider` instances, round-robins requests across them, and fails over on retryable I/O/network failures. It also normalizes delegation-token behavior across a KMS HA group.

## Important APIs and types
The class extends `KeyProvider` and implements `CryptoExtension` and `DelegationTokenExtension`. `ProviderCallable<T>` abstracts an operation on one provider. `WrapperException` transports checked non-IO exceptions through retry code. Key fields are provider array, atomic current index, delegation token service, canonical token alias, and retry policy.

## Control flow
Construction computes token services, optionally shuffles providers, sets each provider's client-token-provider to this load balancer, initializes round-robin index, and builds a failover retry policy from configuration. `doOp()` selects providers from a starting position, invokes the operation, does not retry access-control errors, wraps SSL/socket errors as connect exceptions for retry policy, sleeps after trying all providers in a cycle, and ensures each provider is tried at least once before final failure. Mutating operations such as create/delete/roll use non-idempotent retry flags; reads and EEK operations use idempotent flags where appropriate. Some operations, such as warmup, drain, invalidate, flush, and close, are broadcast to all providers.

## State and persistence
State is in-memory provider list, current index, token service aliases, and retry policy. Persistent key state remains on KMS servers. Mutations that succeed on one KMS are expected to become visible through shared backend/server state.

## Dependencies and integration points
It depends on `KMSClientProvider`, Hadoop retry policies, security tokens, KMS configuration keys, and `KMSUtil`. It is always returned by `KMSClientProvider.Factory` for valid KMS URIs, even with one host.

## Risks
Non-idempotent mutation retry is intentionally constrained but still depends on the retry policy and failure timing. Access-control failures are not retried under the assumption all KMS hosts share ACLs. Canonical token alias handling must balance deterministic token acquisition with backwards-compatible per-host aliases. Provider shuffling improves distribution but tests need deterministic seed paths.

## Test signals
Tests should cover round-robin order, failover on IO/SSL/socket exceptions, no retry on access control, retry limits/sleep behavior, broadcast operations, token selection via canonical and dt services, service rewriting on new tokens, deterministic no-shuffle construction, and close/flush error logging.
