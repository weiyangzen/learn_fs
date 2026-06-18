# sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_core.c

## Purpose
`renesas_sdhi_core.c` implements the common Renesas SDHI host logic on top of the TMIO MMC core. It handles clock selection, SDBUF bus width, signal voltage switching, SCC tuning and HS400 adjustment, reset behavior, SDIO retune handling, a local `vqmmc` regulator, common probe/remove, and suspend/resume.

## Important APIs, Types, And Functions
Exported APIs are `renesas_sdhi_probe()`, `renesas_sdhi_remove()`, `renesas_sdhi_suspend()`, and `renesas_sdhi_resume()`. Core callbacks installed into `tmio_mmc_host` include `renesas_sdhi_clk_enable()`, `renesas_sdhi_clk_disable()`, `renesas_sdhi_set_clock()`, `renesas_sdhi_reset()`, `renesas_sdhi_write16_hook()`, `renesas_sdhi_multi_io_quirk()`, `renesas_sdhi_check_scc_error()`, and tuning hooks such as `renesas_sdhi_execute_tuning()`, `renesas_sdhi_prepare_hs400_tuning()`, and `renesas_sdhi_hs400_complete()`. Regulator ops expose SDHI voltage selection through `CTL_SD_STATUS`.

## Control Flow
Probe allocates `struct renesas_sdhi`, obtains clocks/reset/pinctrl/mux, allocates a TMIO host, applies OF/platform data and quirks, enables clocks, optionally registers a child `vqmmc` regulator, discovers version/SCC support, installs TMIO callbacks, requests IRQs, and calls `tmio_mmc_host_probe()`. Clock setting updates parent clocks, computes TMIO dividers, and toggles SCLK. Tuning initializes SCC, runs CMD19 twice per tap, selects the longest passing tap window, and configures correction. Request-time hooks can adjust HS400 calibration before status commands and request retuning on SCC errors.

## State And Persistence
Runtime state includes clock handles/rates, SCC tap bitmaps and selected tap, HS400 calibration flags, card SDIO classification, reset/regulator handles, and TMIO private data. This is volatile and restored through PM and reset paths, not persisted.

## Dependencies And Integration Points
The core depends on TMIO MMC internals, Renesas SDHI registers, clocks, resets, pinctrl, mux controls, regulators, OF/platform data, IRQs, runtime PM domains, and the DMA ops supplied by front-end drivers.

## Risks And Test Signals
Risks include clock rounding errors, SCC tap selection on marginal boards, HS400 bad-tap/calibration quirks, SDIO IRQ retune interactions, reset preserving regulator state, and version-dependent block-count/CBSY behavior. Test signals include Gen2/Gen3 probe, clock rates and actual clock reporting, voltage switch with pinctrl, SDR104/HS200/HS400 tuning, SDIO IRQ retune, local regulator operation, reset/suspend/resume, and TMIO IRQ-driven request success.
