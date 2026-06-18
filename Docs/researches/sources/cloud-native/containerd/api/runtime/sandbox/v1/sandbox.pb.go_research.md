# sources/cloud-native/containerd/api/runtime/sandbox/v1/sandbox.pb.go

Purpose: generated Go protobuf bindings for the optional shim sandbox runtime API.

Important APIs/types/functions: exports request/response types for sandbox create, start, platform, stop, update, wait, status, ping, shutdown, and metrics. Important fields include sandbox ID, bundle path, rootfs mounts, options/resources `Any`, netns path, annotations, start PID/spec/created time, platform, stop timeout, wait exit data, status info/extra, and metrics.

Control flow: generated message methods provide nil-safe getters, reflection, descriptor compression, and descriptor registration. The descriptor includes one service with nine RPCs; `UpdateSandboxRequest/Response` exist as messages but there is no corresponding service method in this proto.

State/persistence: no local persistence. The messages define wire contracts between containerd and sandbox-capable shims.

Dependencies/integration: imports containerd `types` for mounts, metrics, and platform plus protobuf `Any` and `Timestamp`. Integrates with gRPC/TTRPC transport files and shim implementations.

Risks/test signals: mismatch between message definitions and service methods can confuse implementers, especially the unused update messages. Map fields are nil on absent messages. Tests should validate cross-transport encoding, status timestamps, metrics type, and optional Any payload unpacking.
