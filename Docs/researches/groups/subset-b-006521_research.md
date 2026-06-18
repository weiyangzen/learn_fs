# Research: subset-b-006521 mt8188 ASoC audio files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.c

Purpose: Implements the MT8188 AFE clock helper layer used by the PCM platform and DAI drivers. It maps local `MT8188_CLK_*` IDs to device clock names, registers audsys gates through `mt8188_audsys_clk_register()`, obtains all clocks with `devm_clk_get()`, and provides exported wrappers for prepare/enable, disable, rate, parent selection, APLL tuner setup, top clock-gate bits, and main AFE power-on timing.

Important APIs and functions: `mt8188_afe_init_clock()` is the entry point from platform probe. It registers local audsys clock gates, allocates `afe_priv->clk`, gets every named clock, and initializes five tuner configs. `mt8188_afe_enable_clk()` and `mt8188_afe_disable_clk()` wrap common clock API calls and are exported for other modules. `mt8188_afe_set_clk_rate()` and `mt8188_afe_set_clk_parent()` are convenience helpers for eTDM MCLK routing. `mt8188_apll1_enable()/disable()` and `mt8188_apll2_enable()/disable()` sequence APLL tuner, A1/A2 system clocks, and parent muxing. `mt8188_afe_enable_reg_rw_clk()` and `mt8188_afe_disable_reg_rw_clk()` gate the clocks required for register and SRAM/DRAM access. `mt8188_afe_enable_main_clock()` toggles 26 MHz timing and `AFE_DAC_CON0` AFE-on.

Control flow: probe calls `mt8188_afe_init_clock()`. Runtime resume enables register-access clocks, syncs regcache, and enables main clock. DAPM eTDM APLL supplies call the APLL enable/disable helpers. APLL1 additionally enables `TOP_APLL1_D4`, switches `top_a1sys_hp` to it, enables tuner and A1SYS timing, and unwinds in reverse on failure. APLL2 enables tuner plus A2SYS timing. Top clock gates are written via `ASYS_TOP_CON` bit masks.

State and persistence: APLL tuner state is stored in static `mt8188_afe_tuner_cfgs`, including per-tuner spinlocks and `ref_cnt`. Hardware state persists in AFE registers and common clock framework state; regcache policy is handled by the PCM platform file.

Dependencies and integration: Depends on Linux CCF, regmap, `mt8188-afe-common.h`, `mt8188-afe-clk.h`, audsys clock registration, and register definitions. eTDM uses MCLK source helpers and APLL event helpers. Runtime PM uses register-access and main-clock helpers.

Risks: `mt8188_afe_enable_tuner_clk()` ignores return values from the two clock enables, so partial failures may still lead to tuner enable. `mt8188_afe_disable_apll_tuner()` decrements before underflow repair and disables clocks even when the reference count was already zero, which can unbalance callers if DAPM events pair incorrectly. MCLK source helpers only accept 26M/APLL1/APLL2 even though enum values include APLL3-5. Clock name/order must stay aligned with `MT8188_CLK_*`; missing DT clock providers fail probe.

Test signals: Boot/probe should show no `devm_clk_get` errors and audsys registration should succeed. Runtime PM suspend/resume should not produce regcache or clock imbalance warnings. ALSA eTDM playback/capture at 44.1 kHz and 48 kHz families should select APLL2 and APLL1 respectively. Clock summaries and tracepoints should show balanced APLL tuner and MCLK enables across DAPM start/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.h

Purpose: Declares the MT8188 AFE clock contract shared by the platform and DAI implementations. It defines stable clock IDs, audio PLL IDs, MCLK source selectors, APLL widget names, and the public helper prototypes implemented by `mt8188-afe-clk.c`.

Important APIs and types: The first enum defines `MT8188_CLK_*` IDs for the 26 MHz root, APLL roots, APLL dividers, top muxes, ADSP/audio 26M, AFE gates, DMIC/ADDA/eTDM/PCMIF gates, memif gates, and `MT8188_CLK_NUM`. The second enum defines `MT8188_AUD_PLL1` through `MT8188_AUD_PLL5`. The third enum defines MCLK selectors from 26M through APLL5. Public helpers cover source selection (`mt8188_afe_get_mclk_source_clk_id()`, `mt8188_afe_get_default_mclk_source_by_rate()`), clock registration (`mt8188_afe_init_clock()`), generic clock operations, APLL enable/disable, main AFE clock enable/disable, and register-read/write clock enable/disable.

Control flow and integration: This header is included by all mt8188 audio implementation files that need clocks. The PCM platform calls initialization and runtime-PM helpers. eTDM uses MCLK source, clock parent/rate, and APLL helpers. ADDA, DMIC, and PCMIF rely on clock IDs indirectly through DAPM clock supplies and private clock arrays.

State and persistence: The header itself stores no state, but its enum numeric order is persistent ABI inside this driver set because `mt8188-afe-clk.c` indexes the `aud_clks[]` name table by these values and `mt8188_afe_private->clk` is allocated to `MT8188_CLK_NUM`.

Dependencies: Requires a forward declaration of `struct mtk_base_afe` and references `struct clk` in prototypes without declaring it in this file. In practice, users include Linux clock headers or another header that declares it.

Risks: Enum/name-table drift is the main maintenance risk. `MT8188_CLK_AUD_TOP0_SPDF` exists in the enum but the corresponding `aud_clks[]` entry in the implementation is not populated in the scanned source, while later clock IDs are populated by designated initializers. That is survivable only because designated initializers are used, but any consumer requesting the unpopulated ID would get a NULL clock name. The MCLK enum lists APLL3-5, but implementation helpers reject those selectors.

Test signals: Compile coverage catches missing `struct clk` visibility and prototype mismatches. Probe coverage catches missing clock-name providers for populated IDs. eTDM MCLK tests should confirm 26M/APLL1/APLL2 selector behavior and verify unsupported APLL3-5 paths fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-common.h

Purpose: Provides shared MT8188 ASoC identifiers and private state for the AFE platform and sub-DAI registration files. It is the central cross-file contract for memif IDs, backend IO DAI IDs, IRQ IDs, top clock-gate IDs, MTKAIF calibration data, per-IRQ timing state, and per-DAI private pointers.

Important APIs and types: The main DAI enum lays out all DAI IDs from memory interfaces (`DL2`, `DL3`, `DL6`, `DL7`, `DL8`, `DL10`, `DL11`, `UL1`, `UL2`, `UL3`, `UL4`, `UL5`, `UL6`, `UL8`, `UL9`, `UL10`) through backend IO (`DL_SRC`, `DMIC_IN`, `DPTX`, eTDM IN/OUT, `PCM`, `UL_SRC`). The IRQ enum defines MCU and ASYS IRQ slots used by `irq_data` in `mt8188-afe-pcm.c`. The eTDM timing enum defines special FS selectors used when memif IRQs are synchronized to eTDM domains. `struct mt8188_afe_private` stores clock arrays, clock lookups, optional `topckgen`, runtime-PM bypass state, a spinlock, per-IRQ timing selections, MTKAIF params, and `dai_priv[]`.

Control flow and integration: Platform probe allocates `struct mt8188_afe_private` and then each DAI registration function allocates its own state into `dai_priv[id]`. ADDA reads and writes `mtkaif_params`. PCM controls update `irq_priv[]` and memif private state. eTDM, DMIC, ADDA, and PCMIF all retrieve their private state through this common array. The file declares the registration functions invoked from the platform DAI registration callback table.

State and persistence: This header defines memory layout only. Runtime state persists in the allocated `mt8188_afe_private` for the lifetime of the platform device. The enum numeric values are persistent internal IDs and must match memif/IRQ data tables, DAPM route naming assumptions, and DAI driver IDs.

Dependencies: Includes Linux list/regmap, ALSA SoC headers, and common MediaTek base AFE definitions. The `MT8188_SOC_ENUM_EXT` macro wraps ALSA mixer control initialization while storing a DAI or IRQ ID in `.device`, which several custom control handlers use to find state.

Risks: Any enum insertion can break table indexing in `memif_data`, `irq_data`, `mt8188_afe_memif_const_irqs`, and `dai_priv`. `dai_priv` is a `void *` array, so wrong IDs become runtime type confusion rather than compile-time failures. The macro stores IDs in ALSA control `.device`; handlers depend on that field remaining untouched.

Test signals: Build with all mt8188 sub-drivers catches missing declarations. Probe should allocate every private object before controls are used. ALSA control tests for memif timing, DMIC gain, ADDA DMIC switch, and eTDM settings exercise the shared private state paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-pcm.c

Purpose: Main MT8188 ALSA ASoC AFE platform driver. It defines FE memif DAIs, memory interface register metadata, IRQ metadata and handler, AFE regmap policy, runtime PM, reset/probe sequencing, DAPM routing for the internal interconnect, and registration of all backend DAI modules.

Important APIs and functions: `mt8188_afe_fs_timing()` maps sample rates to register timing values and is exported through the common header. FE operations are `mt8188_afe_fe_startup()`, `mt8188_afe_fe_hw_params()`, and `mt8188_afe_fe_trigger()`. Startup applies 64-byte buffer alignment and a DL7 period-size limit. HW params programs channel merge blocks for UL2/UL9/UL10 and channel-count registers. Trigger enables channel merge, memif, IRQ counter, IRQ FS, capture delay, and IRQ enable on start, then disables and clears IRQ on stop. `mt8188_afe_irq_handler()` demultiplexes shared IRQ status to active memifs and calls `snd_pcm_period_elapsed()`. Probe is `mt8188_afe_pcm_dev_probe()`.

Control flow: Probe initializes reserved DMA memory, 33-bit DMA mask, AFE objects, MMIO, infracfg bus protection, reset, clocks, IRQ/memif arrays, fixed IRQ mapping, platform IRQ, sub-DAI list, and combined component registration. It resumes runtime PM temporarily to initialize regmap from hardware, applies clock-gate patches, registers the component, writes defaults, then returns with regcache cache-only and dirty. Runtime resume performs an ARM SMC for audio domain sidebands, enables register-access clocks, syncs cache, and enables main AFE clock. Runtime suspend disables main clock, switches regcache cache-only/dirty, and disables register-access clocks.

State and persistence: Per-memif state lives in base AFE memif objects plus `mtk_dai_memif_priv` entries in `dai_priv`. ALSA controls persist memif/IRQ timing selections in private state and registers. Register state is cached by flat regcache except volatile monitor/status/current registers. Memif IRQ assignments are fixed by `mt8188_afe_memif_const_irqs`.

Dependencies and integration: Uses common MediaTek AFE helpers (`mtk_afe_fe_*`, `mtk_memif_set_enable/disable`, `mtk_afe_combine_sub_dai`), regmap, reset controller, syscon infracfg, PM runtime, ASoC DAPM/control APIs, and the DAI registration functions from ADDA, DMIC, eTDM, and PCMIF.

Risks: Runtime suspend ignores errors from clock disable helpers, and probe reset error paths after bus protection enable do not visibly disable bus protection before returning. IRQ handler masks status with `AFE_IRQ_MASK`; if mask semantics change, period callbacks can be missed. Large DAPM route/control tables and memif/IRQ metadata are high risk for bit-position drift, so build and route coverage are important.

Test signals: Kernel build for this file is mandatory because table initializers are fragile. Probe should validate reset, clock, IRQ, and component registration. `aplay`/`arecord` through each memif should trigger period elapsed without IRQ storms. Runtime PM tests should suspend/resume during idle and after streams. ALSA control tests should set 1x/fs timing controls and verify IRQ FS register changes on trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-afe-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.c

Purpose: Registers MT8188 audio subsystem gate clocks that are backed by AFE audio top registers rather than separate clock-controller nodes. These gates are made available through `clkdev` so the AFE driver and DAPM `SND_SOC_DAPM_CLOCK_SUPPLY` widgets can obtain them by connection ID.

Important APIs and functions: `struct afe_gate` describes each gate ID, name, parent name, register offset, bit, flags, and gate polarity. Macros `GATE_AUD0`, `GATE_AUD1`, `GATE_AUD3`, `GATE_AUD4`, `GATE_AUD5`, and `GATE_AUD6` instantiate gates for `AUDIO_TOP_CON*` registers with `CLK_SET_RATE_PARENT` and `CLK_GATE_SET_TO_DISABLE`. `mt8188_audsys_clk_register()` allocates `afe_priv->lookup`, calls `clk_register_gate()` for every `aud_clks[]` entry, creates `clk_lookup` records, and installs a devm cleanup action. `mt8188_audsys_clk_unregister()` unregisters gates and drops lookups.

Control flow: `mt8188_afe_init_clock()` calls this before `devm_clk_get()` on the same names. Each successful gate registration creates a lookup with `dev_id = dev_name(afe->dev)`, allowing later device-scoped clock gets. On device teardown or devm reset, cleanup iterates lookups, unregisters gate clocks, and drops clkdev entries.

State and persistence: Gate lookup pointers are stored in `mt8188_afe_private->lookup`. Hardware gate state persists in `AUDIO_TOP_CON0/1/3/4/5/6` registers. Clock framework state persists until devm cleanup.

Dependencies and integration: Depends on Linux clock provider and clkdev APIs, AFE MMIO base address, `mt8188-audsys-clkid.h` ID count, and register offsets from `mt8188-reg.h`. Clock names match `mt8188-afe-clk.c`'s `aud_clks[]` and DAPM clock supply names such as `aud_dac`, `aud_pcmif`, and `aud_hdmi_out`.

Risks: `clk_register_gate()` failures are logged but do not abort registration, so missing clocks may surface later in `devm_clk_get()` rather than at the original failure. If `kzalloc_obj(*cl)` fails after some gates are registered, cleanup coverage depends on devm action registration not yet installed; this can leak earlier gates. Register offsets assume `afe->base_addr + reg` is valid for all audio top gate registers. ID order must match `CLK_AUD_NR_CLK`.

Test signals: Probe should create all expected clock lookups and later `devm_clk_get()` in `mt8188_afe_init_clock()` should succeed. DAPM path tests for ADDA, DMIC, eTDM, PCMIF, and memifs should show gate enable/disable transitions. Module unload or device removal should not leave stale clkdev lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.h

Purpose: Small public header for the local audsys gate-clock registration helper.

Important API: Declares `int mt8188_audsys_clk_register(struct mtk_base_afe *afe);`, implemented in `mt8188-audsys-clk.c` and called from `mt8188_afe_init_clock()` before the driver resolves its clock array.

Control flow and integration: This header is included by `mt8188-afe-clk.c`, making audsys gate registration part of the higher-level AFE clock initialization sequence. The registration helper installs clock provider objects and clkdev lookups scoped to the AFE device.

State and persistence: The header has no state. The function it declares populates `mt8188_afe_private->lookup` and registers common-clock-framework gate objects.

Dependencies: The prototype references `struct mtk_base_afe` without a local forward declaration. Current include order works because callers include common AFE headers first; future direct users should include the common header or add a forward declaration.

Risks: Because this header exposes only a single helper and no type definitions, drift risk is low. The main maintenance risk is include hygiene: direct inclusion without a prior declaration of `struct mtk_base_afe` can produce compiler warnings or errors depending on context.

Test signals: Compile coverage of `mt8188-afe-clk.c` is sufficient for this header. Probe success through `mt8188_afe_init_clock()` confirms the declared integration path is functioning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clkid.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clkid.h

Purpose: Defines the local audio subsystem gate-clock IDs consumed by `mt8188-audsys-clk.c`. The enum indexes the `aud_clks[CLK_AUD_NR_CLK]` gate descriptor array and names the gate set for AFE core, tuners, ADDA, DMIC, eTDM, PCMIF, memifs, and GASRC clocks.

Important definitions: IDs include core and tuner gates (`CLK_AUD_AFE`, `CLK_AUD_APLL1_TUNER`, `CLK_AUD_APLL2_TUNER`), ADDA gates (`CLK_AUD_DAC`, `CLK_AUD_ADC`, hires variants), DMIC gates, line-in/eARC tuner gates, eTDM/PCMIF related gates (`CLK_AUD_I2SIN`, `CLK_AUD_TDM_IN`, `CLK_AUD_I2S_OUT`, `CLK_AUD_TDM_OUT`, `CLK_AUD_HDMI_OUT`, `CLK_AUD_PCMIF`), memory interface gates for UL/DL memifs, GASRC gates, and `CLK_AUD_NR_CLK`.

Control flow and integration: `mt8188-audsys-clk.c` uses these values as designated indexes into the gate descriptor array. `CLK_AUD_NR_CLK` controls allocation size and unregister loop bounds. The higher-level `MT8188_CLK_AUD_*` IDs in `mt8188-afe-clk.h` are separate but must map by clock name to these registered gates.

State and persistence: The enum itself stores no runtime state, but its numeric order is a persistent internal ABI for the descriptor table and cleanup arrays.

Dependencies: Independent header with only include guards. It is included by the audsys clock registration implementation.

Risks: Reordering or inserting IDs without matching `aud_clks[]` descriptors can register gates under wrong indexes or leave NULL lookup slots. Because the descriptor table uses designated initializers in this tree, omissions become missing clocks rather than positional misregistration, but cleanup still iterates to `CLK_AUD_NR_CLK`.

Test signals: Build validates enum names used by `mt8188-audsys-clk.c`. Runtime probe plus clock lookup tests validate every descriptor name has a usable gate. DAPM path testing validates the subset needed by active audio routes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-audsys-clkid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-adda.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-adda.c

Purpose: Implements the MT8188 analog/digital audio front-end backend DAIs for ADDA playback (`DL_SRC`) and capture (`UL_SRC`). It handles MTKAIF receive setup, analog uplink DMIC mode, ADDA sample-rate programming, hi-res clock routing, DAPM widgets/routes, and user controls for DL gain and MTKAIF DMIC selection.

Important APIs and functions: `mt8188_dai_adda_register()` adds the ADDA DAI group to `afe->sub_dais`. `mt8188_adda_mtkaif_init()` configures MTKAIF protocol2 and optional calibrated MISO delay. `mtk_adda_dl_event()` and `mtk_adda_ul_event()` handle DAPM power timing and mic type setup. `mtk_afe_adda_hires_connect()` conditionally connects hires clock supplies based on per-DAI `hires_required`. `mtk_dai_adda_hw_params()` records whether the stream is above 48 kHz and calls DA or AD register configuration. `mt8188_adda_dmic_get/set()` exposes MTKAIF DMIC mode.

Control flow: Register allocates two `mtk_dai_adda_priv` objects into `dai_priv[DL_SRC]` and `dai_priv[UL_SRC]`, then exposes widgets/routes/controls. During hw_params, playback configures DL input mode, disables saturation, unmutes channels, handles voice mode for 8/16 kHz, and enables new second SDM. Capture configures UL voice mode. During DAPM capture power-up, MTKAIF configuration and mic-type bits are programmed. Power-down delays 125 us before AFE off.

State and persistence: Per-DAI state is `hires_required`. Shared MTKAIF state in `mt8188_afe_private->mtkaif_params` tracks calibration success, selected phases, phase cycles, and `mtkaif_dmic_on`. Hardware state is in ADDA and pad registers.

Dependencies and integration: Uses MediaTek ADDA common transform helpers, regmap, bitfield helpers, ASoC DAPM/control APIs, and clocks registered as DAPM supplies (`aud_dac`, `aud_adc`, hires variants). Its I/O connects to AFE memif routing through I/O widgets such as `I168/I169`, `O176/O177`, and ADDA input/output endpoints.

Risks: If MTKAIF calibration is not marked OK, the driver silently continues with protocol setup but no delay compensation. `mtk_afe_adda_hires_connect()` relies on widget-name substring matching. DMIC mode is cached and applied only on DAPM UL power-up, so changing the control during an active path may not immediately reprogram hardware. Rate transforms must stay aligned with supported rates.

Test signals: Playback and capture at 48 kHz and 96/192 kHz should toggle normal and hires clock supplies appropriately. Capture tests should cover analog mic and MTKAIF DMIC switch before stream start. Mixer tests should validate `ADDA_DL_GAIN` and route controls. Logs should show no calibration-related errors unless expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-adda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-dmic.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-dmic.c

Purpose: Implements the MT8188 digital microphone backend DAI. It supports 1 to 8 channel capture across four DMIC controller blocks, loads fixed IIR coefficients, configures source selection and rate modes, controls DMIC clocks and FIFO reset, and exposes hardware gain controls for four DMIC gain engines.

Important APIs and functions: `mt8188_dai_dmic_register()` registers the DAI, DAPM widgets/routes, and mixer controls. `mtk_dai_dmic_hw_params()` validates channel count, programs DMIC source array selection, loads IIR coefficients, chooses voice mode by rate, writes controller registers for the needed DMIC blocks, and caches channel count plus hires requirement. `mtk_dmic_event()` handles DAPM sequencing for FIFO soft reset, source enable, IIR/SDM bits, normal/hires clocks, and power-down delay. `mtk_dmic_gain_event()` enables or bypasses hardware gain based on cached mixer settings. `mtk_dai_dmic_hw_gain_ctrl_get/put()` implements four enum controls.

Control flow: Registration allocates one `mtk_dai_dmic_priv` at `dai_priv[DMIC_IN]`. HW params maps channels to the highest required DMIC block (`DMIC0` for one channel through `DMIC3` for four or more) and applies the same mode bits to all required blocks. DAPM `DMIC_CK_ON` asserts FIFO soft reset before PMU, enables UL source and clocks after PMU, clears setup bits before PMD, and disables clocks after PMD. `DMIC_GAIN_ON` enables or bypasses each gain engine before/after the path.

State and persistence: `mtk_dai_dmic_priv` stores per-DMIC gain enable flags, active channel count, and whether hires clocks are needed. Hardware state persists in DMIC controller, gain, IIR coefficient, and PWR2 top registers.

Dependencies and integration: Uses regmap, ASoC controls/DAPM, PCM params, and clock helpers. Routes expose capture data through `I004` to `I011` into the wider AFE interconnect. Clock IDs come from `mt8188-afe-clk.h`.

Risks: `mtk_dmic_event()` returns `-EINVAL` if DAPM powers before `hw_params` has set channels, so route activation order matters. For channels above four, `mtk_dmic_channels_to_dmic_number()` still selects all four DMIC blocks; channel-to-block semantics depend on hardware pairing. Unsupported rates fall back to 48 kHz register mode despite the DAI rate mask limiting public rates. Hires clock enable calls ignore return values. Gain control identity is string-matched by control name.

Test signals: Capture with 1, 2, 4, and 8 channels should verify correct DMIC block enables and FIFO reset release. 96 kHz capture should enable hires DMIC clocks; 8/16/32/48 kHz should not. Mixer tests should toggle each `DMIC*_HW_GAIN_EN` and gain target/current/step controls. Power-cycle tests should check no clock imbalance warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-dmic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-etdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-etdm.c

Purpose: Implements MT8188 eTDM, HDMI TX, and DisplayPort TX backend DAIs. It manages eTDM IN/OUT formatting, channel packing, AFIFO, master/slave polarity, MCLK/APLL routing, cowork synchronization between eTDM ports, HDMI/DP mux routing, DAPM supplies, user clock-source controls, and device-tree parsing for multi-pin, cowork, and disabled-channel options.

Important APIs and functions: `mt8188_dai_etdm_register()` registers six DAIs (`DPTX`, `ETDM1_IN`, `ETDM2_IN`, `ETDM1_OUT`, `ETDM2_OUT`, `ETDM3_OUT`). `mtk_dai_etdm_set_fmt()`, `mtk_dai_etdm_set_sysclk()`, and `mtk_dai_etdm_set_tdm_slot()` cache DAI format, MCLK, and slot settings. `mtk_dai_etdm_hw_params()` configures master plus cowork slaves when needed. `mtk_dai_etdm_configure()` validates bit clock limits and writes common format/word/channel/slave fields. IN/OUT helpers program AFIFO, FS timing, LRCK width, polarity, relatch, multi-pin mode, and disabled-channel handling. HDMI/DPTX ops program `AFE_DPTX_CON` and reuse eTDM OUT3 registers.

Control flow: Init allocates private state for eTDM DAI IDs, aliases `DPTX` to `ETDM3_OUT`, parses DT properties, and builds cowork slave lists. DAPM route predicates decide which APLL, MCLK, clock gate, and cowork supplies are active. APLL DAPM events call APLL helpers in `mt8188-afe-clk.c`; MCLK events set parent/rate and enable mux/divider clocks. Hw_params either configures a single DAI or configures the cowork master and all slaves, then writes sync mode for slaves.

State and persistence: `mtk_dai_etdm_priv` stores data mode, master/slave mode, inversion, rate, format, slots, LRCK width, MCLK frequency/APLL/direction, cowork source/slaves, and disabled input channel flags. Hardware state persists in `ETDM_*` registers, cowork registers, APLL and top clock state, HDMI/DP mux registers, and DAPM supply state.

Dependencies and integration: Uses clock helpers, regmap, ASoC DAI/DAPM/control APIs, PCM params, and MT8188 register definitions. Routes connect memifs DL10/UL3/UL8 and AFE internal widgets to eTDM and HDMI/DPTX outputs. DT properties include `mediatek,<etdm>-multi-pin-mode`, `mediatek,<etdm>-cowork-source`, and input-only `mediatek,<etdm>-chn-disabled`.

Risks: Many paths depend on widget/control name string matching, so route renames can break behavior. `mclk_fixed_apll` is present but not parsed in this file; fixed APLL behavior may be dead unless set elsewhere. MCLK enable ignores the return from `mt8188_afe_set_clk_rate()` and enables the divider anyway. `ETDM1_OUT` rejects slave mode while other ports allow it. Disabled-channel logic indexes `i + 1`, so odd channel counts need careful validation. Cowork source cycles are only logged as errors for nested master relationships, not rejected.

Test signals: Run capture on ETDM1/2 IN and playback on ETDM1/2/3 OUT at 44.1/48/96/192 kHz with I2S and DSP formats. Test MCLK sysclk values divisible by APLL rate and invalid values. Validate cowork DT setups with one master and multiple slaves. HDMI/DPTX playback should verify channel enable/width bits and mux controls. Runtime PM should keep MCLK/APLL gates balanced across DAPM transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-etdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-pcm.c

Purpose: Implements the MT8188 PCM1 backend DAI, including PCM/I2S/DSP format selection, master/slave clock polarity, sync frequency setup, channel routing widgets, and clock supplies for PCMIF and ASRC blocks.

Important APIs and functions: `mt8188_dai_pcm_register()` registers the PCM DAI group. `mtk_dai_pcm_set_fmt()` decodes ALSA DAI format, inversion, and clock-provider flags into cached `mtk_dai_pcmif_priv` state. `mtk_dai_pcm_prepare()` programs hardware only if playback and capture widgets are inactive. `mtk_dai_pcm_configure()` writes sync frequency, clock domain, PCM mode, format, sync length, bit width, word length, master/slave mode, and clock inversion. `mtk_dai_pcm_mode()` maps supported rates to PCM mode values.

Control flow: Registration allocates `mtk_dai_pcmif_priv` at `dai_priv[PCM]`, exposes one DAI with symmetric rate and sample bits, and installs DAPM widgets/routes. Machine-driver `set_fmt` stores mode before stream prepare. On prepare, the driver avoids reconfiguring if either direction is already active, preserving symmetric full-duplex settings. Runtime rate is converted both through `mt8188_afe_fs_timing()` for sync frequency and `mtk_dai_pcm_mode()` for PCM mode.

State and persistence: Cached state includes `slave_mode`, `lrck_inv`, `bck_inv`, and PCM format. Hardware state persists in `PCM_INTF_CON1/2` and DAPM clock supply state for `aud_asrc11`, `aud_asrc12`, and `aud_pcmif`.

Dependencies and integration: Uses regmap, ASoC DAI ops, PCM params, `mt8188_afe_fs_timing()`, and register macros. Routes connect PCM1 playback from AFE outputs `O000/O001`, capture to `I002/I003`, and external endpoints `PCM1_INPUT`/`PCM1_OUTPUT`.

Risks: Slave-mode ASRC configuration is explicitly marked TODO, so slave mode may be incomplete despite format acceptance. `prepare` skips reconfiguration when either direction is active; a second stream with incompatible assumptions depends on symmetric constraints and machine-driver discipline. `bit_width` is taken from `dai->symmetric_sample_bits`, so format negotiation must set it as expected. Unsupported rates return `-EINVAL`; the rate table includes only 8/16/32/48 and 11.025/22.05/44.1 kHz.

Test signals: Playback and capture should be tested for I2S, DSP_A, and DSP_B formats, all inversion combinations, and master/slave clock-provider settings. Full-duplex tests should validate symmetric constraints and no midstream register churn. Slave-mode tests should specifically verify ASRC behavior because the code marks it incomplete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8188/mt8188-dai-pcm.c -->
