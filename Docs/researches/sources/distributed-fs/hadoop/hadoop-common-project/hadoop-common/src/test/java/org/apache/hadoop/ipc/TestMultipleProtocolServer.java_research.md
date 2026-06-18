# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/TestMultipleProtocolServer.java

Purpose: verifies that a server initialized through `TestRpcBase` can host protobuf RPC service traffic, historically covering mixed protocol support on one server.

Important APIs/types/functions: `TestRpcBase`, `RPC.Server`, `RPC.setProtocolEngine()`, `ProtobufRpcEngine2`, `TestRpcService`, and `TestProtoBufRpc.testProtoBufRpc()`.

Control flow: setup initializes common RPC test configuration and starts a test server with two handlers. The test configures a protobuf RPC engine for `TestRpcService`, obtains a proxy to the inherited server address, and reuses the canonical protobuf ping/echo/error assertions from `TestProtoBufRpc`.

State and persistence behavior: only static test server state and inherited address/configuration are maintained; teardown stops the server. No files or durable state.

Dependencies and integration points: bridges the generic RPC test base and protobuf RPC suite, ensuring server protocol registration remains compatible with clients configured separately.

Risks and test signals: compact integration smoke test. Failures point to protocol engine registration, server multi-protocol wiring, or changes in `TestRpcBase` setup rather than detailed protobuf method behavior.
