# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/proto/mini_rpc_benchmark.proto

Purpose: Protobuf schema for `MiniRPCBenchmark`, mirroring a legacy Writable RPC mini protocol so benchmarks can exercise delegation-token RPC connection establishment over `ProtobufRpcEngine2`.

Important APIs/types/functions: The file uses `syntax = "proto2"`, Java package `org.apache.hadoop.ipc.protobuf`, outer class `MiniRPCBenchmarkProtos`, generic services, and generated equals/hash. Messages are `MiniGetDelegationTokenRequestProto`, `MiniDelegationTokenProto`, and `MiniGetDelegationTokenResponseProto`. Service `MiniProtocolService` exposes `getDelegationToken()`.

Control flow: There is no runtime control flow in the schema. Generated code will serialize a request with required `renewer`, optionally return a delegation token response, and dispatch the service method through protobuf RPC bindings.

State and persistence behavior: Serialized message state includes token identifier/password bytes and token kind/service strings. Required proto2 fields make missing fields invalid at build/serialization time for initialized messages. The response token is optional to allow absent-token responses.

Dependencies and integration points: It intentionally inlines token messages instead of importing security protos to keep benchmark proto-path setup simple. Generated Java integrates with Hadoop IPC protobuf benchmark code and service stubs.

Risks: Required proto2 fields are strict and can break compatibility if benchmark callers construct partial messages. Since this is a benchmark-specific mirror, drift from the legacy MiniProtocol shape would undermine comparative results. Field numbers are wire ABI and must remain stable.

Test signals: Successful protoc generation, service stub availability, and benchmark RPC calls that request and return delegation token messages validate this schema.
