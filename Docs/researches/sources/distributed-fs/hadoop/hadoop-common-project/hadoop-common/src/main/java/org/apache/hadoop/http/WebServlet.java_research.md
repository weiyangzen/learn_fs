<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/WebServlet.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/WebServlet.java

Purpose: Hadoop static-content servlet that redirects root webapp requests to `index.html` while preserving safe query strings.

Important APIs, types, and functions: `doGet()` checks whether `request.getRequestURI().equals("/")`. For root, it builds a redirect to `index.html`, appends the query string after removing CR/LF to prevent response splitting, and sends the redirect. Other paths delegate to Jetty `DefaultServlet`.

Control flow: this servlet is the root servlet in the main webapp context and also serves `/static` resources. Root redirects help SPNEGO and impersonation flows reach the actual page asset.

State and persistence: stateless. Static files are served from configured webapp resource bases.

Dependencies and integration points: depends on Jetty default servlet and `HttpServer2` webapp context setup.

Risks and test signals: query strings are not HTML-escaped here, only CR/LF-stripped for redirect safety. Tests should cover root redirect, query preservation/sanitization, non-root static serving, and interaction with authentication filters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/WebServlet.java -->
