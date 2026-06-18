# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/webapp/WEB-INF/web.xml

## Purpose
This is the main HttpFS WAR deployment descriptor. It maps Jersey to the whole webapp path (`/*`) rather than the nested `/webhdfs/*` pattern used by the alternate resources descriptor.

## Important APIs, Types, and Functions
It declares `HttpFSServerWebApp` as listener, Jersey `ServletContainer` with provider packages `org.apache.hadoop.fs.http.server, org.apache.hadoop.lib.wsrs`, servlet mapping `/*`, and the same auth, MDC, hostname, upload-content-type, and filesystem-release filters.

## Control Flow
Servlet startup initializes the server listener and eagerly loads the Jersey servlet. All requests routed to the webapp run through the filter chain and then Jersey resource dispatch.

## State and Persistence
The descriptor creates container-managed listener/servlet/filter instances. It persists nothing directly.

## Dependencies and Integration Points
It is the production-style webapp descriptor for the HttpFS WAR. It binds the generic servlet filters and wsrs providers to the server resources scanned by Jersey.

## Risks
The same filter-order issue exists as in the alternate descriptor: `MDCFilter` precedes `HostnameFilter`. Mapping Jersey to `/*` means static resources or default servlet behavior must be considered if added later. Filter URL pattern syntax should be validated for target containers.

## Test Signals
The tests load `webapp` from the classpath into Jetty; depending on build resource layout this descriptor is the active one for the compatibility matrix.
