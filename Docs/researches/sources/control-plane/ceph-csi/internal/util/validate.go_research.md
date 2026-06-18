<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate.go -->
## sources/control-plane/ceph-csi/internal/util/validate.go

Purpose: validates CSI request fields, volume IDs, read-only mode constraints, and service account mount restrictions.

APIs: validation functions for ControllerPublish/Unpublish, NodeStage/Unstage, NodePublish/Unpublish; `CheckReadOnlyManyIsSupported`; `ValidateVolumeID`; `IsStaticVol`; and `ValidateServiceAccountRestriction`. Constants define CSI volume/publish context keys for service account and pod UID.

Control flow: request validators enforce non-empty volume id, volume capability where required, node id/paths, secrets for stage, and staging path existence. `ValidateVolumeID` rejects empty IDs, path traversal `..`, slash/backslash, and for dynamic volumes enforces `hhhh-hhhh-[A-Za-z0-9_-]+`. Static volumes skip only the format check. Service-account restriction allows empty policy, warns and allows empty pod SA, otherwise exact-matches a comma-separated list.

State and persistence: checks local filesystem existence for node staging target. Logs service-account warning/debug messages.

Dependencies: CSI protobufs, gRPC status codes, regex/string parsing, internal log.

Integration points: called at CSI RPC boundaries before driver-specific handling. Service-account restriction relies on kubelet `podInfoOnMount` and controller publish context data.

Risks: comma-separated service-account values are not trimmed, so spaces become part of names. Allowing missing pod service account when a restriction exists favors compatibility over strict enforcement. Static volumes still reject traversal and separators, which is important for path safety.

Test signals: `validate_test.go` covers `ValidateVolumeID` and service account restriction, including path traversal and multiple allowed SAs; broader CSI request validators are not covered here.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate.go -->
