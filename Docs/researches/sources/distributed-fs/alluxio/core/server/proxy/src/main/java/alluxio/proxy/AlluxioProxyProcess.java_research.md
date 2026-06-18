# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyProcess.java

## Purpose
`AlluxioProxyProcess` implements the runtime proxy process. It starts the proxy web server, registers the runtime web port, creates a heartbeat executor to the primary master, and blocks until stopped.

## Important APIs, Types, and Functions
The process implements `ProxyProcess` methods `start`, `stop`, `waitForReady`, `getStartTimeMs`, `getUptimeMs`, and `getWebLocalPort`. It owns a `WebServer`, `ProxyMasterSync`, single-thread executor, start timestamp, and a `CountDownLatch`.

## Control Flow, State, and Persistence
`start` creates a `ProxyWebServer` bound to the configured proxy web address, writes the actual local port back to `PropertyKey.PROXY_WEB_PORT`, builds a proxy `NetAddress`, starts the web server, creates `ProxyMasterSync`, submits a heartbeat thread using `PROXY_MASTER_HEARTBEAT_INTERVAL`, and then waits on `mLatch`. `stop` stops the web server, closes master sync, shuts down the heartbeat executor, and releases the latch. `waitForReady` polls the REST `paths/%2f/exists` endpoint using Apache HttpClient until it receives HTTP 200 or times out.

## Dependencies and Integration Points
This class integrates Jetty-based `ProxyWebServer`, Alluxio networking utilities, master client context, heartbeat framework, proxy REST handlers, and process lifecycle management. It also updates global configuration with the effective web port.

## Risks
`start` blocks until `stop`, so callers must run it through the Alluxio process runner or a separate thread. `waitForReady` creates an HTTP client on each poll and depends on the filesystem REST handler being available and root existence checks succeeding. `stop` sets fields to null and is not synchronized, matching the class's not-thread-safe annotation.

## Test Signals
Useful signals are process lifecycle tests that start and stop the proxy, verify the REST readiness endpoint, assert heartbeat thread creation, and confirm the web port is released on stop.
