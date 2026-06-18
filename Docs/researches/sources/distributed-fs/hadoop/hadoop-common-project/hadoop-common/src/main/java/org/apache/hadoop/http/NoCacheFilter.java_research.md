<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/NoCacheFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/NoCacheFilter.java

Purpose: servlet filter that prevents client/proxy caching for Hadoop web responses.

Important APIs, types, and functions: `doFilter()` casts the response to `HttpServletResponse`, sets `Cache-Control: no-cache`, adds current `Expires` and `Date` headers, adds `Pragma: no-cache`, and continues the filter chain. `init()` and `destroy()` are no-ops.

Control flow: installed by `HttpServer2.addNoCacheFilter()` on root, static, logs, and added contexts. It mutates headers before downstream servlets run.

State and persistence: stateless.

Dependencies and integration points: depends on servlet filter APIs and `HttpServer2` context setup.

Risks and test signals: assumes HTTP responses, so non-HTTP servlet responses would fail class cast. Tests should verify headers, chain invocation, and behavior when downstream servlet overwrites cache headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/http/NoCacheFilter.java -->
