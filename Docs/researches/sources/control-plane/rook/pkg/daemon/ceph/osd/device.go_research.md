# sources/control-plane/rook/pkg/daemon/ceph/osd/device.go

This file defines OSD device data structures and device-class selection logic.

`Device` is a small JSON-bound device descriptor. `DesiredDevice` carries user configuration such as name/filter, OSDs per device, metadata device, database size, device class, initial weight, and filter flags. `DeviceOsdMapping` maps device names to `DeviceOsdIDEntry`; its `String()` marshals the mapping to JSON for logging/debugging. `DeviceOsdIDEntry` tracks data OSD ID, metadata OSD IDs, matched config, persistent paths, low-level `sys.LocalDisk` info, and restore state.

`DesiredDevice.UpdateDeviceClass()` applies priority order for CRUSH device class: explicit device-level value first, PVC-backed `ROOK_OSD_CRUSH_DEVICE_CLASS` environment next, non-PVC store config next, and finally `sys.GetDiskDeviceType()` from sysfs-derived disk data. This feeds `getAvailableDevices()` and later ceph-volume configuration.

State is in-memory, except for environment reads in PVC mode. Dependencies include operator OSD env var names, storage config, and sys disk classification. `device_test.go` covers class priority and bootstrap keyring behavior from `init.go`. Risks include default classification depending on incomplete `LocalDisk` data and using JSON marshal while ignoring errors in `String()`.
