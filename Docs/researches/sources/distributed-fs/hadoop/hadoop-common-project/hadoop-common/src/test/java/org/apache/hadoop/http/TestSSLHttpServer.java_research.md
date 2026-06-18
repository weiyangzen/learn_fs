# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java

Purpose: this functional suite validates HTTPS support in `HttpServer2`: generated keystores, SSL client connectivity, echo servlet behavior, long headers, excluded/included cipher suites, and enabled protocol negotiation.

Important APIs and types: setup uses `KeyStoreTestUtil`, `SSLFactory`, `HttpServer2.Builder`, `EchoServlet`, `LongHeaderServlet`, and custom inner `PreferredCipherSSLSocketFactory`/`PreferredProtocolSSLSocketFactory`. Constants define excluded cipher lists, one-enabled cipher sets for TLS 1.2 and TLS 1.3, and enabled protocols.

Control flow: `BeforeAll` clears JVM `https.cipherSuites`, enables `javax.net.debug`, creates SSL material, initializes a client `SSLFactory`, builds an HTTPS server, registers servlets, and starts it. Tests request `/echo`, send a 63 KiB header, try excluded-only ciphers expecting `SSLHandshakeException`, verify negotiated TLS protocol based on Java version, and verify successful connections with at least one mutually enabled cipher. Cleanup stops the server, deletes SSL material, destroys the client factory, and restores JVM properties.

State and persistence: temporary keystore/truststore files are written under a test temp path. JVM SSL-related system properties are saved and restored. The preferred protocol socket factory records the last `SSLSocket` to inspect negotiated protocol.

Dependencies and integration points: integrates Jetty HTTPS connectors, Hadoop SSL config generation, Java TLS stack, cipher/protocol filtering, Hadoop IO utilities, and platform Java version detection.

Risks: TLS cipher availability varies by JDK and security policy; the test branches for Java 11+ TLS 1.3 but still depends on supported cipher names. Turning on global SSL debug logging can produce large logs and must be restored.

Test signals: validates secure servlet serving, request quoting over HTTPS, large headers over TLS, exclusion of insecure ciphers, protocol inclusion, and successful mutually compatible cipher negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestSSLHttpServer.java -->
