# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-pcm.c

## Purpose
MT8195 ASoC AFE platform driver. It registers the SoC audio component, memory-interface FE DAIs, sub-DAIs for ADDA/eTDM/PCM, the MMIO regmap, runtime PM, interrupt dispatch, DMA hardware constraints, and the static memif/IRQ register description used by the shared MediaTek AFE FE helpers.

## Important APIs, Types, and Functions
The exported platform entry is `mt8195_afe_pcm_dev_probe()` through `module_platform_driver()`, matching `mediatek,mt8195-audio`. `mt8195_afe_fs_timing()` maps sample rates to hardware timing codes and is reused by other MT8195 DAI files. FE operations are implemented by `mt8195_afe_fe_startup()`, `mt8195_afe_fe_shutdown()`, `mt8195_afe_fe_hw_params()`, `mt8195_afe_fe_trigger()`, and simple wrappers around common `mtk_afe_fe_*` helpers. `mt8195_afe_irq_handler()` handles both AFE MCU IRQ and ASYS IRQ clear paths. Runtime PM hooks are `mt8195_afe_runtime_suspend()` and `mt8195_afe_runtime_resume()`.

Important data includes `mt8195_afe_hardware`, `mt8195_memif_dai_driver`, large DAPM widget/route tables for I/O matrix endpoints, `mt8195_memif_controls` for ASYS timing selection, `memif_data`, `irq_data_array`, `mt8195_afe_memif_const_irqs`, `mt8195_afe_regmap_config`, `mt8195_afe_reg_defaults`, and `mt8195_cg_patch`. `struct mtk_dai_memif_priv` stores per-memif ASYS timing selection. `struct mt8195_afe_channel_merge` describes three capture channel-merge blocks used by selected UL memifs.

## Control Flow
Probe initializes reserved memory and a 33-bit DMA mask, allocates `struct mtk_base_afe` plus `struct mt8195_afe_private`, maps the AFE MMIO resource, initializes clocks, resets the audiosys block, initializes locks, allocates IRQ and memif arrays, assigns static memif data and const IRQ usage, requests the platform IRQ, registers ADDA/eTDM/PCM/memif sub-DAIs, combines all sub-DAI descriptors, and stores callbacks for rate mapping and runtime PM. It then looks up optional `mediatek,topckgen`, temporarily bypasses runtime-PM regmap control, resumes the device, creates the regmap, applies clock-gate patches, registers the ASoC component with combined DAIs, writes register defaults, suspends runtime PM, and marks the regcache dirty/cache-only.

Stream startup prepares paired DL8/DL10 clocks where hardware requires both `DL8_DL10_MEM` and `DL8_DL10_AGENT`, delegates to common FE startup, enforces 64-byte buffer alignment, and limits DL7 period size. `hw_params` programs channel-merge blocks for UL9/UL2/UL10 and writes channel count fields for memifs with a channel register before delegating to the common FE parameter path. Trigger enables or disables channel merge around common FE trigger handling and toggles paired DL8/DL10 clocks after START/RESUME or STOP/SUSPEND.

The IRQ handler reads `AFE_IRQ_STATUS` and `AFE_IRQ_MASK`, masks to CPU-enabled IRQs, scans every active memif, maps each memif to its const IRQ data, calls `snd_pcm_period_elapsed()` for matching status bits, and clears ASYS or AFE clear registers separately. Read failures fall back to clearing the known AFE and ASYS IRQ bit masks.

## State and Persistence
Persistent driver state is mostly device-managed: `afe->memif`, `afe->irqs`, `afe->sub_dais`, combined DAI arrays, `afe->regmap`, and `afe_priv->dai_priv[]`. Per-memif `asys_timing_sel` and per-IRQ `asys_timing_sel` are updated by ALSA enum controls. Regmap state is cached with `REGCACHE_FLAT`; runtime suspend disables the main clock, switches the regmap to cache-only, marks it dirty, and disables register read/write clocks. Resume enables register access, syncs the cache, and re-enables the main clock unless `pm_runtime_bypass_reg_ctl` is set during probe.

## Dependencies and Integration Points
Depends on Linux platform, reset, reserved memory, DMA mask, regmap, syscon, runtime PM, IRQ, and ASoC component/DAI/DAPM APIs. It integrates with `mt8195-afe-common.h`, `mt8195-afe-clk.h`, `mt8195-reg.h`, common `mtk-afe-platform-driver.h`, and common FE DAI helpers. Sub-DAI registration is delegated to `mt8195_dai_adda_register()`, `mt8195_dai_etdm_register()`, and `mt8195_dai_pcm_register()`. The machine driver binds to the DAI names exported here, such as `DL2`, `UL4`, `DL_SRC`, `ETDM1_OUT`, and `PCM1`.

## Risks
Many `regmap_update_bits()` calls are unchecked, so hardware programming errors may be silent. The IRQ handler assumes `memif->substream` is valid when IRQ usage is active. Rate mapping has special eTDM-related exceptions for DL10, UL8, and UL3; mismatches with machine routes or eTDM programming can produce wrong IRQ timing. DL8/DL10 paired clock sequencing relies on explicit prepare/enable ordering and a 1 us delay. Probe sets all memif const IRQs occupied, so changes to dynamic IRQ allocation must account for this policy. Runtime PM cache-only transitions are sensitive to register volatility coverage.

## Test Signals
Useful signals are successful probe against `mediatek,mt8195-audio`, component registration with all FE and BE DAI names, suspend/resume regcache sync without register-access faults, playback/capture period interrupts on each memif, ASYS IRQ timing control changes visible in hardware, DL8/DL10 operation with paired clocks, UL9/UL2/UL10 multichannel capture with channel merge, DL7 period constraint enforcement, and `aplay`/`arecord` validation across 44.1 kHz and 48 kHz families up to 384 kHz.
