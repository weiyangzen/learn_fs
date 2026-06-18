# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/authentication/server/ProxyUserAuthenticationFilterInitializer.java

Purpose: Hadoop HTTP `FilterInitializer` that installs `ProxyUserAuthenticationFilter` with both normal authentication settings and proxy-user authorization settings.

Important APIs/types/functions: constructor sets `configPrefix` to `hadoop.http.authentication.`. `createFilterConfig` starts from `AuthenticationFilterInitializer.getFilterConfigMap` and then copies properties under `ProxyUsers.CONF_HADOOP_PROXYUSER`, prefixing each with `proxyuser`. `initFilter` adds the filter to the container under name `ProxyUserAuthenticationFilter`.

Control flow: at HTTP server startup, Hadoop calls `initFilter`; configuration map is built once and passed to the servlet filter. The filter later reconstructs proxyuser config from init params.

State/persistence: only instance `configPrefix`; no persistence.

Dependencies/integration: Hadoop HTTP `FilterContainer`, `FilterInitializer`, `AuthenticationFilterInitializer`, `ProxyUsers`, and `ProxyUserAuthenticationFilter`.

Risks: prefix composition must preserve expected `proxyuser.<name>.<setting>` keys; mistakes can silently disable proxy authorization. This initializer always uses default Hadoop HTTP auth prefix and does not expose a constructor override. Test signals include config map contents for auth and proxy settings, filter name/class registration, and round trip with `ProxyUserAuthenticationFilter.getProxyuserConfiguration`.
