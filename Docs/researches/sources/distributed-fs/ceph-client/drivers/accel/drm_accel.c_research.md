# sources/distributed-fs/ceph-client/drivers/accel/drm_accel.c

Purpose: implements the DRM accel core character-device support used by accelerator drivers under `/dev/accel/*`, including accel class setup, minor lookup/open, common debugfs registration, and stub file-ops replacement.

Important APIs/functions: `accel_core_init()` registers the `accel` sysfs class and major char device with stub fops; `accel_core_exit()` unregisters them and checks the accel minor xarray. `accel_set_device_instance_params()` assigns dev_t, class, and device type for accel minors. `accel_open()` is the real open helper drivers use; it acquires the DRM accel minor, increments open count, shares the DRM anon inode mapping, and calls `drm_open_helper()`. `accel_stub_open()` handles initial char-device opens by replacing fops with the target driver's fops. `accel_debugfs_register()` adds a common `name` debugfs file.

Control flow: core init runs with DRM subsystem initialization. Driver fops typically use `DEFINE_DRM_ACCEL_FOPS` or `accel_open()`, so user opens flow through minor lookup into DRM open callbacks.

State and persistence: global `accel_minors_xa` maps minor numbers to DRM minors. Sysfs class and char device persist while DRM core is loaded.

Dependencies: DRM minor/open/debugfs/auth infrastructure, Linux device classes, xarray, and `ACCEL_MAJOR`.

Risks: minor acquire/release pairing is critical. Stub fops must replace with a valid driver fops reference. Open-count increment is undone only on helper failure.

Test signals: module/core init failure unwind, multiple accel device registration, open invalid minor, debugfs name output, and driver open failure reference cleanup.
