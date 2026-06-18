# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRpc.java

Purpose: primary protobuf RPC suite for `ProtobufRpcEngine2`, also testing coexistence with the legacy protobuf engine. It covers ping/echo/error calls, second protocol registration, legacy service registration order, RPC metrics, maximum data length, application exception mapping, and slow-RPC logging.

Important APIs/types/functions: `TestRpcService2`, `TestRpcService2Legacy`, `PBServer2Impl`, `PBServer2ImplLegacy`, `RPC.Builder`, `server.addProtocol()`, generated `TestProtobufRpcProto`/`TestProtobufRpc2Proto`, `ProtobufRpcEngine2`, legacy `ProtobufRpcEngine`, `RpcMetrics`, and parameter source `params()`.

Control flow: each parameterized test calls `initTestProtoBufRpc()` with combinations of legacy enabled and legacy-first registration. Setup configures max data length and slow RPC logging, registers protobuf engines, builds a server with one protocol, adds a second protocol, optionally adds a legacy protocol, and starts it. Tests then obtain proxies and issue ping/echo/error/sleep calls while asserting response contents, `RemoteException` error codes, metrics counters, oversized request failure, and slow-call metric increments.

State and persistence behavior: static server/address plus per-test booleans define runtime state. `@AfterEach` stops the server. No persistent state. Metrics accumulate on the in-process server and are inspected after call bursts.

Dependencies and integration points: integrates protobuf generated classes from both shaded/current and legacy protobuf packages, Hadoop metrics, `CommonConfigurationKeys.IPC_MAXIMUM_DATA_LENGTH`, slow-RPC logging controls, and `TestRpcBase` helpers.

Risks and test signals: parameterization gives good coverage of protocol registration order and mixed engines. Slow-RPC tests use 10K fast calls and wall-clock sleeps, so they are more timing-sensitive. Key signals are correct error-code classification (`ERROR_RPC_SERVER`, `ERROR_APPLICATION`), data-length rejection, detailed metric method counters, and disabled slow logging producing no slow-call increments.
