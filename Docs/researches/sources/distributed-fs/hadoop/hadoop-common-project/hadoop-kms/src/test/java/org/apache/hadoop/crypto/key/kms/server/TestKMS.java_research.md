# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/test/java/org/apache/hadoop/crypto/key/kms/server/TestKMS.java

## Purpose
`TestKMS.java` is the main integration-style test suite for Hadoop KMS. It validates that the MiniKMS server, KMS client provider, key provider operations, Kerberos/simple authentication, SSL, ACL enforcement, delegation tokens, ZooKeeper-backed shared state, proxy users, JMX, and filter initialization all behave correctly together.

## Important APIs, Types, and Functions
- `TestKMS` is a JUnit 5 class with a 180 second timeout. It owns MiniKdc lifecycle, MiniKMS lifecycle helpers, client provider creation, SSL factory setup, and cleanup.
- `KMSCallable<T>` wraps test logic that runs after one or more MiniKMS instances start. It stores KMS URLs and can produce a load-balancing `kms://http@host,...` provider URI.
- `runServer(...)` starts one or more `MiniKMS` instances, injects their URLs into the callable, executes the callable, and stops all instances in `finally`.
- `createBaseKMSConf(...)`, `writeConf(...)`, `createKMSUri(...)`, and `createKMSHAUri(...)` build test KMS configuration and client URIs.
- The nested `KerberosConfiguration` builds JAAS login entries for keytab-backed Kerberos logins.
- `setUpMiniKdc(...)`, `doAs(...)`, and `tearDown()` manage a real MiniKdc, keytab principals, UGI state, and all created `KeyProvider` instances.

## Control Flow and Behavior
The suite starts by creating a fresh MiniKdc and resetting UGI in `setUp()`. Individual tests create temporary KMS configuration directories, write `kms-site.xml`, `kms-acls.xml`, and an empty `core-site.xml`, start MiniKMS, and use `KMSClientProvider` or `LoadBalancingKMSClientProvider` to exercise server endpoints.

The core `testKMSProvider()` path creates keys, reads versions and metadata, rolls versions, generates/decrypts encrypted keys, re-encrypts individual and batch encrypted keys, deletes keys, validates post-delete failures, verifies default `key.acl.name` metadata behavior, and checks that `invalidateCache()` drains encrypted-key queues after rollover.

Authentication and authorization flows are split across several tests:
- `testStartStop*` covers HTTP/HTTPS and pseudo/Kerberos startup, JMX access, empty key lists, and delegation token acquisition.
- `testKeyACLs()` and `testACLs()` assert separation between global KMS ACLs and per-key ACLs, including management/read/generate/decrypt/whitelist/default ACL behavior.
- `testKMSBlackList()` checks blacklist denial behavior.
- `testServicePrincipalACLs()` verifies that service principals can be scoped correctly.
- `testKMSRestart*()` checks that a client can keep using a provider across a server restart on the same port.
- `testKMSAuthFailureRetry()` validates authentication-token expiry retry behavior and `KMSClientProvider.AUTH_RETRY`.
- `testDelegationTokenAccess()`, `testGetDelegationTokenByProxyUser()`, `testDelegationTokensOps*()`, and `testDelegationTokensUpdatedInUGI()` exercise token retrieval, renewal, cancellation, service binding, and UGI credential mutation.
- `testKMSWithZK*()` and `testKMSHAZooKeeperDelegationToken()` run multiple KMS instances against Curator `TestingServer` to validate ZooKeeper signer secrets, ZooKeeper delegation token secret manager state, and HA token compatibility.
- `testProxyUser*()`, `testWebHDFSProxyUser*()`, and `testTGTRenewal()` verify proxy user impersonation and Kerberos relogin/TGT renewal paths.

## State and Persistence
State lives in temporary directories under `target/<uuid>`, JCEKS keystores, generated XML config files, keytabs, in-memory UGI singleton state, client-side encrypted-key queues, delegation token credentials, and optional ZooKeeper znodes. The tests explicitly reset UGI, stop MiniKdc, stop MiniKMS, destroy SSL factories, and close providers to avoid cross-test leakage.

## Dependencies and Integration Points
This test integrates `MiniKMS`, `MiniKdc`, `KMSClientProvider`, `LoadBalancingKMSClientProvider`, `KeyProviderCryptoExtension`, `KeyProviderDelegationTokenExtension`, `KMSACLs`, `KeyAuthorizationKeyProvider`, `ValueQueue`, Hadoop `UserGroupInformation`, `Credentials`, `Token`, Curator `TestingServer`, SSL test utilities, HTTP/JMX endpoints, and ZooKeeper-backed Hadoop authentication/delegation token components.

## Risks and Edge Cases
The suite is sensitive to global UGI and JAAS state, wall-clock sleeps for token/signature expiry, ephemeral ports, ZooKeeper lifecycle, and Kerberos ticket timing. Reflection into client internals in `testKMSProviderCaching()` is brittle but gives direct cache invalidation coverage. The large number of real server starts makes timeout and cleanup correctness important.

## Test Signals
This file itself is the main signal for KMS server/client integration. It covers positive and negative authorization cases, token lifecycle, restart behavior, HA/ZK interoperability, proxy-user security, JMX availability, SSL setup, and regression checks for special key names and filter initialization.
