# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt2701/mt2701-afe-pcm.c

## Purpose

This is the MT2701/MT7622 AFE platform driver. It registers PCM FE DAIs, I2S and BT merge BE DAIs, DAPM interconnect routes, memory-interface metadata, IRQ metadata, runtime PM hooks, and the platform driver binding for `"mediatek,mt2701-audio"` and `"mediatek,mt7622-audio"`.

## Important APIs, Types, and Functions

- `mt2701_afe_hardware` defines PCM buffer/period/format capabilities.
- `mt2701_afe_i2s_rates`, `mt2701_afe_i2s_fs()`, `mt2701_memif_fs()`, and `mt2701_irq_fs()` translate sample rates to hardware fields.
- I2S DAI ops: `mt2701_afe_i2s_startup()`, `mt2701_afe_i2s_prepare()`, `mt2701_afe_i2s_shutdown()`, and `mt2701_afe_i2s_set_sysclk()`.
- BT merge ops: `mt2701_btmrg_startup()`, `mt2701_btmrg_hw_params()`, and `mt2701_btmrg_shutdown()`.
- FE ops specialize the common MediaTek FE helpers for single DL and DLM multichannel constraints.
- `mt2701_asys_isr()` clears ASYS IRQ status and calls `snd_pcm_period_elapsed()`.
- `mt2701_afe_pcm_dev_probe()` allocates `mtk_base_afe`, memifs, IRQs, I2S paths, clocks, and registers ASoC components.

## Control Flow

Probe allocates private state, selects SoC variant data, maps the parent syscon regmap, requests the named `asys` IRQ, initializes memif/IRQ/I2S arrays, configures clock handles, enables runtime PM, then registers the common DMA platform component and the MT2701 DAI component. FE startup delegates to common code after enforcing DL/DLM exclusivity. I2S startup enables MCLK; prepare checks occupancy, programs MCLK, configures ASRC/I2S registers, resets the I2S block, and enables the path. Capture also enables the paired output path. Shutdown decrements path refcounts, disables paths when the count reaches zero, and disables MCLK. Runtime PM delegates global clock enable/disable to the clock-control file.

## State and Persistence Behavior

State is held in `mt2701_afe_private`, `mt2701_i2s_path`, `afe->memif`, and `afe->irqs`. `occupied[]` prevents simultaneous same-direction users on one I2S path; `on[]` reference-counts actual hardware enable. `mrg_enable[]` keeps BT merge clocking alive while either stream direction is active. `mt2701_afe_backup_list` identifies registers saved/restored by common suspend/resume helpers.

## Dependencies and Integration Points

The file depends on syscon parent regmap, the `asys` IRQ, the clock-control helper file, common MediaTek FE/platform helpers, ASoC DAPM/DPCM, and machine drivers that reference CPU DAI names like `PCMO0`, `PCM_multi`, `PCM0`, `I2S0`, and `MRG BT`.

## Risks and Edge Cases

I2S path counters are not explicitly locked in this file, so correctness depends on ASoC serialization. Unsupported sample rates return `-EINVAL`, but callers must propagate all `mt2701_i2s_path_enable()` failures. Capture's automatic output-path enable makes shutdown symmetry critical. BT merge only supports 8/16 kHz. DLM disables/enables agents for all single DL memifs due to hardware coupling and rejects concurrent single-DL playback.

## Test Signals

Test normal playback/capture, simultaneous capture/playback on the same I2S, DLM multichannel playback, rejection of concurrent DLM/single-DL streams, BT SCO 8/16 kHz, runtime suspend/resume, and IRQ period-elapsed delivery.
