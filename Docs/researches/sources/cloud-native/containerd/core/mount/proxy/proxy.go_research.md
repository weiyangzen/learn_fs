<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/proxy.go -->
# sources/cloud-native/containerd/core/mount/proxy/proxy.go

Purpose: client-side `mount.Manager` implementation backed by the containerd mounts gRPC/ttrpc service.

Important APIs/types/functions: `proxyMounts`, `NewMountManager`, and methods `Activate`, `Deactivate`, `Info`, `Update`, and `List`.

Control flow: `NewMountManager` accepts a gRPC mounts client, generic gRPC connection, ttrpc mounts client, or ttrpc client, wrapping gRPC as a ttrpc-compatible interface where needed. Each method converts core structs/options into API requests, calls the remote client, converts responses back, and maps gRPC errors to native errors with `errgrpc.ToNative`. `List` consumes a streaming response until `io.EOF`.

State and persistence: stores only the RPC client. Persistent activation state lives in the remote manager service.

Dependencies and integration points: bridges `core/mount.Manager` callers to API service `api/services/mounts/v1`. Update masks use containerd protobuf field mask type.

Risks: `NewMountManager` panics on unsupported client types. `Activate` forwards labels and `Temporary` but not `AllowMountTypes`, so remote behavior cannot honor that option through this proxy as written. Streaming errors abort list.

Test signals: no direct proxy tests in this subset; conversion/proxy correctness is inferred from API use.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/proxy.go -->
