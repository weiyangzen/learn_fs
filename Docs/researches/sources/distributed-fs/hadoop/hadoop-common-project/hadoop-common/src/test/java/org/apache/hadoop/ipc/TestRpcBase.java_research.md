# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestRpcBase.java

## Purpose

`TestRpcBase` is the shared fixture for Hadoop IPC protobuf RPC tests. It does not define JUnit test methods itself; instead it centralizes server construction, client proxy creation, token fixtures, test protocol metadata, and a protobuf-backed server implementation used by authentication, scheduling, timeout, and response-ordering tests.

## Important APIs, Types, And Functions

The main helper APIs are `setupConf()`, `newServerBuilder()`, `setupTestServer()`, overloaded `getClient()` methods, `getMultipleClientWithIndex()`, `stop()`, and `countThreads()`. `MockConnectionId` extends `Client.ConnectionId` by adding an `index` into equality/hash identity so tests can force separate cached connections. `TestTokenIdentifier`, `TestTokenSecretManager`, and `TestTokenSelector` provide a minimal Hadoop token kind named `test.token`. `TestRpcService` is annotated with `@KerberosInfo`, `@TokenInfo`, and `@ProtocolInfo` and extends the generated protobuf blocking interface. `PBServerImpl` implements test RPC methods such as `ping`, `echo`, `error`, `slowPing`, `add`, `exchange`, `sleep`, `lockAndSleep`, `getAuthMethod`, auth-user queries, and postponed response methods.

## Control Flow

Tests call `setupConf()` to install `ProtobufRpcEngine2` for `TestRpcService`, build an `RPC.Server` around a reflective protobuf `BlockingService`, start it, and use `NetUtils.getConnectAddress()` for clients. Client helpers call `RPC.getProtocolProxy()` with the current UGI, socket factory, timeout, optional retry policy, and optional fallback-to-simple-auth flag. `PBServerImpl` methods exercise normal response paths, thrown `ServiceException`s, lock timing accumulation through `ProcessingDetails`, server-local context via `Server.get()` and `Server.getCurCall()`, and postponed calls by storing `Server.Call` objects then later invoking `sendResponse()`.

## State And Persistence Behavior

The class has static shared `addr` and `conf` fields, per-server latches and postponed-call lists in `PBServerImpl`, token identity serialized through Hadoop `Writable`, and no persistent disk state. Mutable state is test-scoped but global UGI/protocol-engine configuration can leak if callers do not reset it. `stop()` is intentionally tolerant and attempts to close proxies and servers despite exceptions.

## Dependencies And Integration Points

It integrates with Hadoop RPC core (`RPC`, `Server`, `Client.ConnectionId`, `ClientId`), protobuf test classes under `org.apache.hadoop.ipc.protobuf`, UGI/security/token APIs, `NetUtils`, retry policies, and `ProcessingDetails`. Downstream tests depend on its fixtures to validate SASL, response postponement, user identity propagation, and server timing behavior.

## Risks And Test Signals

Risks include static configuration leakage across tests, cached client connections masking configuration changes, races around postponed calls, and token selector/service mismatches. Strong signals are tests that create real RPC servers, assert client IDs, verify auth methods and users through server context, exercise deferred response ordering, and check lock timing injection through `ProcessingDetails`.
