# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-kms/src/main/java/org/apache/hadoop/crypto/key/kms/server/KMSWebApp.java

## Purpose
`KMSWebApp.java` is the servlet context listener that initializes and tears down the KMS runtime object graph: configuration, UGI, ACLs, metrics, audit, key provider, caching, eager EEK generation, and per-key authorization.

## Important APIs, Types, and Functions
`contextInitialized` performs startup. `contextDestroyed` closes provider, audit, ACL reloader, JMX reporter, and metrics. Static getters expose configuration, ACLs, meters, provider, and audit service to resource/filter classes.

## Control Flow
Startup loads KMS config, sets UGI configuration, starts ACL reloading, creates Dropwizard meters and JMX reporter, initializes audit, resolves the backing key provider from `hadoop.kms.key.provider.uri`, optionally wraps it in `CachingKeyProvider`, wraps it in `KeyProviderCryptoExtension`, then `EagerKeyGeneratorKeyProviderCryptoExtension`, and finally optionally `KeyAuthorizationKeyProvider`. Any startup failure prints a detailed message and exits the JVM.

## State and Persistence
Most server runtime state is static in this class. Persistent key state lives in the backing provider; this class controls cache wrappers and flush exposure indirectly. Metrics are process-local and exposed through JMX.

## Dependencies and Integration Points
It integrates with Servlet context lifecycle from `web.xml`, Hadoop configuration and key provider factories, Dropwizard metrics, SLF4J bridge handling, `KMSACLs`, `KMSAudit`, and all REST/filter classes that use its static getters.

## Risks
Static global state simplifies access but makes embedded tests and multiple webapp instances sensitive to lifecycle order. `System.exit(1)` on initialization failure is appropriate for daemon startup but harsh in embedding contexts. Correct wrapper order is security-sensitive: per-key authorization must wrap the crypto extension after caching/eager generation. `getConfiguration` returns a defensive copy.

## Test Signals
Tests should verify missing provider failure, cache enable/disable behavior, per-key authorization enable/disable, meter registration, ACL reloader lifecycle, teardown cleanup, and wrapper ordering with authorization checks.
