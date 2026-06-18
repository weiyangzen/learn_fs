# sources/control-plane/ceph-csi/internal/nvmeof/util/mounter_test.go

Purpose: Tests raw `findmnt` source parsing for NVMe device discovery.

Important APIs/types/functions: Exercises `parseNVMEDeviceFromRawSource`.

Control flow: Table cases cover direct `/dev/nvme0n2`, block-volume `devtmpfs[/nvme1n1]` and `devtmpfs[/nvme0n1]`, non-NVMe devtmpfs, and unrelated strings.

State and persistence behavior: Pure parser tests; no mount table reads.

Dependencies and integration points: Uses `testify/require`. Guards node utility behavior used by mount cache and unstage disconnect decisions.

Risks: Does not cover `devtmpfs[nvme0n1]` without slash despite parser support, full JSON unmarshalling, or partition paths.

Test signals: Focused coverage for the most important source string formats.
