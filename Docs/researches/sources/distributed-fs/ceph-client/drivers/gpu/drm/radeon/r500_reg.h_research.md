# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r500_reg.h

## Purpose

`r500_reg.h` is a register-definition header for the legacy Radeon R300/R400/R500/RS600/RS690 display and memory-controller blocks. It provides symbolic MMIO and indirect MC register offsets plus bit masks/shifts used by the Radeon KMS driver to program pipe tiling, display controllers, cursors, DAC/TMDS/LVTMA transmitters, panel power sequencing, hardware I2C, HPD GPIOs, interrupts, and pre-R600/AVIVO memory mappings.

## Important APIs, Types, and Definitions

- R300/R400/R500 3D and pipe macros: `R300_GA_POLY_MODE`, `R300_GB_MSPOS0/1`, `R300_RB3D_DSTCACHE_CTLSTAT`, `R300_RB3D_ZCACHE_CTLSTAT`, `R400_GB_PIPE_SELECT`, `R500_DYN_SCLK_PWMEM_PIPE`, `R500_SU_REG_DEST`, `R300_GB_TILE_CONFIG`, and `R300_DST_PIPE_CONFIG`.
- Common command/status registers: `RADEON_CP_STAT`, `RADEON_RBBM_CMDFIFO_ADDR`, `RADEON_RBBM_CMDFIFO_DATA`, and `RADEON_ISYNC_CNTL` describe CP/RBBM synchronization and idle-wait bits.
- RS480/RS600/RS690 memory-controller and GART definitions: `RS480_NB_MC_INDEX/DATA`, `RS690_MCCFG_*`, `RS690_MC_INDEX/DATA/STATUS`, `RS600_MC_INDEX/DATA`, `RS600_MC_PT0_*`, `RS600_*_GART_*`, and associated aperture/page-table/cache bits.
- RV515/R520 memory-controller definitions: `RV515_MC_FB_LOCATION`, `R520_MC_FB_LOCATION`, `R520_MC_AGP_LOCATION`, `R520_MC_STATUS`, `R520_MC_CNTL0`, and channel-width masks used by RV515/R520 initialization.
- AVIVO display definitions: `AVIVO_D1CRTC_*`, `AVIVO_D2CRTC_*`, `AVIVO_D1GRPH_*`, `AVIVO_D2GRPH_*`, cursor registers, LUT registers, scaler/viewport/blank/vline status registers, and CRTC master controls.
- Encoder/output definitions: `AVIVO_DACA_*`, `AVIVO_DACB_*`, `AVIVO_TMDSA_*`, `AVIVO_LVTMA_*`, `R500_LVTMA_*`, `R600_LVTMA_*`, and bit-depth/dither flags.
- Panel/I2C/HPD/interrupt definitions: `AVIVO_LVTMA_PWRSEQ_*`, `AVIVO_LVDS_BACKLIGHT_CNTL`, `AVIVO_DC_I2C_*`, `AVIVO_DC_GPIO_DDC*`, `AVIVO_DC_GPIO_HPD_*`, and `AVIVO_DISP_INTERRUPT_STATUS`.

## Control Flow

This header has no runtime control flow. Its values are consumed by C implementation files through register-access macros such as `RREG32`, `WREG32`, `RREG32_MC`, `WREG32_MC`, and PLL/PCIe helper wrappers. Control flow is therefore indirect: display setup code selects CRTC/GRPH/cursor/transmitter offsets, memory setup code programs MC aperture and GART registers, and interrupt code checks/acks status bits defined here.

## State and Persistence Behavior

The state represented by this file lives in GPU hardware registers. Writes to MC aperture, display, DAC/TMDS/LVTMA, I2C, HPD, cache, and interrupt registers persist until overwritten by the driver, firmware, suspend/resume paths, or GPU reset. The header itself stores no state and declares no functions, but changing a macro changes the hardware contract for all call sites that include it.

## Dependencies and Integration Points

- Integrated by Radeon ASIC-specific code such as RV515/R520 setup, RS600/RS690 memory-controller code, AVIVO display mode-setting, hardware I2C, hotplug, and interrupt handling.
- Shares naming and bitfield conventions with generated-style headers such as `r520d.h` and `r600d.h`, but many entries here are hand-maintained legacy macros.
- Relies on the broader Radeon register access layer to route normal MMIO versus indexed MC register access correctly.
- Display mode code uses the AVIVO D1/D2 offset pattern to address the first and second CRTC blocks.

## Risks and Edge Cases

- Several definitions are legacy and hand-written; typos in names or values are easy to propagate because there is no type checking. Examples include misspelled `TRIANGE` names and an incomplete-looking `AVIVO_DACB_POWERDOWN_RED` macro without an explicit value.
- Duplicate or overlapping definitions such as `RS600_MC_STATUS` can hide earlier values and make future maintenance error-prone.
- R500 and R600 LVTMA register aliases differ by offset; choosing the wrong macro for an ASIC family can program the wrong transmitter register.
- Register writes are often read-modify-write at call sites, so incorrect clear masks or shifts can corrupt adjacent hardware fields.
- Some comments explicitly mark uncertainty, for example TMDS clock/dither behavior, so dependent code should be treated as hardware-quirk-sensitive.

## Test Signals

- Build coverage should compile all legacy Radeon display and MC paths that include this header to catch macro drift.
- Hardware smoke tests should cover R520/RV515 discrete cards, RS600/RS690 integrated chipsets, single and dual CRTC modes, cursor movement, LUT updates, LVDS panel power/backlight, DAC/TMDS/LVTMA outputs, and hotplug events.
- Suspend/resume tests should verify MC aperture restoration, display reprogramming, and HPD/I2C state after reset.
- Register trace comparisons against known-good kernels are useful when changing offsets or bit masks.
