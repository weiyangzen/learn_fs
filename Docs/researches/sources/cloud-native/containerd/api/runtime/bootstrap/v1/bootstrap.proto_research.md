# sources/cloud-native/containerd/api/runtime/bootstrap/v1/bootstrap.proto

Purpose: authoritative bootstrap protocol schema between containerd and shim processes at startup.

Important APIs/types/functions: documents the flow: containerd spawns shim, writes `BootstrapParams` as JSON to stdin, shim writes `BootstrapResult` as JSON to stdout, then containerd connects to the returned address. `BootstrapParams` centralizes identity, namespace, log level, daemon version, daemon API addresses, binary path, typed extensions, and optional socket directory. `BootstrapResult` returns shim protocol/address/capabilities/metadata. Enums define log level and future capabilities.

Control flow: declarative schema plus protocol documentation. The actual control flow occurs in bootstrap callers and shims following the documented stdin/stdout exchange.

State/persistence: field numbers and JSON names are the persistent inter-process contract. `google.protobuf.Any` extensions are the extension mechanism without changing core fields.

Dependencies/integration: imports `google/protobuf/any.proto`; Go package is `api/runtime/bootstrap/v1;bootstrap`. Integrates shim startup, log configuration, daemon connection addresses, and optional capability negotiation.

Risks/test signals: stdin/stdout JSON exchange is sensitive to logging accidentally polluting stdout. `socket_dir` must stay short due to Unix socket path limits. Tests should exercise JSON round trips, unknown log-level values, extension preservation, and protocol/address validation.
