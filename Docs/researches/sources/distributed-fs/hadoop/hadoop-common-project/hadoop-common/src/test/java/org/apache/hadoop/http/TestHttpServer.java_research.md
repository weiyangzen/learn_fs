# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java

Purpose: this broad functional suite validates core `HttpServer2` behavior: servlet registration, parameter quoting, static content types, max threads, connector configuration, metrics, security headers, X-Frame options, default servlet authorization, Jersey resources, bind/find-port behavior, port ranges, backlog, idle timeout, and custom headers.

Important APIs and types: nested servlets include `EchoServlet`, `EchoMapServlet`, and `HtmlContentServlet`. Security helpers include `DummyServletFilter`, `DummyFilterInitializer`, `getHttpStatusCode()`, and `MyGroupsProvider`. Tests use `HttpServer2.Builder`, `HttpServer2Metrics`, `RequestQuoter`, `AccessControlList`, Jetty `ServerConnector`, `StatisticsHandler`, and Jersey `JerseyResource`.

Control flow: `BeforeAll` creates a server with max threads and metrics enabled, registers servlets and Jersey package, and starts it. Tests then perform concurrent requests, bad acceptor/selector config, echo/echomap quoting checks, long headers, MIME checks, metrics increments, X-Frame header enabled/disabled/invalid cases, admin authorization matrix for `/conf`, `/logs`, `/stacks`, `/logLevel`, Jersey JSON parsing, bind reuse and find-port checks, port-range allocation, socket backlog/idle timeout reflection, and default/custom header checks.

State and persistence: state includes a shared static server/base URL, custom group mapping static map, server metrics counters, Jetty connector state, and servlet context attributes. No durable application data is written.

Dependencies and integration points: integrates servlet filters, Hadoop security groups and ACLs, Jetty connectors/thread pool/statistics, JSON parsing, JAX-RS resources, Hadoop configuration keys, and network port utilities.

Risks: this file touches many shared server behaviors; failures may be environmental (ports, thread scheduling) or behavior regressions. Static `server` is reused and reassigned in `testAddConnectors`, so lifecycle care matters. Some tests rely on reflection into private listener fields.

Test signals: strong coverage for server construction, request handling, security and cache headers, authorization behavior, resource packages, connector lifecycle, metrics, and configuration-driven network behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestHttpServer.java -->
