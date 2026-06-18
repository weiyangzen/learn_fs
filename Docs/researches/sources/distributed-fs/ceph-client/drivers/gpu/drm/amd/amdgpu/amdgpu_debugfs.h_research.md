# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_debugfs.h

Purpose: this header declares the amdgpu debugfs initialization hooks used by device setup, subsystem-specific debug providers, fence/firmware/GEM helpers, VM/client setup, and usermode queue diagnostics.

Important APIs/types: it forward-declares `struct amdgpu_usermode_queue` and declares `amdgpu_debugfs_regs_init()`, `amdgpu_debugfs_init()`, `amdgpu_debugfs_fini()`, `amdgpu_debugfs_fence_init()`, `amdgpu_debugfs_firmware_init()`, `amdgpu_debugfs_gem_init()`, `amdgpu_debugfs_mes_event_log_init()`, `amdgpu_debugfs_vm_init()`, and `amdgpu_debugfs_userq_init()`.

Control flow and integration: device initialization calls `amdgpu_debugfs_init()` after DRM primary minor/debugfs root setup. That function calls the subsystem init declarations here and registers per-device files. Per-open VM and user queue setup use the client-level init functions to create entries under `file->debugfs_client`.

State and persistence: the header has no state. Declared functions create debugfs dentries or no-op depending on config/implementation. Debugfs state is kernel runtime state only.

Dependencies: users must include this with definitions for `struct amdgpu_device` and `struct drm_file` available. The concrete definitions are spread across `amdgpu_debugfs.c` and other amdgpu debugfs provider files.

Risks: declarations here cover functions not implemented in `amdgpu_debugfs.c` itself, so missing provider objects would become link failures. Publicly declaring `amdgpu_debugfs_fini()` requires matching lifecycle behavior elsewhere. Because debugfs is optional, callers must tolerate no-op implementations where provided.

Test signals: `CONFIG_DEBUG_FS=y/n` builds, link coverage for every declared provider, device probe/remove debugfs lifecycle tests, and per-client debugfs creation tests for VM/user queue entries.
