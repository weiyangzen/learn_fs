# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_debugfs.c

Purpose: creates PowerVR debugfs entries under the DRM minor debugfs root.

Important APIs/functions: static `pvr_debugfs_entries[]` currently contains one entry, `"pvr_fw"`, initialized by `pvr_fw_trace_debugfs_init`. `pvr_debugfs_init(struct drm_minor *minor)` creates a directory for each entry and calls its init callback with `pvr_dev` and the directory.

Control flow and state: called through the DRM driver debugfs callback. It relies on DRM to clean up all children under `minor->debugfs_root`, so no explicit fini exists.

Dependencies and integration: depends on DRM minor/device, debugfs, dentry, PowerVR device conversion, and firmware trace debugfs support.

Risks: debugfs directory creation failures are warnings only; the driver continues without that diagnostic tree. Additional entries should avoid requiring explicit teardown.

Test signals: with `CONFIG_DEBUG_FS`, `/sys/kernel/debug/dri/*/pvr_fw` should appear for registered devices and firmware trace files should initialize below it.
