# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilter.java

Purpose: servlet authentication filter extension that supports Hadoop proxy-user `doAs` query parameter semantics after base HTTP authentication.

Important APIs/types/functions: `init` extracts proxyuser config and refreshes `ProxyUsers`. `doFilter` lowercases request parameters, reads `doas`, creates remote and proxy UGIs, authorizes with `ProxyUsers.authorize`, and wraps request remote user/principal on success. `getProxyuserConfiguration` copies filter init params with `proxyuser.` prefix. `toLowerCase` wraps requests when parameter names contain uppercase characters. `containsUpperCase` supports that normalization.

Control flow: initialize proxy authorization config before `AuthenticationFilter` init. Per request, if `doas` exists and differs from remote user, and a user principal exists, build real-user UGI from remote user, wrap effective doAs user, authorize against remote address, then pass a request wrapper reporting effective user. Authorization failure sends HTTP 403 and stops. Finally calls `super.doFilter`.

State/persistence: no fields; proxy authorization state is maintained by `ProxyUsers` static configuration.

Dependencies/integration: Hadoop auth `AuthenticationFilter`, servlet API, `ProxyUsers`, `UserGroupInformation`, `AuthorizationException`, `HttpExceptionUtils`, and HTTP filter initializer config.

Risks: lowercasing can merge distinct parameter names and preserves all values under the lower-case key; doAs only applies when authenticated remote principal exists; remote address trust depends on servlet/container proxy configuration; request wrapper principal returns full proxy UGI user while remote user returns short name. Test signals include uppercase `DoAs`, duplicate case-folded params, self-doAs no-op, missing principal, forbidden proxy user, successful wrapper values, and config extraction.
