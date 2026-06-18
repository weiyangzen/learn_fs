# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/IsRouterActiveServlet.java

## Purpose
`IsRouterActiveServlet` exposes the router readiness decision through Hadoop's generic `IsActiveServlet`. It answers whether the Router HTTP service should report itself active and ready to serve requests.

## Important APIs, Types, And Functions
- `isActive()` obtains the `ServletContext`, retrieves the `Router` via `RouterHttpServer.getRouterFromContext`, reads `Router.getRouterState()`, and returns true only for `RouterServiceState.RUNNING`.

## Control Flow
The servlet delegates all context lookup and state ownership to `RouterHttpServer` and `Router`. There is no request-specific branching beyond comparing the current state to `RUNNING`.

## State And Persistence
The servlet stores no state. It reflects the in-memory router state at the instant the servlet method executes.

## Dependencies And Integration Points
It depends on Hadoop HTTP's `IsActiveServlet`, the router object stored in servlet context by `RouterHttpServer`, and the `RouterServiceState` lifecycle enum. Load balancers and health check clients can use this endpoint to avoid routing to routers in initializing, safemode, shutdown, or unavailable states.

## Risks And Edge Cases
If the servlet context does not contain a router, or the router is not fully initialized, this method can fail rather than returning false. The active decision is intentionally strict: safemode is not active even though the HTTP server may be alive. Tests should verify this against router lifecycle transitions instead of only HTTP process liveness.

## Test Signals
Router lifecycle and HTTP tests, including `TestRouter`, `TestRouterSafemode`, and router HTTP server tests, provide indirect coverage. Health-check behavior should be validated by driving router state transitions and confirming only `RUNNING` produces an active response.
