# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_spdif.c

## Purpose
Implements the Rockchip S/PDIF playback-only ASoC DAI driver for multiple Rockchip SoCs. It configures IEC958 channel status, S/PDIF data width/alignment, DMA playback, clocks, runtime PM, and RK3288 GRF routing.

## Important APIs, Types, And Functions
- `enum rk_spdif_type` distinguishes compatible-specific behavior.
- `struct rk_spdif_dev` stores device, `mclk`, `hclk`, playback DMA data, and regmap.
- `rk_spdif_hw_params()` builds consumer IEC958 status bytes with `snd_pcm_create_iec958_consumer_hw_params()`, writes channel-status registers, chooses BMC divider and word format, and clears MCLK-domain logic before applying format changes.
- `rk_spdif_trigger()` enables/disables DMA and starts/stops `SPDIF_XFER`.
- `rk_spdif_set_sysclk()` sets `mclk` rate when machine drivers provide one.
- `rk_spdif_probe()` handles RK3288 GRF selection, clocks, MMIO regmap, DMA data, PM setup, dmaengine PCM registration, and component/DAI registration.

## Control Flow
On probe, compatible data is read; RK3288 writes GRF `RK3288_GRF_SOC_CON2` to select the working 8-channel S/PDIF solution. The driver maps registers, creates a flat regmap, sets the playback DMA FIFO address, enables runtime PM, and registers a two-channel playback DAI. During `hw_params`, it writes channel-status frames, enables channel-status embedding, computes 128fs BMC divider from current `mclk`, programs sample format and justification, and pulses `SPDIF_CFGR_CLR`. Trigger start enables transmit DMA and transfer start; trigger stop disables both. Runtime suspend/resume gates clocks and toggles regmap cache-only mode.

## State And Persistence
The driver holds only device-local pointers and DMA configuration. Register state is cached by regmap across runtime suspend. There is no persistent software configuration aside from clock rate set through `.set_sysclk`.

## Dependencies And Integration Points
Uses ASoC DAI callbacks, `snd_dmaengine_pcm`, IEC958 PCM helpers, regmap, runtime PM, clocks, syscon GRF, and `rockchip_spdif.h`. Integrates with DT compatible strings from RK3066 through RK3568 and with DMA through the S/PDIF sample data register.

## Risks And Edge Cases
- `rk_spdif_hw_params()` assumes current `mclk` can derive 128fs and does not validate divider accuracy beyond `DIV_ROUND_CLOSEST`.
- Only playback is supported; capture requests are impossible at DAI capability level.
- RK3288 depends on the `rockchip,grf` phandle.
- The header macro typo `SDPIF_CFGR_VDW_MASK` is consistently used but easy to misread.
- Runtime suspend can drop register writes if callers fail to hold PM references.

## Test Signals
Playback tests for 16/20/24/32-bit formats and 8-192 kHz rates, IEC958 channel-status inspection, RK3288 DT probe with GRF, runtime suspend/resume, and trigger start/stop register traces are the key signals.
