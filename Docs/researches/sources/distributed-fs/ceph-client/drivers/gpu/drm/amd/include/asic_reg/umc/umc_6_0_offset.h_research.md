# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_6_0_offset.h

## Purpose
This generated header defines UMC 6.0 register offsets for four memory channels. The covered registers are ECC control, UMC configuration, and local capability. It lets callers build per-channel register addresses without hard-coding the channel stride.

## Important APIs, Types, and Functions
The public macros are `mmUMCCH0_0_EccCtrl` through `mmUMCCH3_0_EccCtrl`, `mmUMCCH0_0_UMC_CONFIG` through `mmUMCCH3_0_UMC_CONFIG`, and `mmUMCCH0_0_UmcLocalCap` through `mmUMCCH3_0_UmcLocalCap`, each with `_BASE_IDX 0`. Channel spacing is visible in the offsets: ECC control at `0x0053`, `0x0853`, `0x1053`, and `0x1853`; UMC config at `0x0040`, `0x0840`, `0x1040`, and `0x1840`; local capability at `0x0306`, `0x0b06`, `0x1306`, and `0x1b06`.

## Control Flow
There is no code flow in the header. Consumers include the file or related generated headers and use these symbols with SOC15 register address helpers. The pattern supports loops over channels by selecting the channel-specific macro or by using an equivalent stride in calling code.

## State and Persistence Behavior
The header has no state. It names hardware state for ECC enablement, DRAM-ready status, and ECC capability/disablement. Those states persist in UMC registers and are changed by firmware, memory initialization, RAS setup, and GPU reset paths.

## Dependencies and Integration Points
It pairs with `umc_6_0_sh_mask.h` for field extraction and `umc_6_0_default.h` for reset values. Nearby AMDGPU code includes `umc_6_0_sh_mask.h` in `gmc_v9_0.c`, and later generated UMC 6.x headers extend the same register concepts for RAS flows. Consumers depend on SOC15 register offset macros and MMIO accessors.

## Risks
Offsets are hardware-contract data. A wrong channel offset can read the wrong channel's ECC state or write to the wrong UMC register. Because this header enumerates only four channels and later UMC variants use different channel topology, code must not reuse these macros for incompatible ASICs.

## Test Signals
Build coverage should include ASIC paths that include UMC 6.0 register headers. Runtime signals include correct channel-by-channel ECC enable state, DRAM-ready reads, and local capability reads on matching hardware. Register dumps can verify the four-channel offset stride.
