# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/web/CORSFilter.java

## Purpose
`CORSFilter` adds configured CORS response headers to Alluxio web responses when CORS is enabled.

## Important APIs, Types, and Functions
It extends `HttpFilter` and overrides `doFilter(HttpServletRequest, HttpServletResponse, FilterChain)`. It reads `WEB_CORS_*` configuration keys and uses `StringUtils.equals()` to decide whether to add `Vary: Origin`.

## Control Flow, State, and Persistence
For each request, if `WEB_CORS_ENABLED` is true, it reads allowed origins, methods, headers, exposed headers, credential flag, and max age from global configuration, sets corresponding `Access-Control-*` headers, conditionally sets `Vary`, then always continues the filter chain. It stores no state.

## Dependencies and Integration Points
It depends on Alluxio configuration, `HttpFilter`, and servlet filters. `WebServer` installs it for all dispatcher types on `/*`.

## Risks and Test Signals
Risks include permissive wildcard origins, credentials with wildcard origin if configured, repeated `Vary` headers, and runtime global config reads per request. Signals are headers present only when enabled, `Vary` when origins are not `*`, and filter-chain continuation.
