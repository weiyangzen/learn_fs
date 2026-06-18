# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_sysfs.c

Purpose: creates simple read-only sysfs attributes for AMD XDNA accel devices.

Important APIs/functions: `vbnv_show()` returns the static device vbnv string, `device_type_show()` returns the UAPI device type, and `fw_version_show()` returns `major.minor.sub.build` firmware version queried during hardware startup. `amdxdna_sysfs_init()` creates the attribute group on the DRM device kobject; `amdxdna_sysfs_fini()` removes it.

Control flow: PCI probe initializes sysfs after hardware init and before DRM registration; error and remove paths call fini.

State and persistence: sysfs values are derived from `amdxdna_dev_info` and `xdna->fw_ver`. Files exist only while the device is registered.

Dependencies: Linux sysfs device attributes, DRM device, AMD XDNA device info and firmware version state.

Risks: `fw_version` is meaningful only after successful firmware query. `sprintf()` is used with fixed simple values; future longer attributes should prefer bounded helpers.

Test signals: sysfs file presence after probe, removal after unbind, expected values for each supported NPU revision, and behavior when firmware query/init fails before sysfs creation.
