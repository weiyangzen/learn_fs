<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-pcm.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.c

## Purpose
Registers MT8195 audiosys gate clocks backed by AFE MMIO registers so DAPM clock supplies and driver code can use normal Linux clock APIs for audio sub-block power gating.

## Important APIs, Types, and Functions
`mt8195_audsys_clk_register(struct mtk_base_afe *afe)` is the public entry point. `mt8195_audsys_clk_unregister()` is registered as a device-managed cleanup action. `struct afe_gate` describes each gate with clock id, name, parent name, register offset, bit, flags, and gate polarity. `aud_clks[CLK_AUD_NR_CLK]` maps all audio clock ids to gate definitions across `AUDIO_TOP_CON0`, `AUDIO_TOP_CON1`, `AUDIO_TOP_CON3`, `AUDIO_TOP_CON4`, `AUDIO_TOP_CON5`, and `AUDIO_TOP_CON6`.

## Control Flow
Registration allocates `afe_priv->lookup`, then iterates all `aud_clks`, calling `clk_register_gate()` with `CLK_SET_RATE_PARENT` and `CLK_GATE_SET_TO_DISABLE` semantics. For each successfully registered clock it creates a `clk_lookup`, fills `con_id` with the gate name and `dev_id` with the AFE device name, then calls `clkdev_add()`. This lookup path allows `SND_SOC_DAPM_CLOCK_SUPPLY("aud_*")` widgets and `devm_clk_get()` style consumers to find the gates by name.

Cleanup walks the lookup array, obtains each `struct clk` from its lookup, unregisters the gate, and drops the clkdev lookup. The cleanup action is installed with `devm_add_action_or_reset()`, so partial probe failures or driver removal release registered gates.

## State and Persistence
The clock table itself is static. Runtime state is the device-managed `afe_priv->lookup[]` array and each allocated `clk_lookup`. Gate state persists in the audio top registers and is controlled by the common clock framework. No suspend state is kept in this file; higher-level AFE runtime PM and DAPM clock consumers drive enable/disable.

## Dependencies and Integration Points
Depends on Linux CCF (`clk_register_gate`, `clk_unregister_gate`), clkdev lookup support, MT8195 AFE private data, and register constants. Clock ids are defined by `mt8195-audsys-clkid.h`. The ADDA, eTDM, PCM, memif, and machine-driver paths consume these clocks through `afe_priv->clk[]` or DAPM clock supplies such as `aud_dac`, `aud_adc`, `aud_tdm_in`, `aud_i2s_out`, `aud_hdmi_out`, `aud_pcmif`, and memif gates.

## Risks
Failed individual gate registrations only log and continue, which can leave later users with missing clocks and delayed runtime failures. The manually allocated `clk_lookup` uses non-devm allocation but is paired with a devm cleanup action; failures after allocation but before storing can leak if not carefully audited. Gate polarity and parent names must match clock-controller topology and hardware reset values. `aud_clks` length is tied to `CLK_AUD_NR_CLK`; enum/table drift can misindex lookups.

## Test Signals
Build coverage should verify the clock id enum and table size stay aligned. Runtime signals are successful AFE clock initialization, visible clock names under debugfs, DAPM routes enabling/disabling audio gates, eTDM/ADDA/PCM stream startup without missing-clock errors, and clean probe deferral/removal without stale clkdev lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.h

## Purpose
Small private interface for registering MT8195 audiosys gate clocks from the AFE platform clock initialization path.

## Important APIs, Types, and Functions
Declares `int mt8195_audsys_clk_register(struct mtk_base_afe *afe);`. The declaration expects callers to include or already know `struct mtk_base_afe` from the MT8195/common AFE headers.

## Control Flow
The header has no runtime logic. It lets `mt8195-audsys-clk.c` expose one registration function to the broader MT8195 AFE clock setup code.

## State and Persistence
No state is defined here. State created by the declared function lives in `struct mt8195_afe_private`, the Linux clock framework, and hardware gate registers.

## Dependencies and Integration Points
Integrated by MT8195 AFE clock code and indirectly used by the AFE platform probe before sub-DAI registration. It forms the compile-time boundary between the audiosys gate table and the rest of the audio driver.

## Risks
Because the header does not include `mt8195-afe-common.h`, include order matters for users that do not already have `struct mtk_base_afe` visible. API drift is the main risk.

## Test Signals
Compile tests for MT8195 audio are the primary signal. Runtime validation comes from successful `mt8195_afe_init_clock()` and later stream use of audsys gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clkid.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clkid.h

## Purpose
Defines the MT8195 audiosys gate clock id namespace used by the audsys gate table and by MT8195 audio code that indexes `afe_priv->clk[]`.

## Important APIs, Types, and Functions
The file defines one anonymous enum from `CLK_AUD_AFE` through `CLK_AUD_GASRC19`, ending with `CLK_AUD_NR_CLK`. IDs cover core AFE gates, LRCK counter, SPDIF tuners, APLL tuners, DAC/ADC and hires gates, DMIC clocks, line-in/eARC tuners, I2S/TDM/HDMI/PCM interface clocks, A1/A2/A3/A4 system clocks, memif clocks for DL and UL channels, and GASRC0-19 clocks.

## Control Flow
No runtime logic exists. The enum order is used as a stable index into `aud_clks[]` and lookup arrays.

## State and Persistence
No state is stored here. The ids address persistent clock framework objects registered by `mt8195_audsys_clk_register()` and hardware gate bits in audio top registers.

## Dependencies and Integration Points
Included by `mt8195-audsys-clk.c` and expected to stay consistent with `mt8195-afe-clk.h`/private clock arrays. DAI code refers to higher-level `MT8195_CLK_AUD_*` indexes, while this header supplies the audsys registration id range for those gates.

## Risks
Enum reordering or inserting entries without updating `aud_clks[]` can silently bind a clock name to the wrong id. Missing new hardware gates prevents DAPM or DAI paths from enabling required blocks. The anonymous enum style offers no type safety.

## Test Signals
Build failures catch only gross missing symbols. Runtime tests should check all expected `aud_*` gate names are registered and that ADDA, eTDM, PCM, memif, HDMI/DP, and GASRC consumers can enable their corresponding clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-audsys-clkid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-adda.c

## Purpose
Implements MT8195 ADDA DAIs for analog playback and capture paths through MT6359/MTKAIF. It provides DL_SRC playback, UL_SRC1 capture, and UL_SRC2/ADDA6 capture DAIs, DAPM routing, MTKAIF setup, digital mic and ADDA6-only controls, high-resolution clock switching, and sample-rate programming for ADDA DL/UL source blocks.

## Important APIs, Types, and Functions
`mt8195_dai_adda_register()` registers the sub-DAI descriptor with the AFE core. Runtime DAI programming is handled by `mtk_dai_adda_hw_params()`, `mtk_dai_da_configure()`, and `mtk_dai_ad_configure()`. MTKAIF setup lives in `mt8195_adda_mtkaif_init()` and DAPM callbacks `mtk_adda_mtkaif_cfg_event()`, `mtk_adda_ul_event()`, and `mtk_adda6_ul_event()`. Playback power delay is handled by `mtk_adda_dl_event()`. Hires clock parent switching uses `mtk_audio_hires_event()` and conditional DAPM route callback `mtk_afe_adda_hires_connect()`.

Controls include `ADDA_DL_Gain`, `MTKAIF_DMIC`, and `MTKAIF_ADDA6_ONLY`. `struct mtk_dai_adda_priv` stores `hires_required` per ADDA DAI. The DAI table exposes `DL_SRC`, `UL_SRC1`, and `UL_SRC2` with S16/S24/S32 formats and rate masks up to 192 kHz.

## Control Flow
Registration allocates a `mtk_base_afe_dai`, attaches ADDA DAI drivers, widgets, routes, controls, and allocates private data for DL_SRC, UL_SRC1, and UL_SRC2. During `hw_params`, the driver validates the DAI id, marks `hires_required` when rate exceeds 48 kHz, then programs either playback or capture. Playback sets DL source input mode via common ADDA rate transform, disables saturation, unmutes channels, enables voice mode for 8/16 kHz, and enables new second SDM. Capture writes UL voice mode into either ADDA or ADDA6 UL source registers.

DAPM powers the graph through ordered supplies: ADDA enable, playback/capture enable, MTKAIF config, and optional hires clock. MTKAIF init sets protocol-2 and clock inversion bits on ADDA/ADDA6 and AUD_PAD_TOP, then if machine-driver calibration succeeded, writes delay data/cycle values for MISO channel alignment. Capture PRE_PMU chooses analog or digital mic mode and, for ADDA6-only, disables sync word 2 as needed. POST_PMD callbacks delay about 125 us before AFE off.

## State and Persistence
Per-DAI `hires_required` persists across params and is consumed by DAPM route connection checks. MTKAIF calibration fields, `mtkaif_dmic_on`, and `mtkaif_adda6_only` live in `afe_priv->mtkaif_params`, normally filled by the machine driver. Mixer route and gain state lives in ASoC DAPM/control state and AFE registers. Hires clock parent changes persist until DAPM power-down restores `top_audio_h_sel` to 26 MHz.

## Dependencies and Integration Points
Depends on MT8195 clock helpers, register definitions, common ADDA rate transform helpers, ALSA SoC DAI/DAPM/control APIs, and `struct mtkaif_param` in MT8195 private data. It integrates with the machine driver through `mt8195_mt6359_mtkaif_calibration()` and MT6359 codec setup. Its DAPM endpoints connect to memif I/O widgets (`I000`, `I020`, `I070`, etc.) and card routes for `ADDA_INPUT`/`ADDA_OUTPUT`.

## Risks
MTKAIF delay programming is skipped but not failed when calibration is unavailable, so systems may probe while capture timing is marginal. Many register writes ignore return status. `hires_required` is per-DAI state updated only at `hw_params`; route decisions during DAPM must see a current value. The 125 us shutdown delay is timing-sensitive. The ADDA6-only and DMIC controls directly mutate shared MTKAIF parameters and require userspace/board policy to avoid inconsistent capture setup.

## Test Signals
Signals include successful DL_SRC playback and UL_SRC1/UL_SRC2 capture, MTKAIF calibration logs and stable capture from all MISO paths, toggling `MTKAIF_DMIC` and `MTKAIF_ADDA6_ONLY`, route activation of hires clocks above 48 kHz, correct ADDA gain register behavior, no pops or truncation during POST_PMD delay, and capture/playback tests at 8/16/48/96/192 kHz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-etdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-etdm.c

## Purpose
Implements MT8195 eTDM, HDMI TX, and DP TX digital audio DAIs. It defines capture/playback DAIs for ETDM1/2 input, ETDM1/2/3 output, and DPTX, plus DAPM routing, clock source controls, MCLK setup, TDM format handling, cowork synchronization, channel disable handling, HDMI/DP channel muxing, and trigger-time enable sequencing.

## Important APIs, Types, and Functions
`mt8195_dai_etdm_register()` registers this sub-DAI block. DAI ops include `mtk_dai_etdm_startup()`, `mtk_dai_etdm_shutdown()`, `mtk_dai_etdm_hw_params()`, `mtk_dai_etdm_trigger()`, `mtk_dai_etdm_set_sysclk()`, `mtk_dai_etdm_set_fmt()`, `mtk_dai_etdm_set_tdm_slot()`, and HDMI/DP variants `mtk_dai_hdmitx_dptx_*`. `mtk_dai_etdm_configure()` writes common CON0 format/word/channel/slave fields, then dispatches to `mtk_dai_etdm_in_configure()` or `mtk_dai_etdm_out_configure()`. `mtk_dai_etdm_mclk_configure()` selects APLL parent and divider rate. `mt8195_afe_enable_etdm()` and `mt8195_afe_disable_etdm()` maintain an enable reference count protected by `afe_ctrl_lock`.

Key state is `struct mtk_dai_etdm_priv`: clock/data mode, master/slave flags, inversion, format, slots, LRCK width, MCLK frequency/source/direction, cowork source and slave list, disabled input channels, and enable refcount. Device-tree parsing occurs in `mt8195_dai_etdm_parse_of()`.

## Control Flow
Registration attaches DAI drivers, controls, widgets, and routes, allocates per-eTDM private data, aliases DPTX state to ETDM3_OUT, parses DT properties, and computes cowork master/slave lists. Startup enables MCLK divider and audsys clock gates. In cowork mode it enables the master clock and every slave gate. Shutdown reverses that. DAI probe supports an always-on MCLK rate from DT by runtime-resuming the AFE, configuring the clock, enabling it, then releasing runtime PM.

`hw_params` calculates rate, bit width, and channels. In cowork mode it configures the master first, then each slave and sync source selection. Otherwise it configures only the target DAI. Common configuration validates eTDM id, forces slaves when cowork source is set, fixes one-pin channel counts to 2/4/8/16/24, rejects bit-clock rates above 24.576 MHz, writes format/bit length/word length/channel count/slave mode, and programs input/output-specific registers. Input configuration sets AFIFO mode, LRCK width, multi-pin mode, disabled channel pairs, FS timing for masters, and LRCK/BCK inversion. Output configuration sets relatch domain, LRCK width, slave delay behavior or master FS timing, relatch enable timing, and inversion.

HDMI/DP paths use ETDM_OUT3 registers. DPTX additionally programs `AFE_DPTX_CON` channel enable, channel count, and word length; for 8-channel mode it forces one-pin ETDM data mode and 8 channels. HDMI uses multi-pin mode. Triggers enable DPTX first/last around ETDM_OUT3 enable. Generic eTDM triggers enable master before cowork slaves and disable slaves before master.

## State and Persistence
Format, inversion, slave mode, TDM slot width, MCLK direction/frequency, disabled input channels, cowork relationships, and enable refcounts persist in `afe_priv->dai_priv[]`. DT properties persist in private state: `mediatek,<etdm>-mclk-always-on-rate`, `mediatek,<etdm>-multi-pin-mode`, `mediatek,<etdm>-cowork-source`, and input-only `mediatek,<etdm>-chn-disabled`. Hardware register state persists through regmap cache and runtime PM owned by the AFE platform driver.

## Dependencies and Integration Points
Depends on MT8195 AFE clock helpers, runtime PM, regmap, ASoC DAI/DAPM/control APIs, and `mt8195_afe_fs_timing()`. Integrates with audsys gate ids (`aud_tdm_in`, `aud_i2sin`, `aud_tdm_out`, `aud_i2s_out`, `aud_hdmi_out`), top clock selectors/dividers, the machine driver's ETDM BE links, DPTX/HDMI codec init, RT5682/RT1011 clock programming, and SOF route fixups. DAPM routes connect memif I/O matrix nodes to ETDM playback/capture and DL10 to HDMI/DP muxes.

## Risks
The 24.576 MHz BCK limit rejects some high-rate/high-channel/high-width combinations. ETDM1_OUT only supports master mode unless it is a cowork slave. Cowork config can be invalid if DT points a slave to another slave; the code logs but does not fully unwind. DPTX and ETDM3_OUT share private state, so concurrent or conflicting HDMI/DP settings may collide. `mtk_dai_etdm_set_tdm_slot()` stores slot count but only LRCK width materially affects programming. Many regmap writes are unchecked. Input disabled-channel logic assumes paired channels and indexes `i + 1`; odd channel counts need careful validation.

## Test Signals
Signals include probe with all ETDM DAIs visible, DT parsing logs for invalid cowork/channel data, successful I2S/LJ/RJ/DSP_A/DSP_B format setup, master and slave clock polarity tests, always-on MCLK measurement, cowork master/slave simultaneous start and stop, capture with disabled input channels, HDMI and DP jack playback at 2/4/6/8 channels, DPTX register state matching sample format, and rejection of unsupported BCK rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-etdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-pcm.c

## Purpose
Implements the MT8195 legacy PCM interface DAI named `PCM1`, with playback and capture, DAPM routes to the AFE interconnect, PCM format/clock polarity/master-mode setup, and ASRC/PCMIF clock supplies.

## Important APIs, Types, and Functions
`mt8195_dai_pcm_register()` registers the PCM sub-DAI. `mtk_dai_pcm_set_fmt()` stores ASoC format, inversion, and clock-provider policy in `struct mtk_dai_pcmif_priv`. `mtk_dai_pcm_prepare()` calls `mtk_dai_pcm_configure()` when neither playback nor capture widget is active. `mtk_dai_pcm_mode()` maps supported rates to PCM mode values. The only DAI driver is `PCM1`, symmetric in rate and sample bits, with S16/S24/S32 formats and rates from 8 kHz to 48 kHz.

## Control Flow
Registration allocates a sub-DAI descriptor, attaches the DAI driver, DAPM widgets, DAPM routes, and one private `mtk_dai_pcmif_priv`. `set_fmt` accepts I2S, DSP_A, and DSP_B formats, four LRCK/BCLK inversion combinations, and either codec bit/frame clock provider (`BC_FC`, slave mode) or CPU provider (`BP_FP`, master mode). `prepare` avoids reprogramming while either playback or capture is already active, then configures sync frequency, clock domain, PCM mode, format, sync length, word length, master/slave selection, and clock inversion.

For clock domain selection, rates divisible by 8 kHz use the 26 MHz 48 kHz family and 44.1 kHz-family rates use the 26 MHz 44.1 kHz family. Mode A/B force one-bit sync length; I2S/EIAJ style uses sample bit width. Widths above 16 bits use 24-bit and 64-BCK programming, otherwise 16-bit and 32-BCK.

## State and Persistence
Per-DAI state lives in `mtk_dai_pcmif_priv`: slave mode, LRCK inversion, BCLK inversion, and selected format. Hardware configuration persists in `PCM_INTF_CON1` and `PCM_INTF_CON2` until changed or regcache/runtime PM restores it. DAPM state controls `PCM_EN`, `aud_asrc11`, `aud_asrc12`, and `aud_pcmif`.

## Dependencies and Integration Points
Depends on regmap, ALSA PCM params, MT8195 clock/register definitions, and the AFE private state array. It integrates with memif I/O nodes `I002`, `I003`, `O000`, `O001`, `I000/I001`, and `I070/I071`; the MT8195 machine driver exposes `PCM1_BE` using this DAI.

## Risks
Slave-mode ASRC handling is explicitly left as a TODO, so external-clock PCM capture/playback can be incomplete. `prepare` uses DAPM widget active flags and may skip reconfiguration when simultaneous playback/capture requires a new compatible setup. Only a limited set of rates is mapped by `mtk_dai_pcm_mode()`. Unsupported format variants return `-EINVAL`, which can break machine links if DT/topology uses a different ASoC format constant.

## Test Signals
Signals include `PCM1` BE probe, format negotiation for I2S/DSP_A/DSP_B, master and slave clock polarity validation on pins, playback and capture at 8/16/32/44.1/48 kHz, 16-bit versus 24/32-bit BCK width checks, DAPM enabling `PCM_EN` and ASRC clocks, and simultaneous playback/capture behavior with symmetric constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-mt6359.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-mt6359.c

## Purpose
MT8195 machine driver for MT6359-based boards with optional RT5682/RT5682S headset codec, RT1011/RT1019/MAX98390 speaker amplifiers, HDMI, DP, and SOF audio routing. It defines the sound card, DAI links, board variant data, jack setup, codec initialization, BE hw_params policies, MTKAIF calibration, and integration with common MediaTek soundcard/SOF helpers.

## Important APIs, Types, and Functions
The platform driver uses `mtk_soundcard_common_probe` and matches compatibles including `mediatek,mt8195_mt6359`, `mediatek,mt8195_mt6359_rt1019_rt5682`, `mediatek,mt8195_mt6359_rt1011_rt5682`, and `mediatek,mt8195_mt6359_max98390_rt5682`. Card setup is driven by `mt8195_mt6359_soc_card_probe()` or legacy fallback `mt8195_mt6359_legacy_probe()`.

Important init and ops functions include `mt8195_mt6359_mtkaif_calibration()`, `mt8195_mt6359_init()`, `mt8195_rt5682_init()`, `mt8195_rt5682_etdm_hw_params()`, `mt8195_rt1011_init()`, `mt8195_rt1011_etdm_hw_params()`, `mt8195_rt1019_init()`, `mt8195_max98390_init()`, `mt8195_dptx_codec_init()`, `mt8195_hdmi_codec_init()`, `mt8195_dptx_hw_params()`, `mt8195_sof_be_hw_params()`, `mt8195_etdm_hw_params_fixup()`, `mt8195_dai_link_fixup()`, and `mt8195_set_bias_level_post()`.

The DAI link table covers dynamic FE links for DL2/DL3/DL6/DL7/DL8/DL10/DL11 and UL1/UL2/UL3/UL4/UL5/UL6/UL8/UL9/UL10, BE links for DL_SRC, DPTX, ETDM inputs/outputs, PCM1, UL_SRC1/2, and SOF BE links for DL2/DL3/UL4/UL5.

## Control Flow
At card probe, the driver allocates machine private data and either performs legacy node discovery or inspects preconfigured DAI links. It installs init callbacks for DPTX/HDMI if real codecs are attached, ensures MT6359 init is attached once to the ADDA links, and assigns codec-specific init/ops for eTDM links based on codec DAI names. Legacy mode searches compatible RT5682/RT5682S nodes, parses DP/HDMI phandles, and rewrites DAI link codec components for board variants.

MT6359 init sets MTKAIF protocol 2 and runs calibration. Calibration runtime-resumes the AFE, enables codec calibration, drives topckgen test type, sweeps phases 0-42, watches monitor done bits for three MISO paths, detects cycle transitions to choose phases, writes chosen phases back to MT6359, disables calibration, releases runtime PM, and stores calibration status, chosen phases, and phase cycles in `afe_priv->mtkaif_params`.

Codec init functions add jacks, DAPM widgets, controls, routes, and optional codec configurations. RT5682 init creates headset jack pins and button mappings, sets the codec jack, records the I2SO1 MCLK pointer, and adds headset routes. DP/HDMI init creates AVOUT jacks and sets codec jacks. Speaker init adds either dual-speaker or single external-speaker controls/routes. BE hw_params functions set codec PLL/sysclk for RT5682 and RT1011, set DPTX CPU sysclk to rate * 256, and force selected ETDM/DPTX BE formats to S24_LE.

## State and Persistence
`struct mt8195_mt6359_priv` persists the RT5682 I2SO1 MCLK pointer used by `set_bias_level_post` to avoid playback pop noise. `mtkaif_params` persists in the AFE private state and is later consumed by the ADDA DAI. `snd_soc_jack` instances live in common card data. DAI link mutations persist in the shared static card/link structures during probe. Board variant flags choose speaker codec components and codec conf prefixes. PCM constraints force common playback/capture/HDMI-DP streams to 48 kHz and constrained channel lists.

## Dependencies and Integration Points
Depends on ASoC card/link/jack APIs, MT6359 codec APIs, RT5682 and RT1011 codec APIs, common MediaTek soundcard helpers, SOF helper integration, and MT8195 AFE clock/common headers. It integrates with the DAI names exported by the platform driver (`DL2`, `ETDM1_OUT`, `UL_SRC1`, etc.), external codec drivers, DT phandles for DP/HDMI, and SOF connection streams mapping DMA widgets to BE links.

## Risks
The static card and DAI link arrays are mutated at probe, which can be fragile if multiple variants ever bind in one kernel instance. Legacy codec-node discovery by compatible can pick unexpected nodes on complex DTs. MTKAIF calibration busy-waits up to 10000 monitor reads per phase and treats failure as non-fatal, which can lead to later capture issues. `pm_runtime_get_sync()` return values are not checked in calibration. `mt8195_sof_be_hw_params()` rejects inactive AFE PM state, so SOF sequencing bugs surface as hw_params failures. Direct MCLK control in bias callbacks assumes RT5682 init has populated `i2so1_mclk`.

## Test Signals
Signals include card registration for each compatible, FE/BE DPCM route availability, headset jack/buttons, DP and HDMI jack reporting, speaker widgets for RT1011/RT1019/MAX98390 variants, MTKAIF calibration success and stable ADDA capture, RT5682 and RT1011 PLL/sysclk programming during playback, pop-free RT5682 bias transitions, SOF DL/UL route activation, DPTX/HDMI 2/4/6/8-channel playback, and 48 kHz constraint enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-mt6359.c -->
