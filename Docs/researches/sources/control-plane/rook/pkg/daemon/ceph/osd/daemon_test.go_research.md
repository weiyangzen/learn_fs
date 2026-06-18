# sources/control-plane/rook/pkg/daemon/ceph/osd/daemon_test.go

This large test file exercises OSD daemon helper behavior, especially device discovery and filtering.

`TestGetOsdUUID` creates temporary files containing only the BlueStore signature, signature plus UUID, no signature, unreadable content, and a missing path. It verifies UUID extraction and error behavior for old `lsblk` compatibility detection. `TestAvailableDevices` configures a mock executor for `lsblk`, `blkid`, `udevadm`, `dmsetup`, `ceph-volume inventory`, LVM list, and raw list. It checks use-all-devices, no devices, regex filters, exact devices, LVM selection restrictions, metadata devices, device path filters, persistent `/dev/disk` links, PVC-backed devices, raw OSD re-detection, and loop-device handling. `TestGetVolumeGroupName` validates parsing of `/dev/<vg>/<lv>`.

State is mocked host inventory plus temporary files. Integration points include sys device helpers, ceph-volume output parsing from other OSD test fixtures, Ceph version gates, and environment `CEPH_VOLUME_ALLOW_LOOP_DEVICES`.

Risks captured are broad but still unit-level: real udev/ceph-volume quirks, global mutation of `getOsdUUID`, status ConfigMap updates, provisioning side effects, and SIGTERM handling are not fully simulated.
