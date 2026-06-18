<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util_test.go -->
## sources/control-plane/ceph-csi/internal/util/util_test.go

Purpose: unit tests for selected general utilities.

Coverage: `TestRoundOffBytes` and `TestRoundOffVolSize` cover MiB/GiB rounding behavior. `TestMountOptionsAdd` covers empty inputs, duplicate avoidance, leading/trailing commas, and multiple additions. `TestRoundOffCephFSVolSize` covers sub-4MiB, MiB, MB, near-GiB, and GiB rounding. `TestParseClientIP` covers IPv4, IPv6 bracketed addresses, compressed IPv6, and invalid input. `TestConvertIPToCIDR` covers IPv4, IPv6, zero/loopback, and invalid strings.

State and dependencies: pure unit tests, no Ceph/Kubernetes dependencies.

Integration signals: confirms user-facing capacity normalization and network filter helper behavior.

Risks and gaps: no coverage for `ValidateDriverName`, `GenerateVolID`, mount wrappers, call stack, volume context filtering, or controller publish secret lookup.

Test signal quality: good for arithmetic/string helpers; intentionally limited for cluster-integrated helpers.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util_test.go -->
