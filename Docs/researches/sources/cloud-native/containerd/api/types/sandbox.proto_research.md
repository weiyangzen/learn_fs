<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.proto -->
# sources/cloud-native/containerd/api/types/sandbox.proto

Purpose: defines the sandbox metadata wire contract for containerd sandbox controllers.

Important APIs/types/functions: `Sandbox` stores `sandbox_id`, nested `Runtime` with name/options, OCI-like `spec` as `Any`, labels, created/updated timestamps, extension blobs, and `sandboxer` controller name.

Control flow: schema-only file; field layout controls persistence and gRPC compatibility.

State/persistence: acts as persisted sandbox metadata for controllers. Labels and extensions provide open-ended state; timestamps track creation/mutation.

Dependencies/integration: imports protobuf `Any` and `Timestamp`; `go_package` maps to API types. Used by sandbox service APIs and client sandbox proxy accessors.

Risks: untyped `Any` payloads and arbitrary extensions can create decode/version skew. Controller name must match an available sandbox controller. Schema does not validate spec type or label keys.

Test signals: sandbox service tests should cover create/update/list serialization, extension preservation, runtime option compatibility, and timestamp behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.proto -->
