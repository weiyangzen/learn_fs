# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-pcm.c

## Purpose

`mt8186-afe-pcm.c` is the main MT8186 AFE platform driver. It defines FE memif DAIs, ALSA PCM operations, controls, DAPM widgets/routes for memory interfaces and channel merge, memif and IRQ metadata tables, regmap caching policy, IRQ handling, runtime PM, and the platform probe path.

## Important APIs, Types, and Functions

`mt8186_afe_hardware` sets PCM constraints and formats. FE DAI ops include `mt8186_fe_startup()`, `shutdown()`, `hw_params()`, `hw_free()`, `prepare()`, and `trigger()`. Startup binds the substream to the memif, sets hardware constraints, and acquires a dynamic IRQ only if a memif has no constant IRQ. Trigger enables/disables memif hardware, configures IRQ counter/fs fields, optionally delays small-latency capture before IRQ enable, and clears pending IRQs on stop.

Control callbacks expose `Audio IRQ1 CNT`, `Audio IRQ2 CNT`, and `record_xrun_assert`, storing values in `afe_priv->irq_cnt` and `xrun_assert`. DAPM widgets and routes describe UL1-UL8 capture mixers, UL5 channel-merge (`CM1_EN`) and mux paths, hostless UL virtual inputs, and routing from ADDA, I2S, PCM, connsys I2S, SRC, and gain blocks.

`memif_data[MT8186_MEMIF_NUM]` maps every memif to base/current/end registers, MSB registers, fs/mono/quad/enable/HD/align/pbuf/minlen fields. `irq_data[MT8186_IRQ_NUM]` maps all 27 IRQs to counter, fs, enable, and clear registers. `memif_irq_usage[]` gives the current fixed memif-to-IRQ assignment. `mt8186_is_volatile_reg()` marks clock-controlled, current-pointer, monitor/debug, IRQ, tuner, and other hardware-changing registers volatile for regmap. `mt8186_afe_irq_handler()` reads enabled MCU IRQ status, calls `snd_pcm_period_elapsed()` for memifs whose IRQ bit fired, then clears status.

`mt8186_afe_runtime_suspend()` disables AFE, waits for `AFE_DAC_MON`, clears IRQs twice, resets sinegen, makes regmap cache-only/dirty, disables CGs, and disables clocks. Resume enables clocks/CGs, syncs regcache, enables DCM, programs CPU HD alignment and 24-bit connection registers, and turns AFE on. Probe allocates `mtk_base_afe` and `mt8186_afe_private`, handles reserved-memory fallback, maps MMIO, initializes clocks, allocates memif/IRQ arrays, requests IRQ, registers all sub-DAIs through `dai_register_cbs[]`, resets audiosys, bootstraps runtime PM for regmap defaults, and registers the ASoC component.

## Control Flow and State

The persistent driver state is `struct mtk_base_afe` plus `struct mt8186_afe_private`. Memif state tracks substreams and IRQ usage. Controls persist IRQ counter overrides and xrun debug behavior until stream shutdown resets them. Runtime PM keeps register state in a flat regcache while power is off, except volatile registers. Probe is the only platform registration path and publishes the driver for `compatible = "mediatek,mt8186-sound"`.

## Dependencies and Integration Points

The file integrates Linux platform devices, DMA masks, reserved memory, reset control, IRQ, runtime PM, regmap, ALSA SoC components, MediaTek common AFE helpers, and all MT8186 DAI registration modules. It uses clock helpers from `mt8186-afe-clk.c`, GPIO APIs, interconnection bit indexes, and register macros.

## Risks

The fixed `memif_irq_usage[]` has a TODO to verify each mapping; wrong mapping breaks period interrupts. `mt8186_afe_irq_handler()` returns `ret` directly on regmap read failure even though the function type is `irqreturn_t`. `enable_irq_wake()` has no matching disable in this file. Missing clock handles from `mt8186_init_clock()` may become later null dereferences. The volatile register list is large and must remain accurate, or regcache can replay stale monitor/current-pointer state or fail to restore required controls. The probe error path after `pm_runtime_resume_and_get()` is delicate and should be retested after changes.

## Test Signals

Strong signals include successful platform probe, complete DAI/component registration, `aplay`/`arecord` on all DL/UL memifs, period IRQ delivery, suspend/resume with playback/capture recovery, UL5 12-channel channel-merge paths, IRQ counter controls updating live hardware, and regmap cache sync without warnings. Build tests should include modular and built-in configurations.
