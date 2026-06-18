# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dcn401/dcn401_smu14_driver_if.h

## Purpose
This header is a stripped-down SMU 14 driver interface for DCN 4.01 DAL clock-manager needs. It defines PPCLK identifiers, watermark table layout, table type IDs, and the driver interface version checked at runtime.

## Important APIs, Types, And Functions
`SMU14_DRIVER_IF_VERSION` is `0x1`. `PPCLK_e` enumerates clocks with DPM descriptors: GFXCLK, SOCCLK, UCLK, FCLK, DCLK/VCLK, DISPCLK, DPPCLK, DPREFCLK, DCFCLK, DTBCLK, and count. `WatermarkRowGeneric_t` carries a watermark setting and flags. `WatermarksExternal_t` wraps watermark rows plus spare and SMU internal padding. Table IDs include PMFW PPTABLE, combo PPTABLE, watermarks, metrics, driver config, activity monitor coefficients, overdrive, I2C commands, driver info, ECC info, and count.

## Control Flow And Integration
`dcn401_clk_mgr.c` uses `PPCLK_e` to select DPM levels and hardmins. `dcn401_clk_mgr_smu_msg.c` uses `SMU14_DRIVER_IF_VERSION` to validate firmware compatibility and uses `TABLE_WATERMARKS` when transferring the watermark table. Watermark rows are populated by `dcn401_notify_wm_ranges`.

## State And Persistence
The structures describe shared-memory table layout. Firmware reads `WatermarksExternal_t` after the driver writes it into GART memory and sends the DRAM address through SMU messages.

## Dependencies
The header is intentionally standalone apart from fixed-width integer types provided by the compile environment. It is a firmware ABI boundary and must align with SMU expectations.

## Risks
Because it is explicitly stripped down, future code may need fields not present here and duplicate or redefine firmware data elsewhere. `PPCLK_e` numeric values are used in packed SMU parameters and hardmin acknowledgement masks, so changing order is ABI-breaking.

## Test Signals
Version check success, valid watermark transfer, correct DPM queries per `PPCLK_e`, and hardmin status bit matching are the main signals. ABI tests should assert structure sizes and enum numeric values.
