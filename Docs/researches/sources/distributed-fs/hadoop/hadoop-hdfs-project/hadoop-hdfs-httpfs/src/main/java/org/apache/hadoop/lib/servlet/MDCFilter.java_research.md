# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/MDCFilter.java

## Purpose
`MDCFilter` populates SLF4J mapped diagnostic context for HttpFS request logs with request hostname, authenticated user, HTTP method, and path.

## Important APIs, Types, and Functions
The class implements `Filter` and uses `org.slf4j.MDC`. It casts the generic `ServletRequest` to `HttpServletRequest`, reads `getUserPrincipal()`, `getMethod()`, and `getPathInfo()`, and consults `HostnameFilter.get()`.

## Control Flow
Before the downstream chain runs, `doFilter` clears any stale MDC entries, conditionally adds `hostname` and `user`, always adds `method`, conditionally adds `path`, and delegates. The `finally` block clears MDC again.

## State and Persistence
State is log-context state scoped to the current request thread. Nothing is persisted directly, but downstream log lines can include the MDC values if the logging pattern is configured to do so.

## Dependencies and Integration Points
It depends on servlet HTTP requests, `HostnameFilter`, and SLF4J. It is registered in both HttpFS web descriptors and sits in the same filter chain as authentication, upload content checking, and filesystem release.

## Risks
The filter assumes every request is an `HttpServletRequest`; a non-HTTP request would throw `ClassCastException`. Since web descriptors map `MDCFilter` before `hostnameFilter`, the `hostname` field may be absent despite the Javadoc saying it appears if `HostnameFilter` is configured before this filter. Clearing all MDC state can erase context set by earlier filters in the same request.

## Test Signals
Direct tests outside this subset (`TestMDCFilter`) validate MDC population and cleanup. The subset web descriptors confirm the production registration and filter order risk.
