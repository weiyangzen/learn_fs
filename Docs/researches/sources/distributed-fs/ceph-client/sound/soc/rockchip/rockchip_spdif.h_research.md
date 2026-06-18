# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.h

## Purpose
Defines the Rockchip S/PDIF register offsets and bitfield helpers for transfer configuration, DMA control, transfer start/stop, channel-status/user/validity registers, and version register.

## Important APIs, Types, And Functions
The file consists of macros: `SPDIF_CFGR_CLK_DIV()`, clear/channel-status/adjust/halfword/data-width fields, `SPDIF_DMACR_TDE_*`, `SPDIF_DMACR_TDL()`, `SPDIF_XFER_TXS_*`, fixed offsets such as `SPDIF_CFGR`, `SPDIF_DMACR`, `SPDIF_SMPDR`, and indexed offsets `SPDIF_VLDFRn()`, `SPDIF_USRDRn()`, and `SPDIF_CHNSRn()`.

## Control Flow
No executable flow. The driver uses these macros to build regmap masks and values in `hw_params`, trigger handling, and regmap access validation.

## State And Persistence
No software state. The macros describe S/PDIF hardware registers whose state is cached by `rockchip_spdif.c`.

## Dependencies And Integration Points
Requires kernel `BIT()`, `GENMASK()`, and `FIELD_PREP()` definitions from including context. The macros are consumed only by the Rockchip S/PDIF driver.

## Risks And Edge Cases
- `SPDIF_CFGR_CLK_DIV(x)` encodes `x - 1`, so divider zero or underflow would be invalid if caller passed a bad value.
- The data-width mask macro is spelled `SDPIF_CFGR_VDW_MASK`; this is harmless in current code but is a maintainability trap.
- Field macros do not validate hardware-supported ranges.

## Test Signals
Compile tests and register-value trace tests for each supported PCM format and DMA threshold configuration.
