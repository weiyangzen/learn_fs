# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/rpc_engine_test.cc

## Purpose

This unit test validates `RpcEngine` request/response handling, connection reset recovery, connect retry behavior, event callbacks, and RPC timeout behavior using mock sockets.

## Important APIs, types, and functions

The file defines `make_endpoint()`, `MockRPCConnection`, `SharedMockRPCConnection`, `SharedConnectionEngine`, and `RpcResponse()`. Tests cover round trip success, connection reset fail/recover with optional delay, connect failure retry/failure/recovery, event callback ordering and error injection, async delayed recovery, and timeout.

## Control flow, state, and persistence

Tests create `IoService`, `Options`, engines, and mock connections. `RpcResponse()` frames Hadoop RPC responses with a length prefix and varint-delimited header/body. Shared producer mocks emit errors, valid responses, or `would_block` to simulate hangs. Retry tests configure max retries and retry delays, install retry policies, and stop the IO service when callbacks complete. Event tests install FS callbacks that deliberately fail selected connect/read events and assert the callback sequence.

## Dependencies and integration points

The test depends on generated RPC/test protobufs, `RpcConnectionImpl`, `RpcEngine`, `NamenodeInfo`, mock connections, Boost.Asio/deadline timers, and gmock. It is the primary unit signal for the async RPC layer above raw sockets and below filesystem operations.

## Risks and test signals

The callback-order assertions are brittle by design and will flag control-flow changes in retry logic. `would_block` producers require timers to prevent hangs. Passing tests indicate request correlation, response parsing, retry policy integration, connection replacement, event injection, and timeout cancellation remain coherent.
