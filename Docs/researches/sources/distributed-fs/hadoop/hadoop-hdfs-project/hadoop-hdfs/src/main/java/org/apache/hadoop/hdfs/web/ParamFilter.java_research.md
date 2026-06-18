# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/ParamFilter.java

## Purpose

`ParamFilter.java` is a servlet filter that makes HTTP request parameter names case-insensitive for WebHDFS by wrapping `HttpServletRequest` and lower-casing every parameter name. The source was read as a complete 96-line file for this report.

## Important APIs, Types, and Functions

The public type is `ParamFilter implements Filter`. The key runtime method is `doFilter(ServletRequest, ServletResponse, FilterChain)`, which wraps only `HttpServletRequest` instances. The private nested `CustomHttpServletRequestWrapper` extends `HttpServletRequestWrapper` and overrides `getParameter`, `getParameterMap`, `getParameterNames`, and `getParameterValues`.

## Control Flow

`init` and `destroy` are no-ops. During `doFilter`, non-HTTP requests pass through unchanged. HTTP requests are wrapped before being passed to the rest of the filter chain. The wrapper snapshots `request.getParameterMap()` in its constructor, inserts each entry under `entry.getKey().toLowerCase()`, then answers all parameter lookups through that lower-case map. `getParameter` delegates to `getParameterValues` and returns the first value.

## State and Persistence Behavior

The filter has no persistent state. Each request wrapper owns a per-request `HashMap<String,String[]>` of lower-cased parameter names to the original value arrays. The map returned to callers is unmodifiable, but the underlying arrays are the original arrays from the servlet container and are not copied.

## Dependencies and Integration Points

It depends on the servlet `Filter` API and `HttpServletRequestWrapper`. It integrates with WebHDFS resource parameter parsing so parameters like `OP`, `op`, and mixed-case names are accepted as the same logical parameter.

## Risks and Edge Cases

If a request contains two parameters whose names differ only by case, the later iteration order from the servlet container overwrites the earlier entry in `lowerCaseParams`; that order is not guaranteed. `String.toLowerCase()` uses the default JVM locale, so unusual locales can theoretically affect ASCII parameter names; using `Locale.ROOT` would be more deterministic. The wrapper lowercases lookup names without null checks, so `getParameterValues(null)` throws `NullPointerException`.

## Test Signals

Tests should cover mixed-case WebHDFS operation parameters, duplicate case-colliding parameters, non-HTTP pass-through behavior, unmodifiable parameter maps, and locale-sensitive lower-casing behavior under a non-English default locale.
