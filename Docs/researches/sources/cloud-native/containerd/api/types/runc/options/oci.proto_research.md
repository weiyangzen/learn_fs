<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.proto -->
# sources/cloud-native/containerd/api/types/runc/options/oci.proto

Purpose: defines the protobuf wire schema for runc runtime, checkpoint, and process-detail options under package `containerd.runc.v1`.

Important APIs/types/functions: `Options` describes shim/runc creation behavior: pivot-root/keyring toggles, shim cgroup, I/O ownership, binary/root path, systemd cgroups, CRIU image/work paths, and deprecated task API fields. `CheckpointOptions` describes CRIU checkpoint behavior: exit-after-checkpoint, open TCP, external Unix sockets, pty, file locks, empty namespaces, cgroups mode, image path, and work path. `ProcessDetails` identifies a shim-managed exec process by `exec_id`.

Control flow: no executable flow; protoc turns this schema into Go bindings and descriptors. Field numbering is the control surface because serialized checkpoint/runtime data depends on stable tags.

State/persistence: these messages are persisted in runtime option `Any` payloads and checkpoint content. `reserved 8` protects the removed `criu_path` field from incompatible reuse.

Dependencies/integration: `go_package` maps to `github.com/containerd/containerd/api/types/runc/options;options`. The client checkpoint implementation uses `CheckpointOptions`; runtime shims consume `Options` through typeurl/protobuf.

Risks: changing field numbers or semantics breaks persisted checkpoints and external clients. Deprecated task API fields remain part of the schema for old payloads. Path-like fields have no schema validation and must be checked by consumers.

Test signals: generated `oci.pb.go` should match this file. Compatibility tests should check older payloads, reserved-field preservation, and checkpoint option behavior against runc shim/task service integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.proto -->
