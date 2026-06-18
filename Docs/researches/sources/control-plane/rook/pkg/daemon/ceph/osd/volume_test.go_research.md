# sources/control-plane/rook/pkg/daemon/ceph/osd/volume_test.go

## Purpose
`volume_test.go` is the main behavioral safety net for daemon-side ceph-volume orchestration. It mocks external command execution to verify the OSD agent builds correct raw/LVM commands, parses ceph-volume output, handles PVC-backed devices, respects device classes, and zaps stale devices from other clusters.

## Important APIs, Types, and Functions
The suite defines representative ceph-volume JSON fixtures for LVM, raw, encrypted raw, partitions, multi-cluster reports, and LVM symlink paths. Major tests include `TestConfigureCVDevices()`, `TestInitializeBlock()`, `TestInitializeBlockPVC()`, `TestInitializeBlockPVCWithMetadata()`, `TestParseCephVolumeLVMResult()`, `TestParseCephVolumeRawResult()`, `TestCephVolumeResultMultiClusterSingleOSD()`, `TestCephVolumeResultMultiClusterMultiOSD()`, `TestAllowRawMode()`, `TestAppendOSDInfo()`, `TestIsSafeToUseRawMode()`, `TestLVMModeAllowed()`, `TestWipeDevicesFromOtherClusters()`, `TestFindDeviceClass()`, and `TestGetCephVolumeRawOSDsHonorDeviceClass()`.

## Control Flow
Mock executors inspect command names and positional arguments to emulate `ceph-volume`, `lsblk`, `sgdisk`, `cryptsetup`, `wipefs`, `ceph-bluestore-tool`, and `dd`. The tests drive both new-device and no-available-device flows. PVC tests check LV-backed detection and raw/lvm listing behavior. LVM initialization tests assert command variants for default, encrypted, multiple OSDs per device, device class, metadata devices, partitions, existing LVs, multipath, by-id/by-path references, and metadata report validation. Parsing tests assert cluster FSID filtering and OSD count. Wipe tests ensure only desired stale devices are zapped and that encrypted mapper devices resolve to backing devices.

## State and Persistence
The tests use temporary files for `lvmConfPath`, temporary ceph config dirs, environment variables such as OSD store type and device class, and package-level globals like `cvLogDir`. They simulate persistent device state through `clusterd.Context.Devices` and fake ceph-volume JSON rather than touching real disks. Some tests mutate package variables and environment, so isolation discipline matters.

## Dependencies and Integration Points
The suite connects OSD volume code with Rook config types, Ceph version structs, operator OSD `OSDInfo`, store config, executor test mocks, `sys.LocalDisk`, and fake Kubernetes clients for raw OSD device class population. It protects many command contracts that activation, replacement, and cleanup code depend on.

## Risks
The tests are broad but brittle because many assertions depend on exact argument indexes. They do not execute real ceph-volume or validate actual device effects. Environment-derived production globals initialized at package load are hard to vary reliably in tests. Several cases use large in-test fixtures, so maintaining fixture accuracy with new ceph-volume versions is important.

## Test Signals
Strong signals include raw/LVM mode selection, metadata-device command formation, report JSON validation, foreign cluster filtering, destructive zap sequence, DevLinks matching, and per-device class override behavior. Useful additions would include explicit `UpdateLVMConfig()` content assertions and failure-path coverage for malformed raw JSON, failed wipefs, and closed encrypted PVC reopening.
