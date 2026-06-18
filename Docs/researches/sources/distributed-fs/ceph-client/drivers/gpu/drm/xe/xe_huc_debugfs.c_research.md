# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc_debugfs.c

Purpose: registers HuC debugfs reporting under a GT/uC debugfs parent.

Important functions: `xe_huc_debugfs_register`, local `huc_info`, `node_to_huc`, and helpers to reach GT/device from `struct xe_huc`.

Control flow: registration DRM-managed allocates a copy of the static `drm_info_list`, stores the HuC pointer in each entry, and creates `huc_info`. Reads acquire PM runtime with `guard(xe_pm_runtime)` and call `xe_huc_print_info`.

State/persistence: no persistent state beyond the DRM-managed copied info list and per-entry `data` pointer.

Dependencies/integration: uses DRM debugfs helpers, `xe_huc_print_info`, PM runtime, and GT/HuC embedding.

Risks/test signals: missing allocation silently skips debugfs. Test debugfs read with runtime suspended/resumed and with HuC disabled/enabled.
