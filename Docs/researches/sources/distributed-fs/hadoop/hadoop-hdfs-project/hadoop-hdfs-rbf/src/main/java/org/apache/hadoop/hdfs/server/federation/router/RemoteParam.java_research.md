# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/RemoteParam.java

## Purpose
`RemoteParam` is a placeholder for a parameter whose value depends on the remote location being invoked. It supports default destination-path mapping and explicit per-location map lookup.

## Important APIs, Types, And Functions
- The no-arg constructor creates a default parameter that resolves to `context.getDest()`.
- The map constructor stores a `Map<? extends RemoteLocationContext, ? extends Object>` used to look up context-specific values.
- `getParameterForContext(RemoteLocationContext)` returns null for null context, map lookup value when a map exists, or destination path by default.
- `toString` exposes the map for diagnostics.

## Control Flow
Resolution is a simple three-way branch: no context, map-backed context, or default destination. The class does not validate map completeness.

## State And Persistence
The instance stores an optional map reference. There is no defensive copy and no persistence, so external mutations to the map can affect later parameter resolution.

## Dependencies And Integration Points
It depends on `RemoteLocationContext` and is consumed by `RemoteMethod`. Router modules use it when forwarding path-like parameters, cache directive info, and quota paths to subclusters.

## Risks And Edge Cases
Missing map entries resolve to null and may produce downstream RPC failures. Default mapping ignores source path and always uses destination. Mutable maps can introduce race-prone behavior if shared across concurrent invocations.

## Test Signals
Behavior is indirectly covered by router RPC tests that verify operations reach destination paths, plus cache admin and quota tests where `RemoteMethod` uses `RemoteParam` to rewrite paths.
