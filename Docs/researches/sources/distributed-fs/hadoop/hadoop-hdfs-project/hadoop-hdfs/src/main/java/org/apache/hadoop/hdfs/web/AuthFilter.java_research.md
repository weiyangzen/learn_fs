<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilter.java

## Purpose
`AuthFilter` customizes Hadoop HTTP proxy-user authentication for WebHDFS by allowing delegation-token URL authentication to bypass Kerberos authentication.

## APIs and Types
It extends `ProxyUserAuthenticationFilter` and overrides `doFilter(ServletRequest, ServletResponse, FilterChain)`.

## Control Flow
`doFilter` wraps the request with `ProxyUserAuthenticationFilter.toLowerCase`, reads the `delegation` query parameter by `DelegationParam.NAME`, and checks that the servlet path starts with `WebHdfsFileSystem.PATH_PREFIX`. When both are true, it delegates directly to the downstream filter chain with the lower-cased request and returns. Otherwise it invokes the superclass filter.

## State and Persistence
The filter has no added state and no persistence. Authentication state is managed by the superclass and downstream token handling.

## Dependencies and Integration
It depends on servlet APIs, `DelegationParam`, `WebHdfsFileSystem`, and Hadoop authentication server filters. It is installed by `AuthFilterInitializer`.

## Risks
The bypass relies on downstream WebHDFS code validating the delegation token; this filter only skips Kerberos. Request lower-casing may affect parameter/path handling consistently with proxy-user filter expectations. Path prefix matching must not overmatch unintended servlets.

## Test Signals
Tests should cover delegation token on WebHDFS path bypassing superclass auth, delegation token on non-WebHDFS path not bypassing, no token path, lower-case wrapper behavior, and interaction with proxy-user parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/web/AuthFilter.java -->
