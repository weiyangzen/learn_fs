<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.pb.go -->
# sources/cloud-native/containerd/api/types/sandbox.pb.go

Purpose: generated protobuf Go binding for sandbox metadata objects managed by sandbox controllers.

Important APIs/types/functions: `Sandbox` includes `SandboxID`, nested `Sandbox_Runtime`, `Spec`, labels, `CreatedAt`, `UpdatedAt`, extensions, and `Sandboxer`. `Sandbox_Runtime` includes runtime `Name` and `Options` as `Any`. Generated getters expose nil-safe access to maps, timestamps, and `Any` fields.

Control flow: generated descriptor initialization builds message info for `Sandbox`, map-entry types, and nested runtime. Runtime behavior is limited to protobuf reflection and getters.

State/persistence: sandbox records persist identity, runtime selection/options, spec blob, labels, timestamps, extension blobs, and owning sandboxer. Maps serialize as protobuf map entries; timestamps use protobuf timestamp semantics.

Dependencies/integration: imports `google.protobuf.Any` and `Timestamp`; Go package is `github.com/containerd/containerd/api/types`. The client exposes sandbox store/controller proxies from `client.go`, and container metadata can reference a sandbox ID through `WithSandbox`.

Risks: `Any` fields require type registration/consumer knowledge. Map fields are mutable in Go and can be nil. Schema comments contain typos but not semantic issues. Field number gap to `sandboxer = 10` should be preserved for compatibility.

Test signals: sandbox store/controller tests should round-trip runtime options, spec, labels, extensions, and timestamp conversions; generated code should match `sandbox.proto`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/sandbox.pb.go -->
