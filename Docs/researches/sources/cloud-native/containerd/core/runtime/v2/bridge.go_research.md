# sources/cloud-native/containerd/core/runtime/v2/bridge.go

## Purpose
Provides the compatibility client facade used by containerd to talk to runtime v2/v3 shim task services over either ttrpc or gRPC. The file hides transport and API-version differences behind `TaskServiceClient`, whose methods match the current v3 task API.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TaskServiceClient` lists the task RPC surface: state, create, start, delete, pids, pause/resume, checkpoint, kill, exec, pty resize, close IO, update, wait, stats, connect, and shutdown. `NewTaskClient` dispatches on concrete client type: `*ttrpc.Client` supports v2 via `ttrpcV2Bridge` and v3 directly, while `grpc.ClientConnInterface` supports only v3 via `grpcV3Bridge`.

The control flow is adapter-only. For v2 ttrpc shims, each bridge method builds the v2 request from the v3 request, calls the v2 generated client, and maps the v2 response into the v3 response type. gRPC v3 methods pass through to the generated gRPC client because the request/response types already match. The file keeps no persistent state beyond client pointers in bridge structs.

Dependencies include generated task APIs for v2 and v3, ttrpc, gRPC, and protobuf empty responses. Integration points are `newShimTask`, shim reload/downgrade handling, and any code that wants a version-neutral task client.

Primary risks are lossy compatibility if v3 fields are added but not represented in v2, unsupported version errors, nil response dereferences if an RPC returns both nil response and error handling changes, and accidental use of gRPC for non-v3 shims. Test signals are table tests for `NewTaskClient`, bridge request/response mapping for every RPC, and integration tests against v2 ttrpc, v3 ttrpc, and v3 gRPC shims.
