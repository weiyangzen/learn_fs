# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/test_rpc_service.proto

Purpose: Protobuf service schema for Hadoop IPC tests using the current `test.proto` message classes. It defines multiple test services for normal calls, multi-protocol behavior, protocol compatibility, custom protocol naming, and sleep handoff timing.

Important APIs/types/functions: Uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `TestRpcServiceProtos`, generic services, generated equals/hash, and imports `test.proto`. Services include `TestProtobufRpcProto`, `TestProtobufRpc2Proto`, `OldProtobufRpcProto`, `NewProtobufRpcProto`, `NewerProtobufRpcProto`, `CustomProto`, and `TestProtobufRpcHandoffProto`.

Control flow: Generated service interfaces dispatch RPC methods such as `ping`, `echo`, `error`, `slowPing`, `add`, `exchange`, `sleep`, `lockAndSleep`, auth/user lookup, postponed echo/send, current/remote user lookup, and handoff sleep. Compatibility services intentionally vary the `echo` signature across old/new/newer protocols.

State and persistence behavior: No schema-local persistent state. Runtime state is in generated request/response messages and test service implementations. RPC method names and request/response types form the service ABI used by Hadoop IPC test servers and clients.

Dependencies and integration points: Depends on `test.proto` messages and protobuf generic service generation. It integrates directly with Hadoop IPC protobuf engine tests, server/client authentication tests, exception propagation tests, and protocol version compatibility checks.

Risks: Service and method names are test protocol ABI; renaming or changing signatures breaks generated stubs and reflection-based protocol mapping. Generic services are legacy protobuf Java behavior, so toolchain upgrades must preserve support or migrate tests. Compatibility services must remain intentionally distinct.

Test signals: Successful protoc service generation, RPC calls across all methods, expected server-side errors, auth/user responses, postponed response behavior, and old/new protocol compatibility tests validate this schema.
