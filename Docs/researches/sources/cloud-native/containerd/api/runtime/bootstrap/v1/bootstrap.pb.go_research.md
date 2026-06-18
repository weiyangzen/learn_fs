# sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.pb.go

Purpose: generated Go protobuf bindings for the shim bootstrap protocol.

Important APIs/types/functions: exports open numeric enum `LogLevel` with negative verbose values and positive severe values, `Capability`, `BootstrapParams`, `Extension`, and `BootstrapResult`. `BootstrapParams` includes instance ID, namespace, log level, containerd version, TTRPC/gRPC addresses, binary path, typed extensions, and optional `SocketDir *string`. `BootstrapResult` includes version, address, protocol, capabilities, and metadata.

Control flow: protobuf-generated methods provide enum descriptors, message reflection, getters, descriptor compression, and type registration. `GetSocketDir` returns empty string when the optional pointer is nil.

State/persistence: no local storage; this file defines the JSON/protobuf-compatible startup contract between containerd and shims. Optional field presence matters for `socket_dir`.

Dependencies/integration: depends on protobuf runtime/reflection and `google.protobuf.Any`. Integrates with bootstrap helpers, shim process startup, and typed extension negotiation.

Risks/test signals: generated code shows duplicated `ms.StoreMessageInfo(mi)` in `BootstrapParams.ProtoReflect`, harmless but a regeneration artifact worth watching. Unknown log levels are allowed by schema; consumers must not reject them. Tests should cover optional socket_dir presence, Any extensions, metadata maps, and enum numeric compatibility.
