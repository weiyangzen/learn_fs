# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestKeyProviderCache.java

## Purpose
Tests `KeyProviderCache` identity caching and invalidation behavior for configured key-provider URIs.

## APIs and Control Flow
`DummyKeyProvider` implements the abstract `KeyProvider` methods as no-ops and increments a static close counter. `Factory` creates dummy providers for `dummy://` URIs. `testCache` creates a cache, requests providers for identical URI, different host URI, and same host with different userinfo, checking object identity differences, then calls `invalidateCache` and expects three close calls. `getKeyProviderUriFromConf` reads the configured provider path and converts it to `URI`.

## State, Dependencies, Integration
State is cache contents keyed by provider URI and static close-call count. Dependencies include Hadoop crypto `KeyProvider`, `KeyProviderFactory`, `CommonConfigurationKeysPublic`, and URI parsing. It integrates cache lifetime behavior with provider factory resolution.

## Risks and Test Signals
Signals are identity equality/inequality and close count. Risks include static `CLOSE_CALL_COUNT` not reset between repeated runs in the same JVM and needing service-provider registration for `Factory` outside this file.
