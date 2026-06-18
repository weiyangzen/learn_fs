# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.proto

Purpose: source protobuf service definition for optional sandbox-capable shim APIs.

Important APIs/types/functions: defines service `Sandbox` with unary RPCs `CreateSandbox`, `StartSandbox`, `Platform`, `StopSandbox`, `WaitSandbox`, `SandboxStatus`, `PingSandbox`, `ShutdownSandbox`, and `SandboxMetrics`. Message types describe sandbox identity, bundle/rootfs/options, network namespace, annotations, start response PID/spec, platform response, stop timeout, wait exit data, status info, ping/shutdown, and metrics.

Control flow: intended call sequence is create after shim launch, start, platform query for OCI spec generation, status/metrics/ping while running, stop/wait/shutdown for teardown. The schema itself is declarative.

State/persistence: no storage; message fields define transport API state. `Any` fields support runtime-specific options/resources/spec/extra.

Dependencies/integration: imports protobuf Any/Timestamp and containerd metrics, mount, and platform types. Generated bindings provide both gRPC and TTRPC transports.

Risks/test signals: `UpdateSandboxRequest/Response` are defined but absent from the service, which may be intentional future work or API drift. Implementers must define exact state strings and status info conventions. Tests should cover RPC method registration and compatibility across gRPC/TTRPC.
