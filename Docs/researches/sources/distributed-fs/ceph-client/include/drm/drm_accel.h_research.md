# sources/distributed-fs/ceph-client/include/drm/drm_accel.h

Purpose: DRM accelerator minor interface, default accelerator file operations, and core lifecycle hooks for accelerator-class DRM drivers.

Important APIs/types/functions: `ACCEL_MAJOR`, `ACCEL_MAX_MINORS`, `DRM_ACCEL_FOPS`, `DEFINE_DRM_ACCEL_FOPS`, enabled-build `accel_minors_xa`, `accel_core_init`, `accel_core_exit`, `accel_set_device_instance_params`, `accel_open`, and `accel_debugfs_register`, plus disabled-build stubs.

Control flow: accelerator drivers define per-driver file operations with `DEFINE_DRM_ACCEL_FOPS`, use accel core minor management, route opens through `accel_open`, and share standard DRM ioctl/release/poll/read/GEM mmap behavior. Disabled builds let DRM core init continue successfully.

State and persistence: enabled builds maintain global `accel_minors_xa`; file/device state follows DRM runtime lifetime. No persistent storage exists.

Dependencies and integration points: DRM file infrastructure, GEM mmap, xarray, device model, debugfs, `CONFIG_DRM_ACCEL`, and accelerator drivers.

Risks and test signals: sharing file-op structures despite `THIS_MODULE`, direct use of disabled `accel_open`, minor exhaustion, debugfs lifetime issues, and display-node assumption leaks are risks. Test enabled/disabled builds, module refcounts on open, minor limits, open/release/ioctl/mmap, debugfs, and instance naming.
