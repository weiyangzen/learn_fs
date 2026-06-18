# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-st.c

## Purpose
This file supports STMicroelectronics SoC SDHCI controllers, especially STiH407 FlashSS/Arasan integration. It programs controller configuration registers, optional top-level delay/DLL registers, clocks, reset control, UHS signaling, capability reads, and system sleep PM around the common `sdhci-pltfm` helper.

## Important APIs, Types, And Functions
`struct st_mmc_platform_data` stores reset control, optional interconnect clock, and optional top delay MMIO. `st_mmcss_cconfig()` programs FlashSS CCONFIG registers based on DT-compatible and MMC capabilities. `st_mmcss_set_static_delay()`, `st_mmcss_set_dll()`, `st_mmcss_lock_dll()`, and `sdhci_st_set_dll_for_clock()` manage static/dynamic delay and DLL lock. `sdhci_st_set_uhs_signaling()` selects UHS mode bits and delay behavior. `sdhci_st_readl()` masks 3.0 V support from capabilities. Lifecycle functions are `sdhci_st_probe()`, `sdhci_st_remove()`, `sdhci_st_suspend()`, and `sdhci_st_resume()`.

## Control Flow
Probe gets the mandatory `mmc` clock, optional `icn` clock, optional reset control, deasserts reset, initializes an SDHCI platform host with ST quirks, parses MMC OF data, enables clocks, maps optional `top-mmc-delay`, stores clock/reset data, programs FlashSS CCONFIG for STiH407, adds the host, and logs host/vendor version. On failure it disables clocks and asserts reset. Remove delegates to `sdhci_pltfm_remove()`, disables clocks, and asserts reset.

UHS signaling first clears speed-mode bits, applies static delay for each high-speed mode, sets VDD 1.8 V for UHS/HS200 paths, invokes DLL setup/lock for SDR50/SDR104/HS200 when host clock exceeds 90 MHz, warns on lock failure, then writes host-control2. `st_mmcss_cconfig()` sets base clock frequency from `max-frequency`, marks eMMC slot type or configures card-detect output, and advertises SDR50/SDR104/DDR50 bits according to MMC caps.

## State And Persistence
Persistent state includes prepared clocks, reset-control state, optional top-delay mapping, and CCONFIG/delay registers. Suspend marks retune if needed, suspends host, asserts reset, and disables clocks. Resume reenables clocks, deasserts reset, reprograms CCONFIG, and resumes the host.

## Dependencies And Integration Points
The driver depends on `sdhci-pltfm`, reset framework, clock framework, OF properties/resources, and MMC capability parsing. It matches `st,sdhci` and contains a special compatibility path for `st,sdhci-stih407`.

## Risks
DLL lock waits up to one second using jiffies and only warns when UHS signaling cannot lock, so cards may later fail with data errors. Optional `top-mmc-delay` absence silently disables delay programming. Capability masking removes 3.0 V support in reads, which affects core voltage decisions. Resume must replay CCONFIG after reset or capabilities/delay behavior can be stale.

## Test Signals
Test STiH407 and generic ST compatible systems, max-frequency selection at 50/100/200 MHz, removable versus eMMC CCONFIG, SDR50/SDR104/DDR50 capability exposure, DLL lock success above 90 MHz, reset assertion/deassertion across suspend/resume, and host-version log after probe.
