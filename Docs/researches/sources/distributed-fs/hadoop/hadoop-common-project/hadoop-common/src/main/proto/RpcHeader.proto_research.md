# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/RpcHeader.proto

## Purpose
`RpcHeader.proto` defines Hadoop IPC framing metadata for requests, responses, tracing, caller context, retry/state tracking, router federation state, authorization headers, and SASL negotiation.

## Important APIs, types, and functions
Top-level `RpcKindProto` enumerates writable, protocol-buffer, and protocol-buffer2 RPC kinds. Messages include `RPCTraceInfoProto`, `RPCCallerContextProto`, `RpcRequestHeaderProto`, `RpcResponseHeaderProto`, and `RpcSaslProto`. Request fields include call ID, client ID, retry count, trace info, caller context, state ID, router federated state, and authorization header. Response fields include call ID, status, IPC version, exception data, error detail enum, client ID, retry count, state ID, and router state. SASL state covers negotiate/initiate/challenge/response/wrap and advertised auth methods.

## Control flow
Every IPC request and response uses these headers around the engine-specific payload. During authentication, `RpcSaslProto` drives the SASL handshake. During normal calls, request headers identify operation and call correlation; response headers return status or exception metadata.

## State and persistence
Headers are per packet/call. They carry transient correlation, retry, auth, trace, and federation metadata. State IDs reflect server/global state but are not persisted by the proto itself.

## Dependencies and integration points
It generates `org.apache.hadoop.ipc.protobuf.RpcHeaderProtos` and is central to Hadoop IPC client/server, retry cache behavior, tracing, router federation, authorization, and SASL authentication.

## Risks and test signals
Risks include enum value compatibility, required call/client IDs, leakage of authorization headers, large error messages, mismatched retry counts, and SASL state-machine bugs. Test signals include IPC compatibility tests, SASL auth suites, retry-cache tests, tracing propagation, router federation tests, and mixed-version client/server calls with unknown optional fields.
