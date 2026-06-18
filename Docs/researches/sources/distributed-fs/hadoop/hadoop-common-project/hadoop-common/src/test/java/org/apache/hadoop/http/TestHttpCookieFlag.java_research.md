# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java

Purpose: this functional test verifies authentication cookie flags over HTTP and HTTPS: all auth cookies should be `HttpOnly`, and HTTPS cookies should also be secure.

Important APIs and types: nested `DummyAuthenticationFilter` creates an auth cookie based on `request.getScheme()`. `DummyFilterInitializer` registers it. Setup creates HTTP and HTTPS endpoints with generated SSL material and a client `SSLFactory`.

Control flow: `setUp()` builds the server, adds `/echo`, and starts it. `testHttpCookie()` requests HTTP `/echo`, parses `Set-Cookie`, and asserts `HttpOnly` and token value. `testHttpsCookie()` requests HTTPS `/echo` with the client SSL socket factory and additionally asserts `HttpCookie.getSecure()`.

State and persistence: temporary keystore/truststore files live under a test temp path and are cleaned in `AfterAll`. Static server and SSL factory are shared across methods.

Dependencies and integration points: integrates Hadoop auth cookie generation, servlet filters, `HttpServer2` dual-protocol endpoint setup, `KeyStoreTestUtil`, and `SSLFactory`.

Risks: relies on generated local certificates and Java HTTPS behavior. Header string inspection checks `HttpOnly` literally, while secure flag uses parsed cookie state.

Test signals: validates expected cookie hardening for both cleartext and TLS endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpCookieFlag.java -->
