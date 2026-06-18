<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilterInitializer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilterInitializer.java

## Purpose
`AuthFilterInitializer` builds and registers the servlet filter configuration for HDFS WebHDFS authentication using `AuthFilter`.

## APIs and Types
It extends `FilterInitializer`. Constructor sets the config prefix to `hadoop.http.authentication.`. `createFilterConfig(Configuration)` is protected for testing/extension, and `initFilter(FilterContainer, Configuration)` registers the filter.

## Control Flow
`createFilterConfig` starts with `AuthenticationFilterInitializer.getFilterConfigMap`, copies proxy-user configuration entries from `hadoop.proxyuser.*` into filter keys prefixed with `proxyuser`, defaults the auth type to Kerberos when UGI security is enabled or pseudo otherwise, sets cookie path to `/`, and returns the map. `initFilter` adds `AuthFilter` by name and class to the provided container.

## State and Persistence
State is the config prefix string. No persistence. Runtime behavior depends on global `UserGroupInformation.isSecurityEnabled()`.

## Dependencies and Integration
It depends on Hadoop HTTP filter container APIs, security authentication initializers, UGI, `ProxyUsers`, Kerberos and pseudo authentication handler constants, and `AuthFilter`.

## Risks
The default auth type is determined at initialization time from UGI global state, so tests and embedded servers must configure UGI before calling it. Proxy-user key rewriting is string-based and must match authentication filter expectations. Cookie path `/` affects all server paths.

## Test Signals
Tests should verify inherited auth config copying, proxy-user entry translation, Kerberos versus pseudo defaulting, preservation of explicit type, cookie path setting, and `FilterContainer.addFilter` parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilterInitializer.java -->
