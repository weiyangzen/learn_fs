# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestProtoBufRPCCompatibility.java

Purpose: validates protobuf RPC protocol-version compatibility and optional-field evolution behavior.

Important APIs/types/functions: `OldRpcService`, `NewRpcService`, `NewerRpcService`, `ProtocolInfo`, generated protobuf service interfaces (`OldProtobufRpcProto`, `NewProtobufRpcProto`, `NewerProtobufRpcProto`), `Server.getClientId()`, and `ProtobufRpcEngine2`.

Control flow: the test starts a server implementing version 2 of protocol name `testProto`, then creates a version 1 client for the same protocol and verifies a ping fails with a version mismatch. It then creates a newer version-2 compatible client and verifies an `echo` call with the old empty request remains compatible.

State and persistence behavior: static address/server/config fields hold test process state. Server implementations inspect per-call client ID state and assert the expected 16-byte ID. No durable persistence.

Dependencies and integration points: exercises protocol name/version annotations, generated protobuf blocking services, RPC builder registration, client ID propagation, and compatibility of protobuf schema evolution.

Risks and test signals: strong signal for version mismatch diagnostics and optional field compatibility. It does not deeply test all method evolution cases; server cleanup is not in a `finally`, so unexpected early failures could leave the static server running in-process.
