# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-pcm.c

## Purpose

`mt8189-afe-pcm.c` is the central MT8189 AFE platform driver. It registers the `mediatek,mt8189-afe-pcm` platform device as an ASoC component, aggregates all ADDA/I2S/PCM/TDM/memif DAIs, owns the MMIO regmap, sets up DMA/memif hardware descriptions, assigns IRQs, handles runtime power transitions, and exposes front-end memory interfaces used by the machine driver. It is the integration point that turns the SoC audio register block into ALSA PCM streams.

## Important APIs, Types, And Data

The main public integration is the platform driver `mt8189_afe_pcm_driver`, whose probe calls `mt8189_afe_pcm_dev_probe()` and whose PM ops bind runtime suspend/resume. The component driver `mt8189_afe_component` registers under `AFE_PCM_NAME` and supplies `mtk_afe_pcm_new`, `mt8189_afe_pcm_free`, `mt8189_afe_pcm_open`, and `mtk_afe_pcm_pointer`. The FE DAI ops are `mt8189_memif_dai_ops`, with local startup/shutdown/hw_params/trigger and common MediaTek FE helpers for hw_free/prepare.

Key static tables define the platform contract: `mt8189_afe_hardware` advertises mmap-capable interleaved S16/S24/S32 PCM, 96-byte minimum periods, 256 KiB maximum buffers, and no-period-wakeup capability. `mt8189_memif_dai_driver[]` exposes DL0-DL8, DL23-DL25, DL_24CH, HDMI, UL0-UL10, UL24/UL25, UL_CM0/UL_CM1, and ETDM capture memifs. `memif_data[]` maps each `MT8189_MEMIF_*` to base/current/end registers, FS fields, mono/HD/align fields, pbuf/minlen fields, and channel-count fields for multi-channel DL/HDMI. `irq_data[]` maps normal IRQ0-IRQ26 and custom TDM IRQ31 to count, FS, enable, and clear registers. `memif_irq_usage[]` gives default constant IRQ assignments.

Rate conversion is centralized in `mt8189_rate_transform()`, reused through `mt8189_memif_fs()`, `mt8189_irq_fs()`, and `mt8189_get_dai_fs()`. Channel merge hardware is handled by `calculate_cm_update()`, `mt8189_set_cm()`, `mt8189_enable_cm_bypass()`, and the DAPM event handlers `ul_cm0_event()` / `ul_cm1_event()`.

## Control Flow

Probe first enables a 34-bit coherent DMA mask and optional reserved memory, allocates `struct mtk_base_afe` and `struct mt8189_afe_private`, maps the AFE base address, initializes clocks, allocates and initializes memif/IRQ arrays, requests the single hardware IRQ, and invokes the sub-DAI registration callbacks: `mt8189_dai_adda_register`, `mt8189_dai_i2s_register`, `mt8189_dai_pcm_register`, `mt8189_dai_tdm_register`, and `mt8189_dai_memif_register`. After `mtk_afe_combine_sub_dai()`, it installs platform callbacks for rate conversion, pbuf sizing, runtime PM, and memif hardware, initializes regmap while clocks are on, applies `mt8189_cg_patch`, enables MCU IRQ routing, then registers the ASoC component.

PCM open/start flows enter through ASoC FE DAIs. `mt8189_fe_startup()` stores the substream in the memif, applies a 16-byte buffer step constraint and integer period constraint, then ensures an IRQ is assigned. Most memifs use constant IRQs from `memif_irq_usage[]`; dynamic acquisition is still present for any memif whose `irq_usage` is negative. `mt8189_fe_hw_params()` records the capture CM rate/channel state for VUL8/VUL9 and UL_CM0/UL_CM1 before deferring to `mtk_afe_fe_hw_params()`. `mt8189_fe_trigger()` enables/disables the memif, programs the IRQ period count from `runtime->period_size`, converts the stream rate into IRQ FS encoding, enables or disables the IRQ bit, and clears pending IRQ/miss flags on stop. Capture streams with periods under or equal to 10 ms delay 300 us after memif enable so the UL memif can collect data before IRQs start.

The interrupt handler reads MCU-enabled normal and custom IRQ status, calls `snd_pcm_period_elapsed()` for substreams whose assigned IRQ bit is pending, warns if processing exceeds 5 ms, and clears all pending normal/custom IRQs by toggling clear/miss bits. HDMI is special-cased through the custom IRQ path for IRQ31.

Runtime suspend disables the main clock, waits for `AUDIO_ENGEN_CON0_MON` to show off, clears all IRQ status, drops the audio 26 MHz SPM request, marks regmap cache-only and dirty, then disables register read/write clocks. Resume reverses that sequence: enable reg-rw clock, sync regcache, set 26 MHz and CBIP requests, force CPU 8_24 alignment for 32-bit writes, and enable the main clock.

## State And Persistence

Persistent driver state lives in `struct mtk_base_afe` and `struct mt8189_afe_private`. Memifs persist substream pointers, assigned IRQs, and constant-IRQ flags. `afe_priv->cm_rate[]` and `afe_priv->cm_channels` cache channel-merge configuration until the CM DAPM supplies power up. Regmap uses `REGCACHE_FLAT`; many monitor, current-pointer, IRQ, mask, and VOW-related registers are marked volatile by `mt8189_is_volatile_reg()` to avoid stale cache use. Runtime suspend persists software state by making the cache dirty and cache-only while hardware is off.

## Dependencies And Integration Points

This file depends on MediaTek common AFE helpers from `../common/mtk-afe-fe-dai.h` and `../common/mtk-afe-platform-driver.h`, clock helpers in `mt8189-afe-clk.h`, register/enum definitions in `mt8189-afe-common.h`, and interconnect bit indexes from `mt8189-interconnection.h`. The DAPM route tables depend on widgets exported by the ADDA/I2S/PCM/TDM sub-DAI files, such as `ADDA Capture`, `AP DMIC Capture`, `I2SIN0`, `PCM 0 Capture`, and `HW_SRC_*`. The machine driver binds these FE DAIs by name through DPCM links. Device tree must provide the compatible, MMIO resource, IRQ, clocks, power domain, and optional reserved memory.

## Risks

The IRQ usage table has a `TODO: verify each memif & irq` comment and assigns several memifs to IRQ0, so concurrent use of those paths can be risky unless hardware multiplexing is intentional. `mt8189_fe_shutdown()` releases dynamic IRQs only when `const_irq` is false; bad initialization would leak or double-release IRQ assignments. The IRQ clear path toggles bits based on current register contents, which depends on the register write-one/toggle semantics being exactly as expected. CM update calculation divides by `rate` and `ch / 2`; invalid or one-channel CM use would be hazardous, though advertised CM DAIs allow wider capture. The regmap volatile list is large and hand-maintained; omissions can cause stale cached state after runtime PM. Probe calls `pm_runtime_get_sync()` in several paths and relies on balanced `put_sync()` in error/remove paths, so failures around regmap initialization deserve careful suspend/resume testing.

## Test Signals

Useful runtime signals include successful component registration for `mt8189-afe-pcm`, visible PCM devices for each FE DAI, no `init clock error`, `no irq found`, or `mtk_afe_combine_sub_dai fail` messages, and clean runtime PM cycles under `pm_runtime` tracing. Playback and capture tests should cover representative DL, UL, HDMI/custom IRQ, ETDM capture, UL_CM0/UL_CM1 CM paths, small-period capture latency, and suspend/resume with active and inactive streams. Regmap debugfs or tracepoints can confirm IRQ count/FS programming, memif enable bits, CM bypass/power-down state, and regcache sync behavior.
