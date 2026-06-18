# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_huc.h

Purpose: public HuC firmware management API and authentication mode enum.

Important APIs/types: `enum xe_huc_auth_types` with GuC and GSC auth, plus init, post-hwconfig init, upload, auth, auth-status query, sanitize, and print functions.

Control flow/state: higher-level GT/uC init code calls these functions in firmware lifecycle order. Auth status is queried through MMIO-backed implementation in the C file.

Dependencies/integration: forward declares `struct xe_huc` and `struct drm_printer`; integrates with uC firmware, GuC, GSC, and debugfs callers.

Risks/test signals: adding auth types requires updating the implementation table. Tests should cover each auth enum and ensure disabled firmware paths return success without touching hardware.
