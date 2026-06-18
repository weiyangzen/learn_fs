# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RpcEngine.java

## Purpose
`RpcEngine` is the pluggable interface between the `RPC` facade and concrete serialization/transport implementations.

## Important APIs, Types, and Functions
It declares proxy creation by address or `ConnectionId`, proxy creation with auth fallback and alignment context, server construction, and `getProtocolMetaInfoProxy` for metadata queries reusing a connection id.

## Control Flow
`RPC` resolves an engine from configuration and delegates client/server construction. Implementations such as `ProtobufRpcEngine2` create dynamic proxies, clients, and servers.

## State and Persistence Behavior
The interface has no state. Implementations may maintain client caches or protocol registration state in memory.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `RetryPolicy`, `Client.ConnectionId`, UGI, token secret managers, socket factories, and `AlignmentContext`.

## Risks and Test Signals
Risks include incomplete implementation of newer overloads, inconsistent auth/alignment handling, and metadata proxy misuse. Tests should exercise all overload paths for each engine.
