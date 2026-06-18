# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/AuthenticationFilterInitializer.java


Purpose: `AuthenticationFilterInitializer` wires Hadoop HTTP servers to hadoop-auth's `AuthenticationFilter` for pseudo, anonymous, and Kerberos/SPNEGO HTTP authentication.

Important APIs and types: `initFilter(FilterContainer, Configuration)` builds a filter config map and registers the filter named `authentication`. `getFilterConfigMap()` copies all `hadoop.http.authentication.` properties after stripping the prefix, sets cookie path to `/`, and resolves Kerberos `_HOST` principals.

Control flow and state: The initializer is stateless. At initialization time it collects configuration, resolves `KerberosAuthenticationHandler.PRINCIPAL` through `SecurityUtil.getServerPrincipal()` using `HttpServer2.BIND_ADDRESS`, and throws a runtime exception if principal resolution fails.

Dependencies and integration: It depends on `FilterContainer`, `FilterInitializer`, hadoop-auth `AuthenticationFilter`, `KerberosAuthenticationHandler`, `HttpServer2`, and `SecurityUtil`. The output map becomes servlet filter init parameters.

Risks and test signals: Tests should verify prefix stripping, cookie path injection, `_HOST` substitution, and error wrapping when bind-address principal resolution fails. Misconfigured principals fail at web server startup rather than per request.
