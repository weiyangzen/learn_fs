<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.h

## Purpose
`radeon_ucode.h` defines firmware size/address constants and packed header layouts shared by Radeon firmware loaders. It covers CP, MEC, RLC, MC, SDMA, and SMC microcode families across R600 through CIK-era chips.

## Important APIs, types, and definitions
The header contains many firmware size constants such as `R600_PFP_UCODE_SIZE`, `CIK_MEC_UCODE_SIZE`, `BONAIRE_MC2_UCODE_SIZE`, and `CIK_SDMA_UCODE_SIZE`, plus SMC start/size constants for RV7xx, Evergreen, Northern Islands, Southern Islands, Bonaire, and Hawaii variants. Header structures include `common_firmware_header`, `mc_firmware_header_v1_0`, `smc_firmware_header_v1_0`, `gfx_firmware_header_v1_0`, `rlc_firmware_header_v1_0`, `sdma_firmware_header_v1_0`, and `union radeon_firmware_header`. It declares the ucode print helpers and `radeon_ucode_validate`.

## Control flow
The file has no executable flow. Loader code uses constants to validate legacy firmware payload lengths and uses the header structures to parse newer binary firmware headers in a byte-order-aware way.

## State, dependencies, and integration points
The header owns no runtime state. It is consumed by `radeon_ucode.c`, UVD, SDMA, MC, CP, RLC, SMC, and ASIC-specific firmware loaders. It assumes Linux integer types and `struct firmware` are visible to consumers.

## Risks and test signals
Firmware constants must match the blobs shipped by linux-firmware; incorrect values cause firmware load failures or truncated uploads. Structure layout drift affects every parser of new-style firmware. Test signals are successful firmware request/validation across supported ASICs, correct printed versions/features, and absence of microcode load errors during device probe/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_ucode.h -->
