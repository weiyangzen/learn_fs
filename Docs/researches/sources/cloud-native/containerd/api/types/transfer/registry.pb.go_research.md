<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/registry.pb.go

Purpose: generated bindings for OCI registry transfer endpoints, resolver configuration, authentication callbacks, and HTTP debug options.

Important APIs/types/functions: enum `HTTPDebug` has `DISABLED`, `DEBUG`, `TRACE`, `BOTH`; enum `AuthType` has `NONE`, `CREDENTIALS`, `REFRESH`, `HEADER`. `OCIRegistry` carries reference and resolver. `RegistryResolver` carries auth stream, headers, host directory, default scheme, HTTP debug mode, and logs stream. `AuthRequest` carries host, repository reference, and `WWW-Authenticate` values. `AuthResponse` carries auth type, secret, username, and expiry.

Control flow: generated enum/message helpers and descriptor init only. Authentication callback sequencing is implemented by transfer registry/resolver code.

State/persistence: resolver settings are request-scoped; auth responses may contain credentials and expiry times. Header maps and secrets must be treated as sensitive.

Dependencies/integration: imports protobuf `Timestamp`. Used by transfer service registry source/destination configuration and stream-based auth/log callback plumbing.

Risks: secrets in `AuthResponse` and headers can leak through logs or debugging. `HEADER` auth allows raw authorization header injection. Host directory/default scheme influence trust and endpoint selection. Debug/trace modes may expose credentials if not redacted.

Test signals: registry transfer tests should cover auth challenge/response types, expiry, custom headers, host directory config, HTTP debug/log streams, and secret redaction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/registry.pb.go -->
