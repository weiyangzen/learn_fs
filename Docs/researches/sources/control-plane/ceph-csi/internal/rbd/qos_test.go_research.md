<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/qos_test.go

## Purpose
`qos_test.go` validates the pure calculation path for traditional RBD/NBD QoS limits.

## Important APIs, Types, And Functions
The helper `checkQOS` compares expected metadata keys with `rv.QosParameters`. `TestSetQOS` exercises `rbdVolume.SetQOS` with several mutable-parameter maps and requested volume sizes.

## Control Flow
The test starts with base IOPS limits, adds BPS limits, adds per-GiB growth with a base size, then verifies calculations for 20 GiB, 100 GiB, 200 GiB, and 600 GiB requested sizes, including max limit capping.

## State And Persistence
All state is in memory on a fresh `rbdVolume` per scenario. No RBD metadata is written.

## Dependencies And Integration Points
The test depends only on the RBD package constants and `oneGB`. It indirectly validates values later written by `ApplyQOS`.

## Risks
The tests do not check invalid numeric input, empty maps, missing base limits, metadata persistence, `AdjustQOS`, or clear semantics. Because expected values are hard-coded, the tests are good regression signals for formula changes.

## Test Signals
Strong signal for `calcQosBasedOnCapacity`; weak signal for handler integration and Ceph metadata side effects.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/qos_test.go -->
