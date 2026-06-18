<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk.go -->
# sources/control-plane/rook/pkg/clusterd/disk.go

Purpose: discovers and filters local block devices for Rook cluster/device orchestration, including lsblk and udev metadata population and policy for supported device types.

Important APIs/types/functions: `supportedDeviceType`, `GetDeviceEmpty`, `ignoreDevice`, `DiscoverDevicesWithFilter`, `deviceMatchWithFilter`, `DiscoverDevices`, `PopulateDeviceInfo`, `PopulateDeviceUdevInfo`, and `getAllowLoopDevices`. Package variables include `isRBD`, `listAllDevices`, and the `dm-` allow pattern.

Control flow: `DiscoverDevicesWithFilter` lists device names, skips RBD devices, applies regex/meta-device filters, populates lsblk properties, best-effort augments udev info, skips parent disks with child partitions, and returns the remaining `LocalDisk` list. `PopulateDeviceInfo` validates type, optionally reads disk UUID, parses size/rotational/read-only fields, and copies path/filesystem/mount metadata. `PopulateDeviceUdevInfo` overlays DEVLINKS, filesystem, serial, vendor, model, and WWN fields.

State and persistence behavior: no persistent writes. It reads host block-device state through the injected executor and environment variable `CEPH_VOLUME_ALLOW_LOOP_DEVICES` to decide loop-device support.

Dependencies and integration points: depends on Rook `exec.Executor`, `sys` lsblk/udev helpers, capnslog, regexp, and OS environment. The resulting `LocalDisk` values feed OSD discovery and cluster context device lists.

Risks: invalid regex filters silently reject devices; `dm-` devices are always allowed for metadata devices; udev failures are logged but not fatal, which can leave filesystem detection less accurate. Parent/child detection assumes lsblk child output length semantics.

Test signals: filter matching, RBD ignore regex, supported type matrix, loop-device env behavior, lsblk parsing, udev overlay precedence, child-device skipping, and error/log behavior for command failures.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk.go -->
