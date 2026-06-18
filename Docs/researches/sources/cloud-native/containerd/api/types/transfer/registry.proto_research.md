<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.proto -->
# sources/cloud-native/containerd/api/types/transfer/registry.proto

Purpose: source schema for registry-backed transfer endpoints and auth/debug callback contracts.

Important APIs/types/functions: `OCIRegistry` identifies a registry reference plus resolver settings. `RegistryResolver` configures auth stream, headers, host dir, default scheme, HTTP debug, and logs stream. `AuthRequest` and `AuthResponse` define credential callback messages. Enums define HTTP debug and auth response modes.

Control flow: schema-only; comments define callback and debug stream use.

State/persistence: mostly transient transfer configuration, but carries sensitive auth material and optional expiry timestamp.

Dependencies/integration: imports protobuf timestamp and integrates with transfer streaming for auth/log callbacks.

Risks: auth fields are security-sensitive. Debug/trace output and logs stream must avoid credential disclosure. Header/default scheme/host-dir values can weaken registry TLS/auth behavior if mishandled.

Test signals: auth flow tests for credentials/refresh/header, no-auth behavior, challenge parsing, TLS host-dir behavior, and log redaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.proto -->
