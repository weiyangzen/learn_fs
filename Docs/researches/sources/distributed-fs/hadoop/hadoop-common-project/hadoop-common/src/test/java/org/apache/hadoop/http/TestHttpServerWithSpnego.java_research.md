# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java

Purpose: this integration test validates `HttpServer2` with SPNEGO/Kerberos authentication, proxy-user authorization, admin ACLs, and authentication endpoint allow-list behavior.

Important APIs and types: uses `MiniKdc`, Kerberos test utilities, `AuthenticationFilterInitializer`, `ProxyUserAuthenticationFilterInitializer`, `AuthenticatedURL`, signed `AuthenticationToken`s, `Signer`, `SignerSecretProvider`, `ProxyUsers`, `AccessControlList`, and `HttpServer2.Builder`.

Control flow: `BeforeAll` starts a MiniKDC, creates an HTTP service principal/keytab, and writes a signer secret file. `testAuthenticationWithProxyUser()` configures proxy-user SPNEGO, creates users/groups, allows userA to impersonate groupB, starts a server with admin ACL, signs tokens for userA and userB, and checks impersonated access to default servlets plus admin-only access to `/logs` and `/logLevel`. `testAuthenticationToAllowList()` configures a whitelist for `/jmx` and `/prom`, enables Prometheus, starts a security-enabled server, and verifies whitelisted endpoints skip Kerberos while others return unauthorized.

State and persistence: writes keytab and secret file under target test root; MiniKDC holds Kerberos state; system property `hadoop.log.dir` points at the test root. Server state is local and stopped in finally blocks.

Dependencies and integration points: integrates Hadoop auth filters, Kerberos, proxy-user configuration, signed cookie/token authentication, admin ACL checks, default servlet security, and Prometheus endpoint exposure.

Risks: MiniKDC setup is environment-sensitive and uses a broad `assertTrue(false)` on setup failure. Tokens are manually signed, so the test bypasses live Kerberos exchange after server setup while still testing server-side filter behavior.

Test signals: validates allowed and denied proxy impersonation, admin vs non-admin access to sensitive servlets, and whitelist bypass for selected endpoints under SPNEGO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServerWithSpnego.java -->
