# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/firmware.c

## Purpose
`firmware.c` loads or exposes the GVT "golden hardware state" firmware used to seed vGPU PCI config space and MMIO state. If a matching firmware blob exists under `i915/gvt`, it verifies and copies the blob into `gvt->firmware`; if not, it creates a sysfs binary attribute so administrators can read out the current hardware state and install it as firmware.

## Important APIs And Functions
The exported lifecycle functions are `intel_gvt_load_firmware()` and `intel_gvt_free_firmware()`. Internal helpers include `expose_firmware_sysfs()`, `clean_firmware_sysfs()`, and `verify_firmware()`. `struct gvt_firmware_header` defines blob metadata: magic, CRC32, version, config/MMIO sizes, offsets, and payload.

## Control Flow
Load allocates buffers for config space and MMIO, builds a firmware path from PCI vendor/device/revision, and calls `request_firmware()`. Missing firmware is not fatal: execution falls through to `expose_firmware_sysfs()` and returns success after exposing a generated blob. If firmware is found, `verify_firmware()` checks magic, version, CRC32 over the payload metadata/data region, expected config/MMIO sizes, and PCI vendor/device/revision fields in the embedded config space. Verified blobs are copied into `firmware->cfg_space` and `firmware->mmio`, released, and marked `firmware_loaded=true`.

## State And Persistence
Runtime state lives in `gvt->firmware.cfg_space`, `gvt->firmware.mmio`, and `firmware_loaded`. The generated sysfs binary attribute stores a vmalloc buffer in `bin_attr_gvt_firmware.private` until cleanup. On-disk persistence is delegated to the Linux firmware loader path; this code never writes the firmware file itself.

## Dependencies And Integration Points
The file uses Linux firmware loading, CRC32, sysfs binary attributes, PCI IDs, and initial i915 vGPU state arrays (`i915->vgpu.initial_cfg_space`, `initial_mmio`). Other GVT initialization code consumes `gvt->firmware` after load. Device cleanup must call `intel_gvt_free_firmware()` to release buffers or remove the sysfs attribute.

## Risks And Edge Cases
If firmware is absent, GVT still returns success but depends on sysfs extraction and later firmware installation for stable future loads. Verification assumes the blob is large enough for the header and offsets; malformed firmware with inconsistent offsets is only partially guarded by size/value checks. The cleanup path removes the sysfs file only when firmware was not loaded, so `firmware_loaded` must be accurate.

## Test Signals
Tests should cover successful firmware load, missing firmware sysfs exposure, invalid CRC/version/device rejection with fallback exposure, correct sysfs blob size and CRC, and cleanup without leaks across both loaded and exposed modes.
