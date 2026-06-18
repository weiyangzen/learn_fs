<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos.go -->
# sources/control-plane/ceph-csi/internal/rbd/qos.go

## Purpose
`qos.go` implements traditional RBD/NBD QoS handling for mutable volume attributes. It parses user-facing QoS parameters, calculates capacity-adjusted limits, applies active limits through RBD image metadata, and persists the source policy for later adjustment after expansion.

## Important APIs, Types, And Functions
Constants map StorageClass or VolumeAttributesClass keys such as `baseIops`, `iopsPerGiB`, `maxIops`, and `baseVolSizeBytes` to Ceph metadata keys such as `rbd_qos_iops_limit` and saved-policy keys such as `rbd_base_qos_iops_limit`. `qosSpec` groups base, per-GiB, max, and target metadata fields. `nbdQoSHandler` implements `QoSHandler` with `HasParams`, `Validate`, `Apply`, and `Clear`. Key functions are `HasQoSParams`, `validateNBDQoSParams`, `parseQosParams`, `SetQOS`, `ApplyQOS`, `calcQosBasedOnCapacity`, `SaveQOS`, `getRbdImageQOS`, and `AdjustQOS`.

## Control Flow
`parseQosParams` recognizes base limits and attaches optional per-GiB and max limits. `SetQOS` records the base volume size, then calculates final RBD metadata limits for every present base limit. If per-GiB or base-size data is absent, the base limit is used directly. Otherwise, capacity over `baseVolSizeBytes` is multiplied by the per-GiB increment and capped by the max limit when provided. `ApplyQOS` writes `conf_` metadata entries consumed by RBD/NBD. `SaveQOS` stores the original policy metadata. `AdjustQOS` reloads saved policy and recalculates active limits after size changes.

## State And Persistence
Runtime state is `rv.QosParameters` and `rv.BaseVolSize`. Persistent state is RBD image metadata: active `conf_rbd_qos_*` values plus saved `rbd_base_qos_*`, `rbd_*_per_gib_limit`, max, and base-size keys. `Clear` calls `Apply` with empty parameters, which currently does not explicitly remove existing metadata keys.

## Dependencies And Integration Points
This file depends on go-ceph RBD errors for metadata-not-found handling and Ceph-CSI logging. It is integrated by `rbdVolume.modifyVolumeAttributes` and complements cgroup QoS handling in another file; controller validation is expected to prevent mixing QoS types.

## Risks
Capacity calculation uses integer GiB steps and ignores fractional capacity above the base size. Empty `Clear` does not remove old active or saved metadata in this file, so clearing semantics depend on downstream behavior or other handlers. Numeric validation accepts zero and rejects negatives, but `SetQOS` itself can still return parse errors if callers skip validation. Metadata writes are per-key and not atomic as a group.

## Test Signals
`qos_test.go` covers base-only, BPS and IOPS, capacity-adjusted, and max-capped calculations. It does not cover validation failures, `ApplyQOS`, `SaveQOS`, metadata readback, or clear behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos.go -->
