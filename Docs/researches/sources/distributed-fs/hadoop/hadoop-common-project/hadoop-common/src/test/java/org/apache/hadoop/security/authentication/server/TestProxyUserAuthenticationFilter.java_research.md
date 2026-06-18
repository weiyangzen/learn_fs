# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/security/authentication/server/TestProxyUserAuthenticationFilter.java

Purpose: verifies that `ProxyUserAuthenticationFilter` honors the `doas` request parameter for a configured proxy user and exposes the proxied user as `HttpServletRequest.getRemoteUser` to downstream filters.

Important APIs and types: `ProxyUserAuthenticationFilter`, `AuthenticationFilter`, `FilterConfig`, `FilterChain`, `HttpServletRequest`, `HttpServletResponse`, servlet context attributes, Mockito, and AssertJ.

Control flow: a dummy `FilterConfig` provides `proxyuser.knox.users=testuser`, `proxyuser.knox.hosts=127.0.0.1`, and `type=simple`, plus a mocked servlet context without a signer secret provider. A custom `FilterChain` records `request.getRemoteUser()`. The mocked request returns remote user `knox`, parameter `doas=testuser`, remote address `127.0.0.1`, and principal `knox@EXAMPLE.COM`. After filter initialization and `doFilter`, the test asserts the chain saw `testuser`.

State and persistence: stores `actualUser` in the test instance. No files are written. Filter initialization may touch static proxy-user configuration through Hadoop auth internals.

Dependencies and integration points: integrates Hadoop auth filter setup, proxy-user authorization configuration, servlet API wrappers, and simple authentication mode.

Risks: test only covers the successful path, not unauthorized `doas`, missing principal, or failed host matching. The response stub is mostly no-op, so error/status behavior is not verified.

Test signals: focused signal that a valid proxy request is wrapped so downstream code sees the effective user rather than the real authenticated proxy.
