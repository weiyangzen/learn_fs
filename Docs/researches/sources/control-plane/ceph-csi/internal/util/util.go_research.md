<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util.go -->
## sources/control-plane/ceph-csi/internal/util/util.go

Purpose: shared Ceph-CSI utility layer for driver configuration, size rounding, mount helpers, driver name validation, volume context filtering, client IP conversion, and controller publish secret lookup.

APIs and types: driver type constants, build-time `GitCommit`/`DriverVersion`, and large `Config` struct for process flags. Size helpers include `RoundOffVolSize`, `RoundOffBytes`, and `RoundOffCephFSVolSize`. Other exported helpers include `ValidateDriverName`, `GenerateVolID`, `CreateMountPoint`, `IsCorruptedMountError`, `Mount`, `MountOptionsAdd`, `CallStack`, `GetVolumeContext`, `ParseClientIP`, `ConvertIPToCIDR`, and `GetControllerPublishSecretRef`.

Control flow: size helpers round small requests by MiB and larger requests by GiB, with CephFS rounding to 4MiB boundaries first. `ValidateDriverName` uses Kubernetes DNS1123 subdomain validation on lowercase input. `GenerateVolID` resolves pool id if needed and composes a `CSIIdentifier`. `GetControllerPublishSecretRef` decodes cluster id from volume id, tries direct config lookup by driver type, then cluster mapping fallbacks.

State and persistence: reads filesystem paths for mount staging checks elsewhere, creates mount directories, reads Kubernetes/CSI config files through internal config helpers, and uses build-time variables.

Dependencies: Kubernetes validation, mount utils, cloud-provider volume helpers, network parsing, internal k8s/config helpers.

Integration points: broad driver bootstrap and request path use. Secret ref lookup bridges volume ID decoding, Ceph-CSI config map data, and cluster ID mapping.

Risks: `checkDirExists` treats non-`IsNotExist` stat errors as existence. `ParseClientIP` scans space-separated address tokens and accepts first parseable host, which is suitable for Ceph client address strings but should be documented for multi-address inputs. Secret-ref lookup depends on config file state and mapping order.

Test signals: `util_test.go` covers rounding, mount option dedupe, IP parsing, and CIDR conversion; other helpers depend on broader integration tests.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/util.go -->
