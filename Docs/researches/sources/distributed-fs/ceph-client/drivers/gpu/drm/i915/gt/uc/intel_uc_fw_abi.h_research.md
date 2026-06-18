# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/intel_uc_fw_abi.h

Purpose: defines the CSS firmware header ABI consumed by the i915 uC firmware loader for GuC and HuC DMA-loaded images.

Important APIs/types/functions: `struct uc_css_header` describes module metadata, header and component sizes in dwords, date/time fields, software version fields, `vf_version`, optional GuC private data size, and header info. Macros define bit fields for CSS date, time, and `sw_version`, including `CSS_SW_VERSION_UC_MAJOR`, `CSS_SW_VERSION_UC_MINOR`, and `CSS_SW_VERSION_UC_PATCH`. A `static_assert` fixes the ABI structure size at 128 bytes.

Control flow and state: this file has no runtime control flow. Loader code reads this packed structure directly from firmware bytes, validates that header, uCode, and RSA data are present, calculates upload and RSA sizes, and extracts firmware and GuC submission versions.

Dependencies and integration points: depends only on Linux integer types and build assertions. It is included by `intel_uc_fw.h` and `intel_uc_fw.c`; GSC-managed HuC/GSC blobs use separate manifest parsing but may still contain CSS data at a DMA start offset.

Risks and test signals: every field is part of a binary contract with firmware files, so packing, size, and dword-based arithmetic are critical. Test signals include rejecting too-small blobs, mismatched header size calculations, truncated uCode/RSA payloads, version extraction correctness, and build failures if the struct layout changes unexpectedly.
