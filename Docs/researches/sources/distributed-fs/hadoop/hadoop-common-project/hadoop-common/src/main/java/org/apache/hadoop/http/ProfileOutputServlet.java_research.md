<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileOutputServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileOutputServlet.java

Purpose: servlet that serves async-profiler output files and auto-refreshes while a profile result is still being written.

Important APIs, types, and functions: `doGet()` checks `HttpServer2.isInstrumentationAccessAllowed()`, resolves the requested path using servlet context real path, treats files smaller than 100 bytes as incomplete, emits a `Refresh` header, and otherwise delegates to Jetty `DefaultServlet`. `sanitize()` permits only alphanumeric, percent, equals, ampersand, dot, and hyphen characters in query strings.

Control flow: profiler requests first return from `ProfileServlet` with a redirect to `/prof-output-hadoop/<file>`. This servlet then polls the output file until it is large enough and serves it.

State and persistence: no servlet state. It reads files in `ProfileServlet.OUTPUT_DIR`, which are persistent temporary profiler artifacts.

Dependencies and integration points: integrates with `HttpServer2` instrumentation ACLs, `ProfileServlet` response headers, and Jetty static serving.

Risks and test signals: `getRealPath()` and file length checks depend on Jetty context configuration. Query sanitization throws runtime exceptions for unexpected characters. Tests should cover unauthorized access, incomplete-output refresh, query sanitization acceptance/rejection, and final static file serving.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/ProfileOutputServlet.java -->
