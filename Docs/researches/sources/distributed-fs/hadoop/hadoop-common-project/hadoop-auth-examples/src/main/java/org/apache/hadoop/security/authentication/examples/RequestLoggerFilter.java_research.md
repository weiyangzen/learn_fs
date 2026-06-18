# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-auth-examples/src/main/java/org/apache/hadoop/security/authentication/examples/RequestLoggerFilter.java

Purpose: servlet filter for the Hadoop Auth examples that logs HTTP request and response status/headers when debug logging is enabled.

Important APIs, types, and functions: implements `Filter` with no-op `init()`/`destroy()` and debug-aware `doFilter()`. `XHttpServletRequest.getResquestInfo()` formats method, URL, query string, and request headers. `XHttpServletResponse` wraps response mutation methods to track status, message, cookies, and headers, then `getResponseInfo()` formats them after the chain returns.

Control flow: when debug is disabled, the filter delegates directly. When enabled, it wraps request/response, logs request data, invokes the chain, and logs response data in a `finally` block.

State and persistence: per-request wrapper state stores captured headers/status in memory. No persistent state.

Dependencies and integration points: depends on servlet APIs and SLF4J. Registered first in the example `web.xml` so it observes traffic before auth filters and servlet handling.

Risks and test signals: debug logs may expose authentication headers or cookies. Header capture is incomplete for response APIs not overridden. `getResquestInfo` has a misspelled method name but is internal. Test signals are example deployment with debug logging, response header/status capture for success and error paths, and no wrapping overhead when debug is off.
