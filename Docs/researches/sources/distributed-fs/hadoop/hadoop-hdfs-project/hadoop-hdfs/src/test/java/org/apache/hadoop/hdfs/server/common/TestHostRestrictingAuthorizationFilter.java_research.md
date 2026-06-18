# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/common/TestHostRestrictingAuthorizationFilter.java

Purpose: this test checks `HostRestrictingAuthorizationFilter`, an HTTP filter that restricts WebHDFS operations by user, remote host/CIDR, and path rules while allowing unrelated NameNode HTTP requests through.

Important APIs and types: `HostRestrictingAuthorizationFilter`, servlet `Filter`, `FilterConfig`, `FilterChain`, `HttpServletRequest`, `HttpServletResponse`, `WebHdfsFileSystem.PATH_PREFIX`, and Hadoop `AuthenticationFilter` config. `DummyFilterConfig` supplies init parameters and a mocked servlet context.

Control flow: each test creates a mocked request/response pair and invokes the filter directly. `testAcceptAll` supplies a wildcard allow rule. `testAcceptGETFILECHECKSUM` checks that checksum GET is not treated like restricted file-open GET. `testRuleAllowedGet` configures a multi-rule allow string and sends a matching `op=OPEN` WebHDFS request. `testRejectsGETs` sends an OPEN request with no allow rule, exercising default denial behavior. `testUnexpectedInputMissingOpParameter` covers malformed/missing operation input. `testNotWebhdfsAPIRequest` verifies non-WebHDFS paths such as `/conf` pass through.

State and persistence: no persistent state is used. The filter stores parsed init parameters in memory. Request state comes entirely from Mockito stubs.

Dependencies and integration points: this is an HTTP-layer security test for WebHDFS. It integrates Hadoop authentication-filter settings with custom authorization logic, but uses direct servlet mocks rather than an embedded HTTP server.

Risks: several negative tests do not verify `sendError`, so they primarily ensure no crash rather than exact deny/allow status. Requests sometimes stub `getRemoteAddr` twice. Query-string parsing includes whitespace in `op=GETFILECHECKSUM `, making the test useful for tolerance but dependent on implementation trimming behavior.

Test signals: failures point to regressions in host allow-rule parsing, WebHDFS operation classification, or bypass behavior for non-WebHDFS endpoints.
