# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ConfServlet.java

Purpose: HTTP servlet that exposes the running daemon `Configuration` as XML or JSON, optionally for a single property. It is used by Hadoop web UIs and instrumentation endpoints. The source was read as a complete 120-line Java file.

Important APIs/functions: class `ConfServlet extends HttpServlet`; constants `FORMAT_JSON` and `FORMAT_XML`; private `getConfFromContext()`; servlet method `doGet`; testing-visible `parseAcceptHeader`; static `writeResponse(Configuration, Writer, String, String)` and overload without property name; nested `BadFormatException`.

Control flow: `doGet` first asks `HttpServer2.isInstrumentationAccessAllowed`; denied access returns immediately. It chooses JSON when the Accept header contains `json`, otherwise XML. It sets the content type, reads optional request parameter `name`, obtains the response writer, and calls `writeResponse`. `writeResponse` delegates JSON to `Configuration.dumpConfiguration` and XML to `conf.writeXml`; bad format produces HTTP 400 and an unknown property path can produce HTTP 404 via `IllegalArgumentException`.

State and persistence: the servlet reads the `Configuration` stored in the servlet context under `HttpServer2.CONF_CONTEXT_ATTRIBUTE`. It does not mutate configuration or persist data; it writes a transient HTTP response.

Dependencies and integration: integrates with Hadoop `HttpServer2`, servlet APIs, Hadoop `Configuration`, shaded Guava `HttpHeaders`, and web UI/instrumentation access controls. It is limited-private to HDFS and MapReduce and marked unstable.

Risks: Accept negotiation is simplistic and treats any header containing `json` as JSON. Configuration exposure must rely on `HttpServer2` access checks and `Configuration` redaction behavior to avoid leaking secrets. The code obtains a writer before handling some errors and closes it after `sendError`, so servlet-container behavior should be covered by tests.

Test signals: unit tests for Accept parsing, XML and JSON response generation, property filtering by `name`, bad-format handling through `writeResponse`, 404 behavior for missing properties, and web server integration tests for instrumentation ACL enforcement and redaction.
