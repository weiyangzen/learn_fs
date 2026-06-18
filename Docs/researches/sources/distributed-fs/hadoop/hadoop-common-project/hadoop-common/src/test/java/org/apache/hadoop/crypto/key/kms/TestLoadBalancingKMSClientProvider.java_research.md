# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/key/kms/TestLoadBalancingKMSClientProvider.java

## Purpose
`TestLoadBalancingKMSClientProvider` verifies multi-KMS URI parsing, round-robin provider selection, retry/failover policy by operation idempotence and exception class, warmup error handling, token service naming, and current-user credential lookup.

## Important APIs, Types, and Functions
The suite exercises `KMSClientProvider.Factory.createProvider`, `LoadBalancingKMSClientProvider.getProviders`, `getCanonicalServiceName`, `createKey`, `getCurrentKey`, `getKeys`, `getKeyVersions`, `generateEncryptedKey`, `decryptEncryptedKey`, `rollNewVersion`, `warmUpEncryptedKeys`, and provider `getActualUgi`. It uses mocked `KMSClientProvider` instances and config key `KMS_CLIENT_FAILOVER_MAX_RETRIES_KEY`.

## Control Flow
Creation tests parse `kms://http@host...` URIs into one or more backing KMS URLs. Load-balancing tests verify round-robin calls and distinguish retriable `IOException` from non-retriable `NoSuchAlgorithmException`. Retry tests cover all-bad nodes, idempotent versus non-idempotent operations, access-control and runtime exceptions that stop failover, connection/route/host/timeout/socket/SSL exceptions that can fail over or retry, exact configured retry counts, and default retry counts. Warmup tests require all providers to be tried and succeed if at least one succeeds. Token tests compare legacy `host:port` service names with URI-format services. UGI tests run under a test user and verify providers use the current user, not the login user.

## State and Persistence
State is in-memory mocks, credentials, tokens, retry counters, and UGI context. No KMS server or durable key store is used.

## Dependencies and Integration Points
Dependencies include KMS client classes, Hadoop security classes, token kinds, `UserGroupInformation`, `SecurityUtil`, `CommonConfigurationKeysPublic`, Mockito, `LambdaTestUtils.intercept`, and network/SSL exception classes.

## Risks and Edge Cases
This file encodes subtle policy boundaries: non-idempotent mutations should not be blindly replayed on ambiguous IO failures, authorization/runtime failures should not be hidden by failover, transient network and SSL failures may retry, URI token services must coexist with legacy services, and current-user credentials must be honored in Kerberos mode.

## Test Signals
Passing tests signal correct multi-host URL construction, round-robin behavior, failover classification, retry counts, warmup tolerance, exception wrapping preservation, token service naming, and UGI selection.
