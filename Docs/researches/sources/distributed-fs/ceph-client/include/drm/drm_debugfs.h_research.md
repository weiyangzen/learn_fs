# sources/distributed-fs/ceph-client/include/drm/drm_debugfs.h

Purpose: Declares the DRM debugfs interface for per-minor and per-device diagnostic files, including driver-supplied show callbacks, GPU virtual-address dumps, and per-client debugfs directories.

Important APIs, types, and functions: Defines `DRM_DEBUGFS_GPUVA_INFO()`, `struct drm_info_list`, `struct drm_info_node`, `struct drm_debugfs_info`, and `struct drm_debugfs_entry`. With `CONFIG_DEBUG_FS`, declares `drm_debugfs_create_files()`, `drm_debugfs_remove_files()`, `drm_debugfs_add_file()`, `drm_debugfs_add_files()`, `drm_debugfs_gpuva_info()`, `drm_debugfs_clients_add()`, and `drm_debugfs_clients_remove()`. Without debugfs, all helpers become no-op stubs returning success or zero.

Control flow: Drivers describe debugfs files with static info arrays or add files dynamically on a `drm_device`. The core instantiates these entries under DRM debugfs roots and passes a `seq_file` whose private data identifies the minor or device entry. GPUVA dump entries use the macro and call `drm_debugfs_gpuva_info()` from their show callback. Client add/remove hooks maintain per-file debugfs directories when debugfs is enabled.

State and persistence: State is runtime-only debugfs directory/file metadata linked from minors or devices. No information persists after unregister or unmounting debugfs. Stub builds intentionally drop debugfs behavior while preserving call-site compilation.

Dependencies and integration points: Depends on Linux debugfs, `seq_file`, DRM minors, DRM devices, DRM files, and `drm_gpuvm`. It integrates with `drm_driver.debugfs_init`, CRTC/encoder late debugfs hooks, GPUVA-enabled GEM drivers, and per-client accounting/debug views.

Risks and test signals: Risks include show callbacks dereferencing torn-down device state, registering duplicate names, assuming debugfs exists in non-debugfs builds, leaking entries on unregister, and exposing device-private data on render nodes where policy discourages it. Test with `CONFIG_DEBUG_FS=y/n`, primary and render minors, device unregister while files are open, GPUVA dump output, and client debugfs creation/removal on open/close.
