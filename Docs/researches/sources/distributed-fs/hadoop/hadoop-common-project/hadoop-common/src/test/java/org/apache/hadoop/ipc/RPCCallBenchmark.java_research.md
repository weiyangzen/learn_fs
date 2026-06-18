# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ipc/RPCCallBenchmark.java

## Purpose
`RPCCallBenchmark` is a command-line protobuf RPC throughput benchmark. It can run a server, clients, or both, and reports calls per second plus CPU time per call.

## Important APIs, Types, and Functions
`MyOptions` parses CLI flags for server handlers, reader threads, client threads, message size, runtime, host, port, and RPC engine. `startServer()` builds a protobuf `RPC.Server` with `TestRpcService`. `setupClientTestContext()` creates one proxy per client thread identity and repeating test threads. `RpcServiceWrapper` abstracts the echo call. `createRpcClient()` builds a `TestRpcService` proxy and sends `EchoRequestProto`.

## Control Flow
`run()` parses options, sets the protocol engine, starts a server if requested, starts client test threads if requested, prints per-second throughput for the configured duration, then prints aggregate throughput and client/server CPU nanoseconds per call. If only a server is requested, it sleeps indefinitely until externally stopped. `main()` invokes the tool through `ToolRunner`.

## State and Persistence
State includes `Configuration`, an atomic per-second `callCount`, server handler threads, client proxy array, generated echo message, and thread CPU counters from `ThreadMXBean`. Results are printed, not persisted.

## Dependencies and Integration Points
The benchmark depends on Apache Commons CLI, Hadoop `Tool`, `RPC`, `ProtobufRpcEngine2`, test protobuf services, `MultithreadedTestUtil`, UGI test users, and `NetUtils` free-port selection.

## Risks and Edge Cases
At least one of server or client threads must be specified. Server-only mode never exits by itself. CPU time reporting depends on JVM thread CPU support and can be affected by thread lifecycle. The only accepted engine option is `protobuf`.

## Test Signals
Signals are successful option validation, server bind/start, client echo loops, increasing call counts, per-second and aggregate throughput output, and clean server stop when clients finish.
