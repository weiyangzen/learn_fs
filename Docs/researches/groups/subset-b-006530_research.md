<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-reg.h

## Purpose
Register-definition header for the MT8195 ASoC audio front end. It gives the MT8195 platform drivers symbolic offsets for the AFE, ASYS, IRQ, memif, DMIC, ADDA, ETDM, GASRC, SPDIF, DPTX, secure-mask, connection-matrix, and SRAM register spaces, plus field macros for common bit programming.

## APIs, Types, and Functions
This header exports preprocessor constants only. Important address groups include `AUDIO_TOP_CON*`, `ASYS_IRQ*`, `AFE_IRQ*`, `AFE_DAC_CON*`, `AFE_DL*`, `AFE_UL*`, `AFE_CONN*`, `AFE_SECURE_MASK_CONN*`, `AFE_DMIC*`, `ETDM_*`, `AFE_GASRC*`, `AFE_ADDA_*`, and `AFE_DPTX_CON`. `AFE_SRAM_BASE`, `AFE_SRAM_SIZE`, and `AFE_MAX_REGISTER` describe hardware range limits. Field helpers use `BIT()` and `GENMASK()` for top timing, PCM interface configuration, multi-channel microphone capture, MTKAIF, DMIC source configuration, ETDM formatting, DPTX channel enable, and ADDA downlink/uplink controls.

## Control Flow, State, and Persistence
There is no executable control flow or persistent C state in this file. Runtime behavior emerges when MT8195 AFE drivers include these constants and use regmap/MMIO operations to program hardware. The register names encode persistence domains: memif base/end/current registers persist DMA buffer addresses while streams run, connection-matrix and secure-mask registers persist routing/security policy until rewritten or reset, and IRQ/timing/control registers persist stream clocking and interrupt behavior across active runtime power windows.

## Dependencies and Integration
Consumers depend on Linux bitfield helpers made available by included kernel headers in the including compilation units. The file integrates with MT8195 machine/platform DAI, memif, clock, DMIC, ADDA, ETDM, SPDIF, and ASRC code by providing the single source of truth for offsets and masks used in `regmap_update_bits()`, `regmap_write()`, and register backup lists. `AFE_MAX_REGISTER` is suitable for regmap range validation.

## Risks and Test Signals
The main risk is silent hardware misprogramming from a wrong offset, mask, shift, typo, or SoC-revision mismatch; headers like this rarely fail at compile time when a bit definition is semantically wrong. Large repeated ranges such as `AFE_CONN*`, `AFE_SECURE_MASK_CONN*`, and `AFE_GASRC*` are especially sensitive to off-by-one address drift. Test signals are successful MT8195 probe with regmap range checks, working playback/capture on every memif, correct IRQ period accounting, DAPM route toggling through connection registers, suspend/resume register restore, DMIC/ADDA/ETDM/SPDIF/DPTX hardware validation, and register-dump comparison against the MT8195 datasheet or vendor reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8195/mt8195-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/Makefile

## Purpose
Kbuild fragment for MT8365 ASoC support. It defines which object files make up the MT8365 platform AFE module and which machine-driver object is built for the MT8365 plus MT6357 codec card.

## APIs, Types, and Functions
The file declares `snd-soc-mt8365-pcm-y` as a composite object containing `mt8365-afe-clk.o`, `mt8365-afe-pcm.o`, `mt8365-dai-adda.o`, `mt8365-dai-dmic.o`, `mt8365-dai-i2s.o`, and `mt8365-dai-pcm.o`. It wires `obj-$(CONFIG_SND_SOC_MT8365)` to `snd-soc-mt8365-pcm.o` and `obj-$(CONFIG_SND_SOC_MT8365_MT6357)` to `mt8365-mt6357.o`.

## Control Flow, State, and Persistence
There is no runtime state. Build-time control flow is driven by Kconfig: enabling `CONFIG_SND_SOC_MT8365` builds the platform component with all listed sub-DAI implementation objects linked together; enabling `CONFIG_SND_SOC_MT8365_MT6357` builds the matching machine driver.

## Dependencies and Integration
This Makefile is consumed by the kernel sound/soc/mediatek build. The composite object depends on all listed MT8365 source files sharing internal symbols such as `mt8365_afe_enable_main_clk()`, `mt8365_dai_adda_register()`, `mt8365_dai_dmic_register()`, and the I2S/PCM registration functions. The machine driver depends on the platform component being available through ALSA SoC registration and device-tree matching.

## Risks and Test Signals
Risks include omitting a source object that provides a registration callback used by `mt8365-afe-pcm.c`, building machine support without the platform driver selected, or stale object names after source renames. Test signals are successful kernel/module builds for both Kconfig symbols, no unresolved MT8365 symbols at link/modpost time, and runtime probe of both the platform device and MT8365-MT6357 sound card.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.c

## Purpose
Clock and top clock-gate control layer for the MT8365 AFE platform driver. It centralizes devicetree clock lookup, common AFE-on sequencing, top clock-gate reference counting, and APLL tuner/engineering-clock setup used by MT8365 DAI implementations.

## APIs, Types, and Functions
Public functions include `mt8365_afe_init_audio_clk()`, `mt8365_afe_disable_clk()`, `mt8365_afe_set_clk_rate()`, `mt8365_afe_set_clk_parent()`, `mt8365_afe_enable_top_cg()`, `mt8365_afe_disable_top_cg()`, `mt8365_afe_enable_main_clk()`, `mt8365_afe_disable_main_clk()`, `mt8365_afe_emi_clk_on()`, `mt8365_afe_emi_clk_off()`, `mt8365_afe_enable_afe_on()`, `mt8365_afe_disable_afe_on()`, `mt8365_afe_enable_apll_tuner_cfg()`, `mt8365_afe_disable_apll_tuner_cfg()`, `mt8365_afe_enable_apll_associated_cfg()`, and `mt8365_afe_disable_apll_associated_cfg()`. Internal helpers map `MT8365_TOP_CG_*` IDs to `AUDIO_TOP_CON0/1` registers and masks, and set or clear HD engine bits in `AFE_HD_ENGEN_ENABLE`.

## Control Flow, State, and Persistence
Probe calls `mt8365_afe_init_audio_clk()` to fill `mt8365_afe_private.clocks[]` from named clocks. Runtime users call `mt8365_afe_enable_main_clk()`, which prepares `top_audio_sel`, ungates `MT8365_TOP_CG_AFE`, and asserts `AFE_DAC_CON0` bit 0 through `mt8365_afe_enable_afe_on()`. Matching disable paths decrement reference counters and only write hardware when the counter reaches zero. Top clock gates are protected by `afe_ctrl_lock`; APLL tuner counters are protected by `afe_clk_mutex`. APLL-associated enable turns on ENGEN1/2, 22M/24M gates, HD engine bits, tuner top gates, and tuner configuration registers; disable unwinds the sequence.

## Dependencies and Integration
Depends on Linux `clk`, regmap, `struct mtk_base_afe`, MT8365 register definitions, and `struct mt8365_afe_private` from `mt8365-afe-common.h`. All MT8365 sub-DAIs use this layer for startup/shutdown power windows. The platform probe also uses it to set the `top_audio_sel` parent to the 26 MHz clock and to keep AFE registers accessible for DAPM registration.

## Risks and Test Signals
Several clock and regmap operations ignore return codes, and underflow recovery only clamps counters after decrement, so mismatched enable/disable paths can hide sequencing bugs. `get_top_cg_reg()` and `get_top_cg_mask()` return zero for invalid IDs, which could accidentally target `AUDIO_TOP_CON0` with a zero mask. `mt8365_afe_emi_clk_on/off()` are stubs even though PCM DMA fallback calls them. The HD engine disable writes `~AFE_22M_PLL_EN` or `~AFE_24M_PLL_EN` as the value under a one-bit mask, which relies on masked update semantics. Test signals are balanced refcounts under concurrent streams, clean suspend/resume after active streams, clock-tree debugfs showing expected parents/rates, APLL1/APLL2 playback at 44.1k/48k families, and no register access faults when DAPM reads controls while runtime PM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.h

## Purpose
Private MT8365 AFE clock-control interface shared by the platform PCM driver and backend DAI implementations.

## APIs, Types, and Functions
The header forward-declares `struct mtk_base_afe` and `struct clk`, then declares all clock helper entry points implemented by `mt8365-afe-clk.c`: clock initialization, generic disable, rate/parent changes, top clock-gate enable/disable, main AFE clock enable/disable, EMI clock hooks, AFE-on reference control, and APLL tuner/associated configuration enable/disable.

## Control Flow, State, and Persistence
The header carries no state itself. It defines the call boundary through which stream startup, stream shutdown, platform probe, and DAI-specific APLL code manipulate persistent counters and clock pointers stored in `struct mt8365_afe_private`.

## Dependencies and Integration
Included by `mt8365-afe-pcm.c`, `mt8365-dai-adda.c`, `mt8365-dai-dmic.c`, and other MT8365 DAI files. It avoids requiring every includer to pull in full clock headers by using forward declarations, while concrete implementations still depend on Linux `clk` and the common MTK AFE structures.

## Risks and Test Signals
Risks are interface drift between declarations and implementation, lack of kernel-doc describing required pairing rules, and no explicit return contract documenting helpers that currently return success even when internal clock enables fail. Build coverage across all MT8365 objects is the primary static signal; runtime signals are balanced main-clock, top-CG, AFE-on, and APLL enable/disable behavior across every DAI startup/shutdown path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-common.h

## Purpose
Shared private definitions for the MT8365 ASoC AFE driver family. It assigns platform-wide IDs for memory interfaces, backend DAIs, IRQs, clocks, top clock gates, sample-rate encodings, MCLKs, channel-merge blocks, ASRC blocks, and data structures used by the platform, clock, ADDA, DMIC, I2S, PCM, and TDM code.

## APIs, Types, and Functions
Important enums define `MT8365_AFE_MEMIF_*`, `MT8365_AFE_IO_*`, `MT8365_AFE_IRQ*`, `MT8365_TOP_CG_*`, `MT8365_CLK_*`, `MT8365_AFE_APLL*`, I2S sets/clocking, TDM output modes, PCM formats, `MT8365_FS_*`, raw `FS_*HZ` encodings, debugfs indices, IRQ directions, MCLK IDs, `enum mt8365_cm_num`, `enum mt8365_cm2_mux_in`, `enum cm2_mux_conn_in`, DMIC modes, IIR modes, and ASRC IDs. Key structures are `mt8365_fe_dai_data`, `mt8365_be_dai_data`, `mt8365_cm_ctrl_reg`, `mt8365_control_data`, `mt8365_gasrc_ctrl_reg`, `mt8365_gasrc_data`, and `mt8365_afe_private`. Inline helpers `rx_frequency_palette()`, `AutoRstThHi()`, and `AutoRstThLo()` map sample-rate codes to ASRC/auto-reset constants. The header also declares the cross-file registration and configuration functions for rate/channel validation, DAI private data, I2S out, ADDA, DMIC, PCM, and TDM.

## Control Flow, State, and Persistence
This header defines the persistent per-device state stored behind `mtk_base_afe.platform_priv`. `mt8365_afe_private` holds clock handles, SRAM mapping, FE SRAM/dma selection state, BE prepared flags, channel-merge controls, GASRC state, AFE-on and clock-gate refcounts, APLL tuner refcounts, selected TDM output mode, selected CM2 mux input, DAI-on flags, and per-DAI private pointers. These fields are mutated by probe, ALSA stream callbacks, DAPM mux controls, clock helpers, suspend/resume backup, and DAI registration paths.

## Dependencies and Integration
Depends on Linux clock/list/regmap headers, ALSA SoC/asound headers, the common MediaTek `mtk-base-afe.h`, and `mt8365-reg.h`. It is the integration boundary across all MT8365 source files: IDs in this header must match DAI driver IDs, memif tables, IRQ tables, top-CG mappings, `dai_priv[]` indexes, and machine-driver routing assumptions.

## Risks and Test Signals
Array-index correctness is the main risk: `be_data[dai->id - MT8365_AFE_BACKEND_BASE]`, `dai_priv[id]`, `top_cg_ref_cnt[cg]`, `clocks[clk]`, and IRQ/memif tables all rely on enum ordering staying synchronized. The `MT8365_AFE_BACKEND_END` and `MT8365_AFE_BACKEND_NUM` arithmetic makes insertions risky. Inline sample-rate tables return zero for unsupported values, which can look like a valid low constant if callers skip validation. Test signals are successful build of all MT8365 objects, probe without out-of-bounds KASAN reports, DAI registration for every ID, stream tests across FE and BE DAIs, DAPM route tests for CM1/CM2 and ASRC muxes, and suspend/resume with state restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-pcm.c

## Purpose
Main MT8365 AFE platform component driver. It owns platform probe/remove, regmap and IRQ setup, memory-interface DAI registration, PCM hardware constraints, DMA/SRAM buffer programming, channel-merge setup, AFE DAPM widgets/routes, register backup for system sleep, and ALSA FE trigger integration.

## APIs, Types, and Functions
Exported cross-file helpers include `mt8365_afe_fs_timing()`, `mt8365_afe_rate_supported()`, `mt8365_afe_channel_supported()`, and `mt8365_dai_set_priv()`. Core PCM callbacks are `mt8365_afe_fe_startup()`, `mt8365_afe_fe_shutdown()`, `mt8365_afe_fe_hw_params()`, `mt8365_afe_fe_hw_free()`, `mt8365_afe_fe_prepare()`, and `mt8365_afe_fe_trigger()`. Other important functions include `mt8365_afe_irq_direction_enable()`, `mt8365_afe_cm2_mux_conn()`, `mt8365_afe_get_cm_update_cnt()`, `mt8365_afe_configure_cm()`, HW gain callbacks, hostless startup, DAPM CM2 mux get/put, `mt8365_afe_irq_handler()`, suspend/resume helpers, `mt8365_afe_init_registers()`, `mt8365_dai_memif_register()`, `mt8365_afe_pcm_dev_probe()`, and `mt8365_afe_pcm_dev_remove()`. Static data covers PCM hardware limits, register backup lists, sample-rate encodings, CM register maps, DAI drivers, extensive DAPM mixers/routes, memif metadata, IRQ metadata, and fixed memif-to-IRQ assignments.

## Control Flow, State, and Persistence
Probe allocates `struct mtk_base_afe` and `mt8365_afe_private`, maps AFE MMIO and optional SRAM, initializes clocks, creates an MMIO regmap clocked by `top_audio_sel`, allocates memif/IRQ arrays, requests the platform IRQ, registers sub-DAIs through `mt8365_dai_pcm_register()`, `mt8365_dai_i2s_register()`, `mt8365_dai_adda_register()`, `mt8365_dai_dmic_register()`, and local memif registration, combines sub-DAIs, assigns memif/IRQ metadata, enables runtime PM, ungates AFE for DAPM register access, sets `top_audio_sel` to 26 MHz, registers the component, and initializes connection 24-bit registers. FE startup stores the substream, applies buffer/period constraints, enables the main clock, and FE shutdown clears the substream and disables it. `hw_params()` optionally configures CM1 for VUL2 or CM2 for TDM_IN, chooses SRAM when the requested buffer fits, otherwise allocates pages, programs memif base/end registers, mono bits, and FS bits. `prepare()` programs high-definition sample format and routes IRQs to the MCU. `trigger()` gates CM1/CM2 on start/resume and off on stop/suspend before delegating to common `mtk_afe_fe_trigger()`. The IRQ handler reads status and enable masks, calls `snd_pcm_period_elapsed()` for active memifs, and clears handled bits. Suspend backs up a curated register list under the main clock and resume writes it back.

## Dependencies and Integration
Depends on Linux platform, OF, MMIO, DMA, PM runtime, regmap, IRQ, ALSA PCM/ASoC APIs, and MediaTek common AFE helpers. It integrates with the companion MT8365 clock, ADDA, DMIC, I2S, and PCM DAI files through registration callbacks and shared `mt8365_afe_private` state. Device tree must expose compatible `mediatek,mt8365-afe-pcm`, MMIO resource 0, optional SRAM resource 1, an IRQ, and the named clocks required by `mt8365-afe-clk.c`.

## Risks and Test Signals
Risks include unchecked return values from constraint, regmap, and PM calls; global `mCM2Input` shared across devices; CM update-count arithmetic returning `-1` after unsigned underflow checks; SRAM physical addresses stored in 32-bit fields; EMI clock hooks being no-ops for external DMA fallback; `pm_runtime_get_sync()` not being balanced visibly in probe; IRQ handler calling period elapsed when `memif->substream` could be NULL after races; and enum/table ordering coupling across memif, IRQ, and DAI IDs. Test signals are platform probe/removal, component registration, period IRQs for every FE, SRAM and non-SRAM buffer paths, mono/stereo and 16/24/32-bit format programming, CM1 VUL2 and CM2 TDM_IN capture, DAPM route toggles for hostless FM and HW gain, runtime/system suspend-resume with register restoration, and KASAN/lockdep coverage during concurrent playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-adda.c

## Purpose
Internal analog AD/DA backend DAI implementation for MT8365. It programs ADDA downlink/uplink source blocks, shared ADDA AFE-on state, DAC/ADC clock gates, I2S output coupling for playback, and DAPM routes for internal DAC playback, internal ADC capture, and hostless FM-to-ADDA paths.

## APIs, Types, and Functions
Public functions are `mt8365_dai_enable_adda_on()`, `mt8365_dai_disable_adda_on()`, and `mt8365_dai_adda_register()`. Internal stream helpers include `mt8365_dai_set_adda_out()`, `mt8365_dai_set_adda_in()`, `mt8365_dai_set_adda_out_enable()`, `mt8365_dai_set_adda_in_enable()`, `mt8365_dai_int_adda_startup()`, `mt8365_dai_int_adda_shutdown()`, and `mt8365_dai_int_adda_prepare()`. The file defines the `"INT ADDA"` DAI driver, DAI ops, DAPM mixers `ADDA_DL_CH1/CH2`, virtual switch `INT ADDA O03_O04`, and routes connecting O03/O04, `AIN Mux`, `Hostless FM DL`, and the ADDA streams.

## Control Flow, State, and Persistence
Startup enables the main AFE clock and gates DAC plus pre-distortion clocks for playback or ADC clock for capture. Prepare is idempotent per stream via `be_data[].prepared[]`; playback programs downlink rate/voice mode, pre-distortion and SDM defaults, configures I2S output by rate/bit width, then enables ADDA downlink and I2S output. Capture programs the uplink sampling rate, selects internal ADC, enables UL source, asserts ADDA AFE-on, and enables `AFE_AUD_PAD_TOP` FIFO bits. Shutdown disables the prepared direction, clears I2S/ADDA enables, disables stream-specific clock gates, and disables the main clock. Shared ADDA AFE-on is tracked by a file-scope `adda_afe_on_ref_cnt` protected by `afe_ctrl_lock`.

## Dependencies and Integration
Depends on regmap, ALSA PCM params, MT8365 clock/common headers, and MediaTek `mtk-dai-adda-common.h` for rate transforms. It is registered by `mt8365-afe-pcm.c` and shares ADDA AFE-on state with the DMIC DAI, which calls `mt8365_dai_enable_adda_on()` and `mt8365_dai_disable_adda_on()` for the DMIC clock divider. Playback also depends on I2S helpers declared in `mt8365-afe-common.h`.

## Risks and Test Signals
The file-scope `adda_afe_on_ref_cnt` is global rather than per device, which is risky if multiple MT8365 AFE instances ever exist. Many `regmap_update_bits()` and I2S helper return paths are either ignored or only partly propagated. Disable paths use bitwise negated values under masks, relying on regmap masking semantics. Hardware sequencing includes required delays only on uplink disable, so playback pop/click behavior depends on register defaults and external analog paths. Test signals are internal DAC playback at 8/16/44.1/48 kHz, internal ADC capture at 16/32/48 kHz, simultaneous DMIC/ADDA refcount balance, DAPM route activation for `AIN Mux` and hostless FM, clean shutdown with no ADDA underflow warnings, and audio quality checks for the programmed -0.3 dB downlink gain and SDM defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-dmic.c

## Purpose
Digital microphone backend DAI implementation for MT8365. It configures up to four DMIC source registers for 1-8 capture channels, controls DMIC clock gates and the ADDA DMIC clock divider, exposes IIR controls, and registers DAPM routes from the DMIC capture stream into AFE input widgets.

## APIs, Types, and Functions
The public entry point is `mt8365_dai_dmic_register()`. Internal state is `struct mt8365_dmic_data`, holding two-wire mode, per-channel clock phase, IIR fields, mode, and active channel count. Important helpers are `get_chan_reg()`, `audio_dmic_adda_enable()`, `audio_dmic_adda_disable()`, `mt8365_dai_enable_dmic()`, `mt8365_dai_disable_dmic()`, `mt8365_dai_configure_dmic()`, `mt8365_dai_dmic_startup()`, `mt8365_dai_dmic_shutdown()`, `mt8365_dai_dmic_prepare()`, and `init_dmic_priv_data()`. Static ASoC data defines the `"DMIC"` capture DAI, IIR switch/enum controls, one `DMIC In` widget, and routes from `DMIC Capture` to AFE inputs `I14` through `I21`.

## Control Flow, State, and Persistence
Registration allocates an AFE sub-DAI, attaches controls/widgets/routes, then allocates DMIC private data. `init_dmic_priv_data()` reads optional `mediatek,dmic-mode`; when not in two-wire mode it defaults channel clock phases to 0 and 4. Startup enables the main AFE clock, ungates all four DMIC ADC clock gates, and enables the shared ADDA AFE-on plus DMIC clock-divider bit. Prepare configures the register selected by `dai->symmetric_channels`, stores the active channel count, programs SDM 3-level mode, optional two-wire mode or clock phases, and one of the supported voice-mode encodings for 8/16/32/48 kHz, then enables channel 1, channel 2, and source bits for the active register. Shutdown disables the active DMIC source, clears the DMIC clock divider, decrements ADDA AFE-on, waits 125-300 us, ungates all DMIC clocks, and disables the main AFE clock.

## Dependencies and Integration
Depends on Linux bitops/regmap, ALSA PCM params, MT8365 clock/common definitions, ADDA AFE-on helpers from `mt8365-dai-adda.c`, and the MT8365 register field definitions. It is registered by `mt8365-afe-pcm.c` and integrated into the shared DAPM graph via AFE input nodes consumed by VUL/VUL2/TDM capture routes.

## Risks and Test Signals
`mt8365_dai_configure_dmic()` uses `dai->symmetric_rate` and `dai->symmetric_channels` instead of directly reading `substream->runtime`, so correctness depends on ASoC symmetric fields being populated as intended. The DAI advertises 16/32/48 kHz but the switch accepts 8 kHz too, while `mt8365_afe_rate_supported()` also allows 8 kHz for DMIC. IIR controls only target `AFE_DMIC0_UL_SRC_CON0`, so multi-pair DMIC configurations may not expose independent IIR settings. `of_property_read_u32_array()` uses a temporary array for one value and ignores malformed multi-value policy. Test signals are capture with 1-8 channels, 16/32/48 kHz and any intended 8 kHz path, two-wire and phase-select hardware variants, IIR switch/mode control behavior, DAPM route activation into VUL/VUL2, ADDA refcount balance with simultaneous internal ADDA streams, and shutdown timing with no stale DMIC clock gates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-dmic.c -->
