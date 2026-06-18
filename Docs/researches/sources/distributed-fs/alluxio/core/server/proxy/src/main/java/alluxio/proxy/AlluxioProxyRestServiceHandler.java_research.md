# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyRestServiceHandler.java

## Purpose
`AlluxioProxyRestServiceHandler` exposes general proxy process information through the REST API under `/proxy`. It returns runtime version, uptime, start time, and configuration values.

## Important APIs, Types, and Functions
The main endpoint is `GET /proxy/info`, implemented by `getInfo(Boolean rawConfiguration)`. It returns `AlluxioProxyInfo`. The query parameter `raw_configuration` controls whether raw or display configuration values are returned. `getConfigurationInternal` builds a sorted map from `Configuration.toMap`.

## Control Flow, State, and Persistence
The constructor retrieves `ProxyProcess` from the servlet context using `ProxyWebServer.ALLUXIO_PROXY_SERVLET_RESOURCE_KEY`. `getInfo` normalizes a null query value to false, then builds the response inside `RestUtils.call`. There is no local mutable state beyond the process reference.

## Dependencies and Integration Points
The handler integrates Jersey annotations, Swagger annotations, `RestUtils`, global configuration, `RuntimeConstants.VERSION`, `AlluxioProxyInfo`, and servlet-context resource injection from `ProxyWebServer`.

## Risks
The endpoint can expose a large configuration map; raw values may reveal unresolved or sensitive configuration if callers are authorized to access it. The handler assumes the servlet context contains a valid `ProxyProcess`. It has no field-selection mechanism.

## Test Signals
Signals include REST tests for `/proxy/info`, raw and display configuration modes, and verification that start time, uptime, and version are populated from the process.
