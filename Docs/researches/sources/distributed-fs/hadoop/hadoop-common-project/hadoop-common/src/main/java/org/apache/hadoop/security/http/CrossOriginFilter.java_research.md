# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/CrossOriginFilter.java

## Purpose

`CrossOriginFilter` is Hadoop's servlet CORS filter. It validates request origin, requested method, and requested headers against init-parameter allowlists, then emits CORS response headers when checks pass.

## Important APIs, Types, and Functions

The filter defines init params `allowed-origins`, `allowed-methods`, `allowed-headers`, and `max-age` with defaults. Core methods are `init`, `doFilter`, `destroy`, `doCrossFilter`, `encodeHeader`, `areOriginsAllowed`, `isMethodAllowed`, and `areHeadersAllowed`.

## Control Flow

Initialization splits comma-separated config values and detects `*` origin allowance. `doFilter` calls `doCrossFilter` and always continues the chain. `doCrossFilter` sanitizes `Origin` against CR/LF response splitting, returns without setting CORS headers for non-CORS, disallowed origins, methods, or headers, and otherwise sets `Access-Control-Allow-*` headers.

## State and Persistence Behavior

Allowed methods, headers, origins, `allowAllOrigins`, and `maxAge` are in-memory filter instance state. `destroy` clears the lists. No persistent state is written.

## Dependencies and Integration Points

It depends on the Servlet API, Apache Commons `StringUtils`, regex `Pattern`, SLF4J, and Hadoop test visibility annotations. Hadoop HTTP servers add it through filter initializers.

## Risks and Edge Cases

Legacy wildcard patterns without the `regex:` prefix are still accepted but discouraged. Header and method comparisons are case-sensitive. Multiple origins are split on whitespace. The filter does not reject requests; it only omits CORS headers. Regex patterns are compiled during request checks, so complex configs can add per-request cost.

## Test Signals

Tests should cover null origin, CR/LF header sanitization, wildcard origins, exact origins, `regex:` origins, legacy wildcard warnings, requested method/header denial, response header values, and destroy clearing.
