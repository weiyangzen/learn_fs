## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.h

Purpose: declares the GuC firmware upload entry point.

Important APIs, types, and functions:
- Forward declares `struct intel_guc`.
- Exposes `int intel_guc_fw_upload(struct intel_guc *guc)`.

Control flow:
- Higher-level UC initialization, resume, or reset code calls `intel_guc_fw_upload()` after firmware fetch/preparation has succeeded.

State and persistence:
- No header-owned state. The implementation updates GuC firmware status and hardware registers.

Dependencies and integration points:
- Provides a narrow boundary between generic UC firmware orchestration and GuC-specific upload/status logic.

Risks:
- Minimal header risk; callers must interpret nonzero returns as firmware load failure and trigger the correct fallback/reset path.

Test signals:
- Build coverage and load-path tests that mock or exercise `intel_guc_fw_upload()`.
