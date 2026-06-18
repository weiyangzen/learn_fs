# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/resources/webapps/webhdfs/WEB-INF/web.xml

## Purpose
This deployment descriptor packages the HttpFS web application under a `/webhdfs/*` servlet mapping for the resource-style webapp layout.

## Important APIs, Types, and Functions
It declares listener `org.apache.hadoop.fs.http.server.HttpFSServerWebApp`, Jersey servlet `org.glassfish.jersey.servlet.ServletContainer`, provider packages `org.apache.hadoop.fs.http.server, org.apache.hadoop.lib.wsrs`, servlet mapping `/webhdfs/*`, and filters `HttpFSAuthenticationFilter`, `MDCFilter`, `HostnameFilter`, `CheckUploadContentTypeFilter`, and `HttpFSReleaseFilter`.

## Control Flow
On webapp startup the listener initializes HttpFS services. Requests under `/webhdfs/*` are routed to Jersey after passing through all mapped filters in descriptor order: auth, MDC, hostname, upload content-type check, filesystem release.

## State and Persistence
The descriptor itself is static. It causes servlet container state to include one listener, one Jersey servlet, and filter instances.

## Dependencies and Integration Points
It integrates HttpFS server resources with the generic lib wsrs providers. The filter chain connects authentication, logging context, upload validation, and filesystem lifecycle cleanup. Tests create Jetty `WebAppContext(url.getPath(), "/webhdfs")`, matching this path style.

## Risks
`MDCFilter` is declared before `HostnameFilter`, so MDC hostname population may not occur despite the filter's documented dependency. `url-pattern>*</url-pattern>` is used for filters under a Servlet 2.4 descriptor; deployment behavior should be verified across containers. Provider package scanning must include both server resources and generic JSON/exception providers.

## Test Signals
`BaseTestHttpFSWith.createHttpFSServer` and `TestHttpFSAccessControlled.createHttpFSServer` load the `webapp` resource into Jetty at context `/webhdfs`, exercising this descriptor's listener, servlet, and filters.
