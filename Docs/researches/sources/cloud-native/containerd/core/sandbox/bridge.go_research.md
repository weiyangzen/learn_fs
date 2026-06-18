# sources/cloud-native/containerd/core/sandbox/bridge.go

## Purpose
Provides a transport-neutral sandbox API client facade, allowing callers to use the ttrpc sandbox service interface against either ttrpc or gRPC clients.

## APIs, Flow, State, Dependencies, Risks, And Tests
`NewClient` returns a generated ttrpc sandbox client for `*ttrpc.Client` or a `grpcBridge` wrapping a generated gRPC client for `grpc.ClientConnInterface`. The bridge implements all sandbox service methods by forwarding to gRPC: create, start, platform, stop, wait, status, ping, shutdown, and metrics.

There is no persistence and only a stored gRPC client pointer. Dependencies include generated runtime sandbox v1 API, ttrpc, and gRPC.

Integration points are shim/sandbox controllers that need one client interface regardless of transport. Risks are unsupported client types and future sandbox API methods requiring bridge updates. Test signals are interface conformance, unsupported type tests, and method forwarding tests with fake gRPC/ttrpc clients.
