## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_guc_fw.c

Purpose: prepares hardware for GuC firmware transfer, supplies the RSA signature to hardware, uploads GuC ucode, polls load status, decodes boot/ukernel failures, and transitions firmware status to running or load-failed.

Important APIs, types, and functions:
- `guc_prepare_xfer()` programs GuC shim/cache/clock-gating/doorbell registers, Gen9 RC6 timing, and GuC debug register mirroring on newer IP.
- `guc_xfer_rsa_mmio()` copies RSA data into `UOS_RSA_SCRATCH()` registers for smaller keys.
- `guc_xfer_rsa_vma()` writes the GGTT offset of a GuC RSA VMA for larger keys.
- `guc_xfer_rsa()` selects the RSA transfer mode.
- `guc_load_done()` reads `GUC_STATUS`, decodes bootrom and ukernel fields, and tells the wait loop when success or a known terminal failure has occurred.
- `guc_wait_ucode()` polls load completion with retry limits, timing/frequency diagnostics, and detailed error mapping.
- `intel_guc_fw_upload()` is the public load entry point used by driver load, resume, and reset flows.

Control flow:
- Upload begins by programming shim/doorbell state.
- RSA signature is transferred either through MMIO scratch registers or a GGTT-pinned VMA offset.
- `intel_uc_fw_upload()` DMA-loads the CSS header plus uKernel code at offset `0x2000` using `UOS_MOVE`.
- `guc_wait_ucode()` polls `GUC_STATUS` in up to 1-second chunks. Debug GEM builds allow more retries. On success the firmware status becomes `INTEL_UC_FIRMWARE_RUNNING`; on failure it becomes `INTEL_UC_FIRMWARE_LOAD_FAIL`.

State and persistence:
- Hardware registers retain prepared GuC shim/doorbell/debug state.
- Firmware object status is updated through `intel_uc_fw_change_status()`.
- Diagnostics include load time, actual/requested GT frequencies, perf-limit reasons, bootrom status, ukernel status, and scratch EIP for exceptions.

Dependencies and integration points:
- Depends on GT uncore register access, RPS frequency helpers, GuC register definitions, Intel UC firmware upload helpers, and wait utilities.
- Called from higher-level `intel_uc_init_hw()`-style flows.

Risks:
- Load timing is sensitive to GT frequency and thermal/firmware conditions; excessive load time warnings distinguish slow success from failure.
- RSA transfer mode must match platform bootrom expectations.
- Status decoding must track firmware ABI values; unknown failures fall back to `-ENXIO`.
- Hardware register programming differs by graphics version and IP version.

Test signals:
- Firmware load success on cold boot, resume, and GT reset.
- Negative tests for RSA failure, key mismatch, invalid workaround KLV, HWConfig error, and firmware exception status.
- Confirm status transitions and diagnostic logs under timeout and slow-load scenarios.
