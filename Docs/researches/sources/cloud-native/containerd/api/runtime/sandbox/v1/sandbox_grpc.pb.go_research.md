# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox_grpc.pb.go

Purpose: generated gRPC bindings for the sandbox runtime service, excluded when build tag `no_grpc` is set.

Important APIs/types/functions: `SandboxClient` interface and `NewSandboxClient` wrap `grpc.ClientConnInterface` and invoke nine fully-qualified RPCs. `SandboxServer` declares the same methods and requires embedding `UnimplementedSandboxServer` for forward compatibility. `RegisterSandboxServer`, per-method `_Sandbox_*_Handler` functions, and `Sandbox_ServiceDesc` register server-side unary RPCs.

Control flow: client methods allocate response objects and call `cc.Invoke`. Server handlers decode requests, optionally pass through unary interceptors, and dispatch to the concrete `SandboxServer`. Unimplemented methods return `codes.Unimplemented`.

State/persistence: no durable state; clients hold a connection handle and server registration holds service metadata.

Dependencies/integration: imports `context`, `google.golang.org/grpc`, and gRPC status/codes. Integrates sandbox service implementations with gRPC transport.

Risks/test signals: generated `_Sandbox_StartSandbox_Handler` contains a duplicated unreachable `return nil, err` in the decode-error branch. It is harmless but indicates generated-code quality should be checked on regeneration. Tests should cover service registration, interceptor path, unimplemented defaults, and build behavior with `no_grpc`.
