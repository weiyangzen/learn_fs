# Research: subset-b-006523

This grouped report covers the MT8189 ALSA SoC AFE platform, backend DAI, interconnect, and machine-driver files listed for `subset-b-006523`. Each source-file section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-pcm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-adda.c

## Purpose

`mt8189-dai-adda.c` implements MT8189 ADDA and AP DMIC backend DAIs. It programs DAC/ADC sample-rate conversion, gain, IIR filters, MTKAIF protocol and phase alignment, AP DMIC source configuration, and PMIC VS1 voting. It also publishes DAPM mixers/routes that connect memory interfaces and internal sources to ADDA playback/capture endpoints.

## Important APIs, Types, And Data

The exported hook is `mt8189_dai_adda_register()`, called from the AFE platform probe. It allocates one `mtk_base_afe_dai`, attaches `mtk_dai_adda_driver[]`, `mtk_adda_controls[]`, `mtk_dai_adda_widgets[]`, and `mtk_dai_adda_routes[]`, initializes private data, and adds the DAI to `afe->sub_dais`.

`struct mtk_afe_adda_priv` stores the last DL and UL rates per ADDA-like DAI. `init_adda_priv_data()` allocates private data for `MT8189_DAI_ADDA` and `MT8189_DAI_ADDA_CH34`; AP DMIC and AP DMIC_CH34 share those state blocks. Rate helpers map ALSA rates to register encodings: `adda_dl_rate_transform()` supports common DL rates through 192 kHz while `adda_ul_rate_transform()` supports 8/16/32/48/96/192 kHz capture.

The DAI array exposes `ADDA`, `ADDA_CH34`, `AP_DMIC`, and `AP_DMIC_CH34`. Controls include raw `ADDA_DL_GAIN`, `MTKAIF_DMIC Switch`, and `ADDA_DL_MAX_VOL Switch`. DAPM widgets include ADDA enable gates, DL/UL clocks, playback/capture source enables, AUD_PAD_TOP, MTKAIF config supplies, AP DMIC supplies, FIFO soft reset supplies, VS1 voter supplies, and muxes for `ADDA_UL_Mux` and `ADDA_CH34_UL_Mux`.

## Control Flow

Playback setup enters `mtk_dai_adda_hw_params()` and `set_playback_hw_params()`. The code builds `AFE_ADDA_DL_SRC_CON0` with DL rate, x8 output mode, unmuted channels, optional voice mode for 8/16 kHz, and gain enable. It builds `AFE_ADDA_DL_SRC_CON1` with the normal -0.3 dB gain value. For the main `ADDA` DAI it clears predistortion registers, writes DL SRC registers, sets SDM attenuation, selects second-order SDM, and enables SDM auto reset with `SDM_AUTO_RESET_THRESHOLD`.

Capture setup enters `set_capture_hw_params()`. It converts the sample rate into UL voice mode, enables IIR in software-selected mode, writes 35 Hz-at-48 kHz IIR coefficients, and programs one of the ADDA UL0, DMIC0, or DMIC1 SRC blocks. For analog MTKAIF capture it forces `AFE_MTKAIF0_RX_CFG0` data mode to AMIC. For AP DMIC capture, it calls `mtk_adda_ul_src_enable_dmic()`, which selects DMIC phases, 3.25 MHz mode, disables low-power mode, enables SDM 3-level and channel modes, and programs UL gain/gain mode.

DAPM events provide power sequencing. `mtk_adda_ul_event()` switches MTKAIF data mode to DMIC and configures the ADDA UL source when the user control has requested MTKAIF DMIC, then delays 120-130 us on power-down and resets the DMIC flags. `mtk_adda_pad_top_event()` writes AUD pad config based on `afe_priv->mtkaif_protocol`. `mtk_adda_mtkaif_cfg_event()` programs protocol 2 / protocol 2 clock phase mode, optionally inverts clocks for calibration, checks selected phase availability, computes MISO delay data/cycle pairs, and updates MTKAIF0/1 delay registers. `mtk_adda_dl_event()` adds the same 120-130 us post-power-down delay for DL.

PMIC VS1 voting is driven by `mt_vs1_voter_dl_event()`, `mt_vs1_voter_ul_event()`, `mt8189_adda_dl_max_vol_set()`, and `mt6363_vs1_vote()`. The vote is asserted when ADDA UL is on or when ADDA DL is on at max volume, and deasserted otherwise by writing the PMIC regmap set/clear registers.

## State And Persistence

State is held in `afe_priv->dai_priv[]`, `afe_priv->mtkaif_dmic`, `afe_priv->mtkaif_dmic_ch34`, `afe_priv->mtkaif_protocol`, MTKAIF phase arrays, and the VS1 voting booleans `is_adda_dl_on`, `is_adda_ul_on`, `is_adda_dl_max_vol`, and `is_mt6363_vote`. These values persist across DAPM events while the component remains bound. Register programming is not self-restoring in this file; platform-level regcache and runtime resume in `mt8189-afe-pcm.c` handle hardware power transitions.

## Dependencies And Integration Points

The file depends on the AFE clock/register headers and the interconnection constants used by mixer controls. It integrates with MTKAIF calibration state in `struct mt8189_afe_private`, PMIC access through `afe_priv->pmic_regmap`, and DAPM routes used by the memif file. It is registered as one of the sub-DAIs aggregated by the main AFE platform driver and selected by the machine driver's BE links and DAPM paths.

## Risks

`mt8189_adda_dmic_set()` sets both `mtkaif_dmic` and `mtkaif_dmic_ch34`, but only `mtkaif_dmic` is read in `mtk_adda_ul_event()` in this file; callers need to verify CH34 behavior through routes and DMIC source events. MTKAIF phase delay programming assumes phase arrays are initialized correctly; negative values skip delay setup. `mt6363_vs1_vote()` silently returns when `pmic_regmap` is absent, so audio may work without the power vote only if board power is otherwise sufficient. Some route controls connect many internal sources into ADDA DL/UL mixers and include duplicated or asymmetric channel options; route validation should match hardware diagrams.

## Test Signals

Test playback at 8/16/48 kHz and capture at 8/16/32/48 kHz on ADDA and AP DMIC, checking for rate transform warnings. Validate `MTKAIF_DMIC Switch`, `ADDA_DL_MAX_VOL Switch`, and VS1 PMIC set/clear writes with regmap tracing. Exercise MTKAIF protocol 2 and phase-delay paths with calibration data populated and absent. DAPM debug should show expected supplies for ADDA playback, analog capture, AP_DMIC, and AP_DMIC_CH34, plus the 120 us shutdown delay before AFE off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-i2s.c

## Purpose

`mt8189-dai-i2s.c` implements MT8189 I2S-style backend DAIs using the ETDM input/output hardware blocks. It configures ETDM IN0/IN1 and OUT0/OUT1/OUT4, manages APLL and MCLK DAPM supplies, supports optional I2S sharing from device tree, and exposes DAPM mixers/routes so memory interfaces and internal sources can feed external I2S outputs or capture I2S inputs.

## Important APIs, Types, And Data

The exported function is `mt8189_dai_i2s_register()`. It registers five DAIs: `I2SIN0`, `I2SIN1`, `I2SOUT0`, `I2SOUT1`, and `I2SOUT4`. `I2SOUT4` supports up to 8 playback channels; the others are 2-channel. The DAI ops are `mtk_dai_i2s_ops` with `.hw_params = mtk_dai_i2s_hw_params` and `.set_sysclk = mtk_dai_i2s_set_sysclk`.

`struct mtk_afe_i2s_priv` persists per-DAI rate, MCLK ID/rate/APLL, share-property name, share target, channel count, sync/IP/slave/loopback fields, and low-jitter metadata. The static `mt8189_i2s_priv[]` seeds default IDs, MCLK IDs, and default share mappings: I2SIN0 defaults to sharing I2SOUT0, I2SIN1 defaults to sharing I2SOUT1, outputs default to no share, and I2SOUT4 uses the I2SIN1 MCK ID. `mt8189_dai_i2s_get_share()` can override these from device tree string properties such as `i2sin0-share` and `i2sout4-share`.

Rate and format helpers translate ALSA parameters to ETDM encodings: `get_etdm_rate()`, `get_etdm_inconn_rate()`, `get_etdm_wlen()`, and `get_etdm_lrck_width()`. User controls include `I2SIN0 Loopback` and `I2SIN1 Loopback`. Dummy muxes allow an I2S interface to be powered without a real codec path.

## Control Flow

During registration, `init_i2s_priv_data()` allocates and copies the template private data into `afe_priv->dai_priv[]`, then `mt8189_dai_i2s_get_share()` parses any share properties. At hw_params time, `mtk_dai_i2s_config()` records the stream rate and writes the relevant ETDM register block. IN0/IN1 configure initial count/point, LRCK reset, APLL clock source, auto clock enable, FS timing, relatch rate, AFIFO mode, almost-end counters, output-to-latch time, I2S format, APLL relatch domain, bit length, word length, and cowork master/slave selection. OUT0/OUT1/OUT4 similarly configure initial timing, FS timing, APLL clock source, relatch selection, I2S format, APLL relatch domain, bit length, word length, and cowork selection for OUT0/OUT1. If a DAI has `share_i2s_id >= 0`, the same configuration recursively applies to the shared DAI.

`mtk_dai_i2s_set_sysclk()` validates that the requested output MCLK divides the selected APLL rate, then records `mclk_rate` and `mclk_apll`. If the current DAI has a share target, it propagates the same MCLK values to the shared private data. DAPM supply events use that state: `mtk_apll_event()` enables/disables APLL1 or APLL2 based on widget name, and `mtk_mclk_en_event()` enables/disables the specific MCK gate only while a nonzero MCLK rate is routed. DAPM route predicates `mtk_afe_i2s_share_connect()`, `mtk_afe_i2s_apll_connect()`, `mtk_afe_i2s_mclk_connect()`, and `mtk_afe_mclk_apll_connect()` dynamically decide whether shared I2S, APLL, and MCLK routes are active.

The route table is substantial. I2SOUT0 and I2SOUT1 mix DL0-DL8 and DL_24CH stereo pairs plus gain/ADDA/PCM inputs. I2SOUT4 mixes DL0-DL8, DL24, DL_24CH channels 1-8, gain, ADDA, PCM, and SRC2. I2SIN0/I2SIN1 are capture widgets with DAPM supplies and optional dummy input muxes.

## State And Persistence

State lives in per-DAI `struct mtk_afe_i2s_priv` objects under `afe_priv->dai_priv[]`. The important persistent fields are `rate`, `mclk_rate`, `mclk_apll`, and `share_i2s_id`, which DAPM route predicates read after hw_params/set_sysclk. MCLK rate is reset to zero on MCLK supply power-down. ETDM registers are programmed during hw_params and rely on the platform regcache/runtime PM to preserve or restore values across power transitions.

## Dependencies And Integration Points

This file depends on clock helpers such as `mt8189_apll1_enable()`, `mt8189_apll2_enable()`, `mt8189_get_apll_by_rate()`, `mt8189_get_apll_rate()`, and `mt8189_mck_enable()`. It uses register definitions from `mt8189-afe-common.h`, interconnect bit indexes from `mt8189-interconnection.h`, and common AFE DAI data structures. The machine driver sets I2S BE sysclk through `snd_soc_dai_set_sysclk()`; that call is required before DAPM can enable the correct MCLK path.

## Risks

`get_etdm_rate()` and `get_etdm_inconn_rate()` return zero for unsupported rates instead of erroring, so an unexpected rate could silently program the 8 kHz encoding. `get_etdm_lrck_width()` returns zero only for physical width <= 1; normal S8 becomes 7, S16 becomes 15, and S32 becomes 31. Share recursion lacks cycle detection, so invalid device tree share properties could cause repeated configuration or recursion. `mtk_dai_i2s_set_sysclk()` checks `share_i2s_id > 0`, not `>= 0`, which is fine for current positive DAI IDs but should be kept in mind if IDs change. Route predicates depend on widget name prefixes, so DAPM widget renames can break behavior.

## Test Signals

Validate 48 kHz and higher-rate I2S playback/capture with I2SOUT0/1/4 and I2SIN0/1. Confirm set_sysclk failures for non-divisible MCLKs and success for expected 128fs or codec-driven rates. Device tree share-property tests should show only intended shared enable routes in DAPM. Regmap traces should show ETDM IN/OUT timing, word length, FS timing, cowork, APLL, and MCLK bits programmed before DAPM enables the interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-pcm.c

## Purpose

`mt8189-dai-pcm.c` implements the MT8189 PCM0 backend DAI. Despite the file banner saying I2S control, the implementation programs `AFE_PCM0_INTF_CON0/CON1`, exposes a single symmetric playback/capture PCM DAI, and provides DAPM mixers/routes for PCM0 playback and capture through the AFE interconnect.

## Important APIs, Types, And Data

The exported hook is `mt8189_dai_pcm_register()`, which adds `mtk_dai_pcm_driver[]`, `mtk_dai_pcm_widgets[]`, and `mtk_dai_pcm_routes[]` to `afe->sub_dais`. The DAI array contains one DAI named `PCM 0` with id `MT8189_DAI_PCM_0`, 1-2 channel playback and capture, 8/16/32/48 kHz rates, S16/S24/S32 formats, and symmetric rate/sample-bits constraints.

The file defines PCM register-value enums for left-channel repeat, VBT 16 kHz mode, modem selection, sync type, BT mode, AFIFO/ASRC source, master/slave clocking, word length, PCM mode, format, BCLK inversion, enable, and 1x enable domain. `pcm_rate_transform()` maps ALSA rates to `MTK_AFE_PCM_RATE_*`; `pcm_1x_rate_transform()` maps the same rates to PCM 1x relatch encodings.

DAPM widgets include three playback mixers (`PCM_0_PB_CH1`, `PCM_0_PB_CH2`, `PCM_0_PB_CH4`), a `PCM_0_EN` supply on `AFE_PCM0_INTF_CON0`, a `PCM0_CG` clock gate on `AUDIO_TOP_CON0`, and external input/output pins. Mixers route ADDA UL, DL2, DL_24CH, I2SIN1, and DL0 sources into PCM0 playback channels.

## Control Flow

`mtk_dai_pcm_hw_params()` reads the sample rate, converts both main and 1x encodings, and checks whether the playback or capture DAPM widgets are already active. If either side is active, it returns without reprogramming registers, preserving symmetric full-duplex operation while the other direction is running. For `MT8189_DAI_PCM_0`, it builds `pcm_con0` as non-inverted BCLK, no left-channel repeat, VBT disabled, one-BCK sync, AFIFO bypass mode, master mode, rate-selected PCM mode, and I2S frame format. It builds `pcm_con1` as internal modem, dual-mic TX mode, 26 MHz hopping domain, and the selected 1x rate. It updates `AFE_PCM0_INTF_CON0` while preserving the enable bit and writes masked `AFE_PCM0_INTF_CON1`.

## State And Persistence

The PCM DAI itself has no private allocation. Its state is the hardware registers and DAPM widget active flags. Because hw_params skips programming when playback or capture is already active, the first stream to configure PCM0 determines the shared hardware configuration until both directions go inactive. Register state is preserved by the main AFE regmap/cache and runtime PM handling.

## Dependencies And Integration Points

The file depends on `mt8189-afe-common.h` for PCM register fields, `mt8189-interconnection.h` for input port bit positions, and ASoC DAPM/PCM helpers. The machine driver defines a `PCM_0_BE` link with I2S-style DAI format, playback-only BE settings, and a startup op that restricts rate to 48 kHz. Other DAI files and the memif route table reference the `PCM 0 Capture` and `PCM 0 Playback` widgets.

## Risks

The hw_params active-widget guard prevents conflicting reconfiguration but also silently accepts a second stream whose requested params may differ; symmetric DAI constraints mitigate this, but route-level tests should still cover duplex use. Unsupported rates fall back to 48 kHz with a warning rather than failing. The `regmap_update_bits()` mask for `AFE_PCM0_INTF_CON0` uses `~PCM0_EN_MASK_SFT`, so correctness depends on `PCM0_EN_MASK_SFT` being an actual mask value, not just a shifted-bit macro name. The file banner is misleading, which can confuse maintainers searching for PCM-specific code.

## Test Signals

Run PCM0 playback and capture at the supported rates, then duplex/open-order tests to ensure the active-widget guard preserves the first configuration and ALSA constraints prevent incompatible params. Regmap tracing should confirm PCM0 enable is not clobbered by hw_params. DAPM should show `PCM0_CG` and `PCM_0_EN` active for both playback and capture paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-tdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-tdm.c

## Purpose

`mt8189-dai-tdm.c` implements MT8189 TDM and DisplayPort transmitter (`TDM_DPTX`) playback backend DAIs. It configures TDM word/channel timing, HDMI output channel mapping, DPTX channel format, MCLK/BCK clocks, and DAPM routes that select between normal TDM output and DPTX output.

## Important APIs, Types, And Data

The exported registration hook is `mt8189_dai_tdm_register()`. It registers two playback-only DAIs, `TDM` and `TDM_DPTX`, both supporting 2-8 channels, S16/S24/S32 formats, and rates from 8 kHz through 192 kHz including 88.2/96/176.4 kHz. DAI ops are `mtk_dai_tdm_ops`, with hw_params, trigger, and set_sysclk.

`struct mtk_afe_tdm_priv` stores BCK ID/rate, MCLK ID/multiple/rate/APLL. Normal TDM defaults to 128fs MCLK; DPTX defaults to 256fs. Both use `MT8189_TDMOUT_BCK` and `MT8189_TDMOUT_MCK`. Helper functions translate ALSA params into register encodings: `get_tdm_wlen()`, `get_tdm_channel_bck()`, `get_tdm_lrck_width()`, `get_tdm_ch()`, `get_dptx_ch_enable_mask()`, `get_dptx_ch()`, and `get_dptx_wlen()`.

Controls include eight HDMI channel mux controls backed by `AFE_HDMI_CONN0`, letting each HDMI output slot select CH0-CH7. DAPM widgets include a `TDM Playback Route` demux with `NONE`, `TDMOUT`, and `DPTXOUT`, BCK/MCK supplies for normal and DPTX paths, and the TDM clock gate.

## Control Flow

Registration allocates one DAI descriptor and two private state blocks, installs controls/widgets/routes, adds the DAI to `afe->sub_dais`, and stores the private blocks in `afe_priv->dai_priv[MT8189_DAI_TDM]` and `[MT8189_DAI_TDM_DPTX]`.

`mtk_dai_tdm_hw_params()` validates the DAI ID, obtains private state, calculates MCLK if not explicitly set, then calculates BCK as `rate * channels * physical_width`. It rejects BCK rates above MCLK or MCLK rates not divisible by BCK. It writes `AFE_TDM_CON1` for left alignment, word length, channel count group, channel BCK cycles, and LRCK width. For DPTX it also programs `AFE_DPTX_CON` channel enable mask, channel number mode, and 16/24-bit format. It then maps channel pairs into `AFE_TDM_CON2`: 2 channels use O30/O31 only, 4 channels add O32/O33, 6 add O34/O35, and 8 add O36/O37. Finally it updates `AFE_HDMI_OUT_CON0` with channel count.

`mtk_dai_tdm_trigger()` enables HDMI output, optional DPTX, and TDM on start/resume, then disables them in reverse on stop/suspend. `mtk_dai_tdm_set_sysclk()` validates output-clock direction and delegates to `mtk_dai_tdm_cal_mclk()`, which selects an APLL by requested frequency and requires exact divisibility. DAPM events `mtk_tdm_bck_en_event()` and `mtk_tdm_mck_en_event()` enable/disable MCK gates at the stored rates, and `mtk_afe_tdm_apll_connect()` routes MCLK supplies to the chosen APLL.

## State And Persistence

Per-DAI private state stores the calculated or requested MCLK, selected APLL, and BCK rate. `mtk_tdm_mck_en_event()` resets `mclk_rate` to zero on power down, causing a later hw_params to recalculate default MCLK unless set_sysclk is called again. Hardware register state is restored through the parent AFE regmap/runtime PM flow.

## Dependencies And Integration Points

The file depends on MT8189 clock helpers for APLL selection/rates and MCK enable/disable, AFE register macros for TDM/HDMI/DPTX fields, and ASoC DAPM route predicates. The main AFE file assigns HDMI memif to custom IRQ31 and defines HDMI memif registers; the machine driver's `TDM_DPTX_BE` sets 256fs sysclk and forces backend format to S32_LE before reaching this DAI.

## Risks

Default MCLK calculation ignores the return value from `mtk_dai_tdm_cal_mclk()`; a non-divisible default might leave stale or invalid `mclk_apll` state before later BCK checks. `get_tdm_lrck_width()` subtracts one from physical width and assumes nonzero format width. `get_dptx_ch()` treats any channel count except exactly two as 8-channel mode; 4- and 6-channel DPTX rely on the enable mask to limit active channels. Trigger enables HDMI output before TDM/DPTX and disables HDMI last; hardware sequencing should be validated against the HDMI/DPTX block requirements.

## Test Signals

Test 2/4/6/8-channel playback at S16/S24/S32 and common HDMI/DP rates, including explicit set_sysclk and default MCLK paths. Negative tests should request non-divisible sysclk or BCK/MCLK combinations and expect `-EINVAL`. Regmap traces should show `AFE_TDM_CON1`, `AFE_TDM_CON2`, `AFE_HDMI_OUT_CON0`, and `AFE_DPTX_CON` values matching channel/format selection. DAPM should route either `TDMOUT` or `DPTXOUT`, select the correct APLL, and enable BCK/MCK supplies in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-dai-tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-interconnection.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-interconnection.h

## Purpose

`mt8189-interconnection.h` defines the input-port bit positions used by MT8189 AFE connection registers. The DAI files use these macros in `SOC_DAPM_SINGLE_AUTODISABLE()` mixer controls to connect internal producers such as DL memifs, ADDA UL channels, DMICs, I2S inputs, PCM capture, gain blocks, and SRC outputs to consumer widgets.

## Important APIs, Types, And Data

The header exports only preprocessor constants. It has include guards and no functions, structs, or runtime state. Input ports below 32 are encoded directly, including CONNSYS I2S, gain outputs, STF, ADDA UL channels, proximity UL, and DMIC channels. For connection register banks representing input indexes at 32, 64, 128, and 192 or above, it defines bank offsets (`I_32_OFFSET`, `I_64_OFFSET`, `I_128_OFFSET`, `I_192_OFFSET`) and then subtracts those offsets to produce the bit position used in the corresponding `AFE_CONNxxx_n` register word. Examples include `I_DL0_CH1`, `I_DL_24CH_CH8`, `I_DL24_CH2`, `I_PCM_0_CAP_CH1`, `I_I2SIN1_CH2`, and `I_SRC_4_OUT_CH2`.

## Control Flow

There is no executable control flow. Its definitions are compiled into the static DAPM mixer tables in `mt8189-afe-pcm.c`, `mt8189-dai-adda.c`, `mt8189-dai-i2s.c`, and `mt8189-dai-pcm.c`. At runtime, ALSA control changes set or clear bits in AFE connection registers using these constants.

## State And Persistence

The header has no state and no persistence behavior. Persistence of the bits selected by these constants is handled by the regmap and DAPM controls in the C files that reference the macros.

## Dependencies And Integration Points

The constants must match the MT8189 hardware interconnect matrix and the register bank layout in `mt8189-afe-common.h`. They are an integration contract shared by every DAPM route that uses an `AFE_CONN*` register. Any mismatch affects audio routing even when clocks, DAIs, and memifs are otherwise configured correctly.

## Risks

Because many macros intentionally subtract a bank offset, the same numeric bit position can represent different absolute hardware input indexes depending on the connection register bank. Using a macro with the wrong `AFE_CONNxxx_n` bank can silently route the wrong source. The header contains no compile-time validation against hardware tables, so copy/paste mistakes in DAPM mixers are the main risk. Several C files have large route tables, increasing the chance of pairing a readable control label with an incorrect `I_*` bit macro.

## Test Signals

The primary tests are route-level audio loopback and DAPM control validation. For each mixer control, toggling the control should flip the intended bit in the intended `AFE_CONN*` register and produce audio from the named source. Static review should compare every `I_*` use against the MT8189 interconnect matrix and ensure the register bank suffix (`_0`, `_1`, `_2`, `_4`, `_6`) matches the macro offset group.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-interconnection.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-nau8825.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-nau8825.c

## Purpose

`mt8189-nau8825.c` is the MT8189 ASoC machine driver. It defines the sound card topology for MT8189 boards using NAU8825, RT5650, RT5682S, RT5682I, ES8326, CS35L41, HDMI, DP/DPTX, and dummy/dumb amplifier endpoints. It supplies FE/BE DAI links, codec-specific hw_params, jack setup, card-level DAPM widgets/controls, and compatible-specific card pdata for the common MediaTek soundcard probe.

## Important APIs, Types, And Data

The platform driver is `mt8189_nau8825_driver`, matched by compatibles `mediatek,mt8189-nau8825`, `mediatek,mt8189-rt5650`, `mediatek,mt8189-rt5682s`, `mediatek,mt8189-rt5682i`, and `mediatek,mt8189-es8326`. Probe delegates to `mtk_soundcard_common_probe`. Card configuration is held in `mt8189_nau8825_soc_card` and `mtk_soundcard_pdata` instances for each compatible. The shared `mt8189_nau8825_dai_links[]` table defines all FE and BE links.

FE DAI links cover DL0-DL8, DL23-DL25, DL_24CH, HDMI playback, UL0-UL10, UL24/UL25, UL_CM0/UL_CM1, and UL_ETDM_In0/In1. They are dynamic DPCM links using dummy codecs and `SND_SOC_DPCM_TRIGGER_PRE`. BE links include I2SIN0/1, I2SOUT0/1, AP_DMIC, AP_DMIC_CH34, TDM_DPTX, and PCM_0.

Codec-specific ops are implemented by `mt8189_nau8825_ops`, `mt8189_rtxxxx_i2s_ops`, `mt8189_cs35l41_i2s_ops`, `mt8189_es8326_ops`, `mt8189_common_i2s_ops`, `mt8189_dptx_ops`, and `mt8189_pcm_ops`. Jack pins are defined for headset, DP, and HDMI. `mt8189_cs35l41_codec_conf[]` gives left/right name prefixes for the two CS35L41 devices.

## Control Flow

Common I2S startup constrains rates to 48 kHz. `mt8189_common_i2s_hw_params()` sets CPU DAI sysclk to 128fs. DPTX hw_params sets CPU sysclk to 256fs and `mt8189_dptx_hw_params_fixup()` forces BE format to S32_LE. NAU8825 hw_params derives BCLK from rate, channels, and bit width, selects FLL block clock input, and programs the codec PLL to 256fs. RT5682-family and RT5650 hw_params set a two-slot TDM slot width, codec PLL from 32fs to 512fs, codec sysclk to 512fs, and CPU sysclk to 512fs. CS35L41 hw_params iterates both codec DAIs, sets component and DAI sysclk from 32fs BCLK, assigns RX slots 0 and 1, and sets CPU sysclk to 128fs. ES8326 hw_params sets codec and CPU MCLK to 256fs.

Initialization helpers add card widgets/controls and jack handling. `mt8189_dumb_amp_init()` adds an external speaker widget and pin switch. DP/HDMI init functions create lineout jacks and pass them to codec components. `mt8189_headset_codec_init()` adds headphone/mic widgets and pin switches, creates a headset jack with four buttons, maps button keys differently for ES8326 versus the other headset codecs, and calls `snd_soc_component_set_jack()`. Exit clears the component jack.

`mt8189_nau8825_soc_card_probe()` walks prelinks before card registration and adapts each BE link based on actual codec DAI names. It attaches DP/HDMI jack init when non-dummy codecs are present, selects headset ops/init/exit for NAU8825/RT5682S/RT5650/RT5682I/ES8326 on I2SOUT0/I2SIN0, adds dumb amplifier init for unknown non-dummy I2SOUT0/I2SIN0 codecs, and configures CS35L41 ops plus codec name prefixes on I2SOUT1.

## State And Persistence

Persistent card state is in the static `snd_soc_card`, DAI link array, compatible-specific `mtk_soundcard_pdata`, and runtime jack objects allocated by the common soundcard infrastructure. The probe mutates DAI link ops/init/exit pointers and card codec_conf based on detected codec DAIs, so the link table is effectively customized at probe time. Jack state is maintained by codec components after `snd_soc_component_set_jack()`.

## Dependencies And Integration Points

This file integrates with the AFE platform driver by naming CPU DAIs such as `DL0`, `UL0`, `I2SOUT0`, `PCM 0`, and `TDM_DPTX`. It depends on the common MediaTek soundcard framework (`mtk-soc-card.h`, `mtk-soundcard-driver.h`, and `mtk-afe-platform-driver.h`) to bind device-tree endpoints into the DAI link table. It includes codec headers for NAU8825, RT5682/RT5682S, CS35L41, and ES8326 behavior. The DPTX and PCM BE links map to the TDM and PCM DAI files, while I2S codec links map to `mt8189-dai-i2s.c`.

## Risks

The shared static DAI link array is mutated at probe time; if multiple compatible instances were ever probed in one kernel image, stale ops/init pointers could leak across cards. `mt8189_nau8825_soc_card_probe()` assumes `dai_link->codecs` is valid for I2S links before comparing `dai_name`; malformed link data could dereference null. Common I2S startup hard-restricts many codec paths to 48 kHz even though lower layers support more rates, which may be intentional board policy but can surprise users. The ES8326 pdata variable is named `mt8188_es8326_card`, likely a naming typo. DPTX format fixup forces S32_LE, so HDMI/DP paths need end-to-end validation with the TDM DAI's format and channel handling.

## Test Signals

Boot each compatible and verify the card name, FE/BE link creation, and codec-specific ops selection. Run 48 kHz headset playback/capture on NAU8825, RT5682S, RT5650, RT5682I, and ES8326 boards; verify jack insertion and button mappings. Test CS35L41 stereo speaker playback and confirm right/left name prefixes and RX slot mapping. Test DP and HDMI lineout jack reporting. DPCM tests should route FE streams to I2S, PCM, AP_DMIC, and TDM_DPTX BE links without unresolved DAPM paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8189/mt8189-nau8825.c -->
