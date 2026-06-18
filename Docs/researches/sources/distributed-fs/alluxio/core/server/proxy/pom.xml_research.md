# sources/distributed-fs/alluxio/core/server/proxy/pom.xml

## Purpose
This POM defines the `alluxio-core-server-proxy` jar module. It declares dependencies for the Alluxio proxy service and configures Swagger documentation generation for the proxy REST API.

## Important APIs, Types, and Functions
The artifact is `org.alluxio:alluxio-core-server-proxy` with packaging `jar`. External dependencies include Jackson XML, Guava, commons-io, servlet API, Apache HttpClient/Core, Jetty, Jersey server/servlet/HK2/Jackson media, and Kerby utility. Internal dependencies are `alluxio-core-common`, `alluxio-core-client-fs`, and `alluxio-core-server-common`. The Swagger plugin scans `AlluxioProxyRestServiceHandler`, `PathsRestServiceHandler`, and `StreamsRestServiceHandler`.

## Control Flow, State, and Persistence
The file has no runtime control flow. Maven resolves dependencies, builds the proxy jar, and can generate REST docs under `generated/proxy/index.html` and `generated/proxy/swagger-ui` using a shared template.

## Dependencies and Integration Points
The POM connects the proxy Java sources to Jetty/Jersey REST hosting, XML serialization for S3 models, filesystem client APIs, and server common utilities. The Swagger documentation block depends on class annotations and endpoint constants in the proxy REST handlers.

## Risks
REST behavior depends on compatible Jersey, Jackson, Jetty, and servlet versions inherited from parent dependency management. Moving handler packages without updating Swagger locations would silently omit API docs. The `build.path` relative expression is specific to this module depth.

## Test Signals
Useful signals are `mvn -pl core/server/proxy test`, compilation of proxy sources, and Swagger generation verification that the proxy, paths, and streams endpoints appear in generated docs.
