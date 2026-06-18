# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.h

Purpose: declares debugfs entry plumbing for the PowerVR driver with a no-op fallback when debugfs is disabled.

Important APIs/types: under `CONFIG_DEBUG_FS`, `struct pvr_debugfs_entry` contains a directory name and init callback, and `pvr_debugfs_init()` is declared. Otherwise an inline no-op `pvr_debugfs_init()` is provided.

Control flow and state: debugfs initialization is optional and controlled entirely by configuration.

Dependencies and integration: forward declares DRM minor, PowerVR device, and dentry to keep includes light.

Risks: callers can invoke `pvr_debugfs_init()` unconditionally from driver setup because the no-op fallback exists.

Test signals: build coverage with and without `CONFIG_DEBUG_FS`.
