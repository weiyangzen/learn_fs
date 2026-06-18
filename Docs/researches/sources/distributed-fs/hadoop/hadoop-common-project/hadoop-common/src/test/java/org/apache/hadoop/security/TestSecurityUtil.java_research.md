# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/TestSecurityUtil.java

Purpose: exercises `SecurityUtil`, related `NetUtils` token-service helpers, Kerberos principal utilities, ZK auth loading, and host resolver caching. It prevents regressions in principal expansion, lower-casing, wildcard host handling, token service address canonicalization, authentication method configuration, and resolver failure behavior.

Important APIs and types: `SecurityUtil.getServerPrincipal`, `isTGSPrincipal`, `getHostFromPrincipal`, `buildDTServiceName`, `buildTokenService`, `setTokenService`, `getTokenServiceAddr`, `getZKAuthInfos`, `setAuthenticationMethod`, `getAuthenticationMethod`, `StandardHostResolver`, `QualifiedHostResolver`, `CacheableHostResolver`; also `CredentialProviderFactory`, `LocalJavaKeyStoreProvider`, `Token`, `ZKAuthInfo`, `NetUtils`, and mocked `InetAddress`.

Control flow: setup pins Kerberos realm properties so host/principal tests are deterministic. Helper methods validate both string and `InetAddress` principal expansion, then address helpers construct socket addresses, encode token services under `use_ip` true and false, and decode back. Auth tests load ZK auth from literal config, `@file` indirection, and local JCEKS. Resolver tests toggle `HADOOP_SECURITY_TOKEN_SERVICE_USE_IP` and hostname cache duration to assert resolver type and cache presence, then test cached identity reuse, expiry, and invalid host exceptions.

State and persistence: mutates JVM system properties for Kerberos, static `SecurityUtil` configuration and resolver singletons, `NetUtils` static resolutions, temporary auth files, and local JCEKS credential stores. Temp files are deleted in finally blocks, but static configuration can affect neighboring tests if run in the same JVM without reset.

Dependencies and integration points: integrates Hadoop configuration keys, Kerberos Java principal parsing, Hadoop credential providers, token serialization services, `NetUtils` static DNS overrides, Guava file helpers, Mockito, and JUnit 5. It tests the security layer as consumed by RPC token service generation and ZK authentication config.

Risks: DNS and hostname resolution may vary by host environment. Static resolver and config state can bleed across tests. Cache expiry uses `Thread.sleep(1500)`, which is timing-sensitive. The local JCEKS test depends on provider registration and filesystem permissions.

Test signals: strong signal for principal replacement, auth config validation, malformed socket address rejection, service-address round trips, ZK auth source precedence, resolver type selection, resolver cache hit/expiry, and invalid-host exception propagation.
