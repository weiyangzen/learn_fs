# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_huc_fw.h

## Purpose

This header exposes HuC firmware upload, GSC load/auth, GSCCS authentication, and GSC-binary parsing helpers.

## APIs, Dependencies, Risks, And Test Signals

Declared APIs are `intel_huc_fw_load_and_auth_via_gsc()`, `intel_huc_fw_auth_via_gsccs()`, `intel_huc_fw_upload()`, and `intel_huc_fw_get_binary_info()`. It forward-declares `struct intel_huc` and `struct intel_uc_fw` and includes `linux/types.h` for `size_t`. The risk is lifecycle misuse: callers must allocate `huc->heci_pkt` before GSCCS auth and fetch firmware data before parsing/upload. Build coverage plus legacy DMA upload, DG2 GSC load, and MTL GSC-header parsing/auth are the main signals.
