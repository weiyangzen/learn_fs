# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ipc/RPC.java

## Purpose
`RPC` is the central facade for Hadoop IPC. It defines RPC kinds, protocol naming/versioning helpers, client proxy construction, proxy shutdown, server construction, version mismatch exceptions, and the `RPC.Server` base that maps protocol/version pairs to implementations.

## Important APIs, Types, and Functions
`RpcKind` encodes builtin/writable/protobuf wire kinds. `setProtocolEngine` and `getProtocolEngine` configure cached `RpcEngine` instances. Many `getProxy`, `getProtocolProxy`, and `waitForProtocolProxy` overloads create clients with UGI, socket factory, timeout, retry policy, auth fallback, and alignment context. `Builder` builds servers. `Server` registers protocol implementations, installs `ProtocolMetaInfoPB`, resolves supported versions, and dispatches calls to rpc-kind invokers.

## Control Flow
Client construction initializes SASL when security is enabled, resolves the configured engine, and delegates proxy creation. `waitForProtocolProxy` retries connection failures until timeout or interruption. Server construction validates mandatory builder fields, delegates to the protocol engine, registers protocol implementation maps, and installs protocol metadata service. Incoming calls are dispatched by `Server.call` through the registered invoker for the request kind.

## State and Persistence Behavior
Static `PROTOCOL_ENGINES` caches one engine per protocol class. Server instances hold per-rpc-kind protocol implementation maps keyed by protocol name and version, plus scheduler priority side effects for service principals. No durable persistence occurs.

## Dependencies and Integration Points
It integrates with `Client`, `Server`, `RpcEngine`, `ProtobufRpcEngine2`, SASL/security, UGI, Hadoop configuration, protocol metadata, retry policies, and service-specific translators. `TestRPC`, `TestRPCWaitForProxy`, `TestMultipleProtocolServer`, and compatibility tests cover major paths.

## Risks and Test Signals
High-risk areas are engine cache lifetime/config drift, protocol annotation/version fallback, security initialization, proxy close semantics, server registration maps, and wait-loop timeout arithmetic. Tests should cover multiple protocols, version mismatch, unauthorized access, proxy stop failures, security-enabled clients, and metadata service registration.
