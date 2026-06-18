# Research: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java

Purpose: this unit test validates `IsActiveServlet` response behavior for active and inactive services.

Important APIs and types: uses an anonymous `IsActiveServlet` overriding `isActive()`, mocked `HttpServletRequest` and `HttpServletResponse`, `ByteArrayOutputStream`, and `PrintWriter`.

Control flow: setup wires the mocked response writer to a byte buffer. `testSucceedsOnActive()` returns true from `isActive()`, calls `doGet()`, verifies no error response, and asserts the active response body. `testFailsOnInactive()` returns false and verifies `sendError(SC_METHOD_NOT_ALLOWED, RESPONSE_NOT_ACTIVE)`.

State and persistence: all state is in mocks and an in-memory response buffer. No server is started and no files are written.

Dependencies and integration points: validates the servlet contract consumed by HTTP health/readiness probes for HA-aware services.

Risks: direct servlet invocation avoids container behavior, so it only tests servlet method logic and response interactions.

Test signals: confirms active requests produce the expected response body and inactive requests return method-not-allowed with the expected message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/TestIsActiveServlet.java -->
