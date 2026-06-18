<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.pb.go -->
# sources/cloud-native/containerd/api/types/runc/options/oci.pb.go

Purpose: generated Go protobuf bindings for `types/runc/options/oci.proto`, used as the typed `Any` payload for runc shim runtime options, checkpoint options, and process details. It is data-contract code rather than hand-written behavior.

Important APIs/types/functions: exports `Options`, `CheckpointOptions`, and `ProcessDetails`, each with standard `Reset`, `String`, `ProtoMessage`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe getters. `Options` carries runc task configuration such as `NoPivotRoot`, `NoNewKeyring`, shim cgroup, I/O pipe uid/gid, runc binary/root, systemd cgroup, CRIU image/work paths, and deprecated task API address/version fields. `CheckpointOptions` carries CRIU checkpoint flags including exit, TCP, external unix sockets, terminal, file locks, empty namespaces, cgroups mode, image path, and work path. `ProcessDetails` carries an `ExecID` for shim-managed exec processes.

Control flow: generated initialization builds `File_types_runc_options_oci_proto`, raw descriptors, exporter functions for unsafe-disabled builds, message infos, and Go type mappings. Runtime methods are protobuf reflection accessors and do not perform validation or side effects.

State/persistence: instances serialize to protobuf bytes and are persisted wherever containerd stores runtime `Any` options, task checkpoint request options, or checkpoint image metadata. Field number 8 remains reserved by the source proto, so old `criu_path` data must not be reused.

Dependencies/integration: depends on `protoreflect`, `protoimpl`, and `reflect/sync`. Hand-written client checkpoint code marshals `options.CheckpointOptions` into task checkpoint requests and checkpoint image records. Runtime option payloads integrate with runc shim implementations through typeurl/protobuf `Any`.

Risks: generated file must stay in lockstep with `oci.proto`; editing it directly will be overwritten. Deprecated `TaskApiAddress` and `TaskApiVersion` still deserialize for compatibility but should not guide new behavior. Proto3 zero values make unset and explicit false/zero indistinguishable, so callers must rely on higher-level defaults.

Test signals: regeneration via the repository proto target should be clean. API compatibility tests should cover marshal/unmarshal of all fields, reserved tag 8 non-reuse, checkpoint option round trips, and compatibility with client checkpoint code.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/runc/options/oci.pb.go -->
