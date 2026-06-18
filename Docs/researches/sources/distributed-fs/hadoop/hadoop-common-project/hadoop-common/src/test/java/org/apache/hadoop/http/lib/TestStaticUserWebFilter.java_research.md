<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/lib/TestStaticUserWebFilter.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/lib/TestStaticUserWebFilter.java

## Purpose
Unit tests for `StaticUserWebFilter`, which wraps HTTP requests so web UIs can expose a configured static user principal when no authentication is active.

## Important APIs, Types, and Functions
Uses Mockito `FilterConfig`, `FilterChain`, `HttpServletRequest`, `ServletResponse`, and `ArgumentCaptor<HttpServletRequestWrapper>`. `mockConfig()` returns a config whose `HADOOP_HTTP_STATIC_USER` init parameter is the requested username. Tests call `StaticUserFilter.init`, `doFilter`, and `destroy`, and call `StaticUserWebFilter.getUsernameFromConf`.

## Control Flow and State
`testFilter()` initializes the filter with `myuser`, invokes it with mocked request/response, captures the wrapped request sent to the chain, and asserts both `getUserPrincipal().getName()` and `getRemoteUser()` return `myuser`. Configuration tests check legacy `dfs.web.ugi` parsing and modern `hadoop.http.staticuser.user` behavior.

## Dependencies and Integration Points
Integrates Hadoop `CommonConfigurationKeys`, servlet filter chain contracts, and Mockito. It validates backward compatibility with the historical `dfs.web.ugi` format used by older HDFS web UI code.

## Risks and Test Signals
Risk centers on preserving legacy config parsing and ensuring wrapper identity is passed down the chain. The test signals are captured wrapper values and direct username extraction from `Configuration`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/http/lib/TestStaticUserWebFilter.java -->
