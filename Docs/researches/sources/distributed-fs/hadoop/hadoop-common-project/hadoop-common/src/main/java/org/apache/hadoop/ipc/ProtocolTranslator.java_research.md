# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/ProtocolTranslator.java

## Purpose
`ProtocolTranslator` marks client-side translators that wrap an underlying RPC proxy and can expose that proxy for connection and lifecycle operations.

## Important APIs, Types, and Functions
`getUnderlyingProxyObject()` returns the real dynamic proxy object.

## Control Flow
`RPC.getConnectionIdForProxy` checks this interface and unwraps translators before reading the `RpcInvocationHandler`.

## State and Persistence Behavior
The interface has no state. Implementations hold whatever proxy state they wrap.

## Dependencies and Integration Points
It integrates with translator classes generated or hand-written around protobuf services, and with `RPC.stopProxy`/connection-id helper paths.

## Risks and Test Signals
Risks include returning the wrong object or a non-RPC proxy, breaking connection reuse and protocol metadata queries. Tests should cover translator unwrapping and proxy shutdown.
