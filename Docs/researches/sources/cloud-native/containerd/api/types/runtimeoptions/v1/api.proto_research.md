<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.proto -->
# sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.proto

Purpose: source schema for runtime option indirection, especially runtime-specific config supplied by path or embedded TOML bytes.

Important APIs/types/functions: `Options` includes `type_url` to identify the config type, `config_path` for a filesystem config file, and `config_body` for an in-memory TOML blob used when `config_path` is absent.

Control flow: no executable flow; schema comments define precedence semantics: `config_body` is used if `config_path` is not specified.

State/persistence: `config_path` references mutable external filesystem state; `config_body` embeds a snapshot of config bytes in the serialized message.

Dependencies/integration: `go_package` is `github.com/containerd/containerd/api/types/runtimeoptions/v1;runtimeoptions`. Runtime plugin loaders and shims can consume this message via protobuf `Any`.

Risks: unclear or invalid `type_url` can lead to runtime-specific decode failures. Path-based configs depend on file availability and permissions at runtime. Body payloads are unvalidated by schema.

Test signals: validate generated Go bindings, precedence between path and body in consuming code, and error behavior for unknown type URLs or unreadable paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runtimeoptions/v1/api.proto -->
