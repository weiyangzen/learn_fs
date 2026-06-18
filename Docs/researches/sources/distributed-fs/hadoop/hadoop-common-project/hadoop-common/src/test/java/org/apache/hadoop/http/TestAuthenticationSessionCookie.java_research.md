# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java

Purpose: this test verifies `AuthenticationFilter.createAuthCookie()` behavior as surfaced through `HttpServer2` filters, distinguishing session cookies from persistent cookies.

Important APIs and types: defines `DummyAuthenticationFilter`, `DummyFilterInitializer`, `Dummy2AuthenticationFilter`, and `Dummy2FilterInitializer`. `startServer(boolean)` configures filter initializer, temporary keystores, HTTP and HTTPS endpoints, SSL key/trust stores, and an `/echo` servlet.

Control flow: session-cookie mode initializes `isCookiePersistent=false`; persistent mode sets `isCookiePersistent=true` and `expires` to current time plus a token validity interval. Both tests request `/echo`, parse the `Set-Cookie` header with `HttpCookie.parse()`, and assert token value plus presence or absence of `Expires`.

State and persistence: temporary SSL material is created under `GenericTestUtils.getTempPath(...)` and removed in `cleanup()`. Static fields hold server, SSL paths, persistence flag, and expiry value.

Dependencies and integration points: integrates Hadoop authentication filter cookie creation, `HttpServer2` filter initialization, `KeyStoreTestUtil`, Jetty/servlet filtering, and `TestHttpServer.EchoServlet`.

Risks: exception handling in tests prints stack traces but continues, which can obscure setup failures until later null/server assertions. Static mutable cookie flags couple filter initialization and request handling.

Test signals: asserts session cookies omit `Expires`, persistent cookies include it, and both carry the expected token value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestAuthenticationSessionCookie.java -->
