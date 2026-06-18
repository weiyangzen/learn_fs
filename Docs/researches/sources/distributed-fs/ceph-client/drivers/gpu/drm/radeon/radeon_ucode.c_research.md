<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.c

## Purpose
`radeon_ucode.c` provides firmware-header diagnostics and validation for Radeon microcode blobs. It understands the common header and IP-specific v1.0 header extensions for MC, SMC, GFX, RLC, and SDMA firmware.

## Important APIs, types, and functions
The shared helper `radeon_ucode_print_common_hdr` prints common header fields. Public printers are `radeon_ucode_print_mc_hdr`, `radeon_ucode_print_smc_hdr`, `radeon_ucode_print_gfx_hdr`, `radeon_ucode_print_rlc_hdr`, and `radeon_ucode_print_sdma_hdr`. `radeon_ucode_validate` checks that the firmware file size matches the little-endian `size_bytes` value in the common header.

## Control flow
Each print function reads header major/minor version, logs common fields, then uses `container_of` to access the corresponding extended header when `version_major == 1`. Unknown versions are logged as errors. Validation performs a simple total-size check and returns `0` or `-EINVAL`.

## State, dependencies, and integration points
The file owns no persistent state. It depends on Linux firmware objects, endian conversion helpers, DRM logging, and structures from `radeon_ucode.h`. UVD, SDMA, MC, GFX, RLC, and power-management firmware loading paths can call validation or header printers before copying microcode to hardware.

## Risks and test signals
Validation is intentionally shallow: it does not verify CRC, payload offsets, or minimum header size before dereferencing, so callers must only pass firmware buffers large enough for the common header. Risks include accepting corrupt blobs with matching size or rejecting valid future header formats in diagnostics. Test signals include firmware load success, expected debug logs for known blobs, and graceful `-EINVAL` on size mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.c -->
