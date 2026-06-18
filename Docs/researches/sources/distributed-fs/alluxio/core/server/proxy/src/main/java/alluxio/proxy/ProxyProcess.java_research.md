# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyProcess.java

## Purpose
`ProxyProcess` defines the process contract for an Alluxio proxy. It extends the common Alluxio `Process` lifecycle with proxy-specific runtime metadata.

## Important APIs, Types, and Functions
The interface adds `getStartTimeMs`, `getUptimeMs`, and `getWebLocalPort`. The nested `Factory.create` method returns a new `AlluxioProxyProcess`.

## Control Flow, State, and Persistence
The interface has no implementation state. The factory is a simple construction point used by `AlluxioProxy.main`. Concrete state and lifecycle live in `AlluxioProxyProcess`.

## Dependencies and Integration Points
It integrates the proxy module with the shared Alluxio `Process` abstraction and gives REST handlers a stable type for querying process metadata.

## Risks
The factory hard-codes `AlluxioProxyProcess`, so tests or alternative process implementations need mocking or code changes rather than dependency injection. `getWebLocalPort` is documented as unit-test oriented but is part of the public interface.

## Test Signals
Signals are compile-time usage by the proxy process and runtime tests that `Factory.create` returns a functioning `AlluxioProxyProcess`.
