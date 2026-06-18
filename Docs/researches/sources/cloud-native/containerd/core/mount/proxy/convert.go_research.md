<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/convert.go -->
# sources/cloud-native/containerd/core/mount/proxy/convert.go

Purpose: converts between core mount activation structs and protobuf API structs for the mounts service.

Important APIs/types/functions: `ActivationInfoToProto`, `ActivationInfoFromProto`, `ActiveMountToProto`, `ActiveMountFromProto`, `toTimestamp`, and `fromTimestamp`.

Control flow: conversions allocate same-length slices, copy mount fields, mount points, mount data, labels, and timestamps. Nil `ActivationInfo` proto input returns a zero-value core struct; nil time/timestamp pointers stay nil.

State and persistence: no persistence; pure data translation.

Dependencies and integration points: used by `proxy.go` and server/client code for gRPC/ttrpc mount manager RPCs. Relies on `mount.ToProto`/`FromProto` for system mounts and protobuf timestamp helpers.

Risks: `ActiveMountFromProto` assumes each proto active mount and nested `Mount` are non-nil. Timestamp conversion uses `AsTime` without validation checks.

Test signals: no direct tests in this subset; exercised indirectly by proxy clients when RPC tests exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/convert.go -->
