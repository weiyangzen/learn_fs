# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.h

Purpose: Register definition header for the Rockchip PDM capture controller.

Important APIs, types, and functions: Defines register offsets for system control, CTRL0/CTRL1, clock, HPF, FIFO, DMA, interrupts, RX FIFO data, data valid, and version. Bit macros cover RX start/stop/clear, PDM path enables, left/right-justified mode, sample-rate selector, valid data width, fractional divider numerator/denominator, path routing, clock ratios, clock polarity, downsample/CIC ratios, HPF controls, and DMA read threshold.

Control flow: No executable code. `rockchip_pdm.c` uses these macros for `regmap_update_bits` and DMA address setup.

State and persistence: No state; constants must match hardware register layout for all supported PDM versions.

Dependencies and integration: Uses Linux `BIT`/`GENMASK` from including source. Integrates with regmap read/write filters and hardware-specific code paths in the PDM driver.

Risks and edge cases: Macros such as `PDM_VDW(X)` and `PDM_DMA_RDL(X)` assume nonzero inputs. `PDM_CLK_CTRL` shares low bits between DS ratio and CIC ratio meanings depending on hardware version, so callers must select the correct mask.

Test signals: Build and register-dump validation during sample-rate/channel tests should confirm expected CTRL0, CLK_CTRL, HPF, and DMA_CTRL fields.
