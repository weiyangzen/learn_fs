# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw.h

Purpose: declares the shared firmware state machine and API used by GuC, HuC, and GSC code to reason about firmware availability, loading, and runtime status.

Important APIs/types/functions: defines `enum intel_uc_fw_status`, `enum intel_uc_fw_type`, `struct intel_uc_fw_ver`, `struct intel_uc_fw_file`, and `struct intel_uc_fw`. Inline helpers include status/type stringification, status-to-errno mapping, `intel_uc_fw_is_supported()`, `intel_uc_fw_is_enabled()`, `intel_uc_fw_is_available()`, `intel_uc_fw_is_loadable()`, `intel_uc_fw_is_loaded()`, `intel_uc_fw_is_running()`, `intel_uc_fw_is_in_error()`, `intel_uc_fw_is_overridden()`, `intel_uc_fw_sanitize()`, and upload-size helpers. It exports the implementation functions from `intel_uc_fw.c`.

Control flow and state: the comment block documents the intended state progression from uninitialized through selected, available, loadable, transferred, and running, with terminal disabled, unsupported, missing, error, init fail, and load fail states. The `status` field is exposed read-only through a union to discourage accidental writes outside `intel_uc_fw_change_status()`. `INTEL_UC_RSVD_GGTT_PER_FW` defines static 2 MiB reserved GGTT slices per firmware.

Dependencies and integration points: includes firmware ABI definitions plus i915 device, GEM, and VMA types. Consumers in GuC/HuC/GSC loaders, reset paths, debugfs, and error handling use these helpers to gate upload, authentication, and cleanup.

Risks and test signals: status comparisons rely on enum ordering, so additions must preserve semantic thresholds. `__intel_uc_fw_status()` asserts that callers do not query an uninitialized object. Tests should cover disabled/unsupported gating, status-to-errno mapping, sanitize after reset, upload-size zero before fetch, and compile coverage with and without `CONFIG_DRM_I915_DEBUG_GUC`.
