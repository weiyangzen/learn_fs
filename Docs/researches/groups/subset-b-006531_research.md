# Research Report: subset-b-006531

This grouped report covers the requested MediaTek MT8365 and Amlogic Meson ASoC source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-i2s.c

Purpose: Implements the MT8365 AFE I2S backend DAIs for the primary I2S interface and the second I2S interface. It configures I2S input/output registers, master clock parents/rates, 16/32-bit word length behavior, the 2-channel ASRC path used for slave capture, DAPM widgets/routes, and private per-DAI data registration.

Important APIs and functions: `mt8365_dai_i2s_register()` allocates a `mtk_base_afe_dai`, attaches I2S DAI drivers, widgets, and routes, then installs private copies of `mt8365_i2s_priv`. `mt8365_afe_set_i2s_out()` exposes ADDa-linked output configuration. `mt8365_afe_set_i2s_out_enable()` maintains a spinlock-protected reference count before toggling `AFE_I2S_CON1`. Runtime callbacks are `mt8365_dai_i2s_startup()`, `mt8365_dai_i2s_shutdown()`, `mt8365_dai_i2s_prepare()`, `mt8365_afe_2nd_i2s_hw_params()`, and `mt8365_afe_2nd_i2s_set_fmt()`. Internal helpers include `get_iir_coef()`, `mt8365_dai_set_config()`, `mt8365_afe_set_2nd_i2s_asrc()`, `mt8365_afe_set_2nd_i2s_asrc_enable()`, and `mt8365_dai_set_enable()`.

Control flow: Startup enables the AFE main clock and the direction-specific I2S module clock, except second-I2S slave capture where it enables the `MT8365_TOP_CG_I2S_IN` top clock gate instead. Prepare is one-shot per stream direction using `be->prepared[]`: it programs I2S format/rate/word length, optionally programs the ASRC for second-I2S slave capture, enables the correct APLL-associated path based on 44.1k-family versus 48k-family rates, reparents the I2S M-clock selector to AUD1 or AUD2, sets MCLK to rate times the interface multiplier, and enables the input or output register. Shutdown reverses enable state, disables the matching APLL-associated configuration, clears the prepared flag, disables clocks, and drops the main clock. ASRC setup maps input/output rates through `mt8365_afe_fs_timing()`, loads IIR coefficient SRAM when `get_iir_coef()` returns a table, programs input/output frequency palettes and calibration thresholds, and enables frequency tracking when requested.

State and persistence: `struct mtk_afe_i2s_priv` stores static hardware identity, register offsets, clock ids, clock multipliers, ADDa linkage, and mutable fields such as `i2s_out_on_ref_cnt`. Backend state lives in `mt8365_be_dai_data`, especially `fmt_mode` and `prepared[]`. Register writes through `regmap_update_bits()` persist in AFE hardware until disabled, reconfigured, or reset. The shared ADDa output enable is guarded by `afe_ctrl_lock` because multiple paths can refer to the same output register.

Dependencies and integration points: Depends on `mt8365-afe-common.h` for AFE ids, backend state, rate timing helpers, ASRC frequency helpers, and register bit definitions from `mt8365-reg.h`. It integrates with ALSA SoC DAI callbacks, DAPM routes connecting O00/O01/O03/O04 and 2ND I2S input, and MT8365 clock helpers in `mt8365-afe-clk.h`.

Risks: `get_iir_coef()` silently returns no coefficients for unsupported rate pairs, disabling IIR rather than rejecting the ASRC request. The ADDa output refcount is manually balanced and can underflow before being clamped if shutdown ordering is wrong. The second-I2S `set_fmt()` records only master mode `CBP_CFP`; other valid master-mask settings are accepted only by omission, so new formats need careful review. The code uses `config_val_in` in the output path, which may be intentional for this hardware but is a high-risk register-selection detail. Test coverage needs both master and slave capture paths because slave capture exercises ASRC and clock-gate logic that playback does not.

Test signals: Build with `SND_SOC_MT8365`; DAPM route inspection for `I2S Playback`, `2ND I2S Playback`, and `2ND I2S Capture`; playback/capture at 44.1k and 48k families; S16/S24/S32 formats; second-I2S slave capture with ASRC enabled; repeated prepare/shutdown cycles to check `prepared[]` and output refcount balancing; and regmap traces for `AFE_I2S_CON*`, `AFE_ASRC_2CH_CON*`, `AFE_ADDA_TOP_CON0`, and APLL clock configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-pcm.c

Purpose: Implements the MT8365 PCM1 backend DAI, including PCM interface format selection, master/slave mode, clock polarity, sample-rate encoding, bit-width/BCLK ratio programming, DAPM widgets/routes, and private state allocation.

Important APIs and functions: `mt8365_dai_pcm_register()` registers the PCM1 DAI driver plus `PCM1 Out`/`PCM1 In` widgets and routes. Runtime operations are `mt8365_dai_pcm1_startup()`, `mt8365_dai_pcm1_shutdown()`, `mt8365_dai_pcm1_prepare()`, and `mt8365_dai_pcm1_set_fmt()`. Hardware helpers are `mt8365_dai_configure_pcm1()`, `mt8365_dai_enable_pcm1()`, and `mt8365_dai_disable_pcm1()`. `struct mt8365_pcm_intf_data` stores the selected format, polarity, and slave-mode flags.

Control flow: `set_fmt` accepts only `SND_SOC_DAIFMT_I2S`, records normal/inverted BCLK and LRCLK polarity, and maps clock-provider mode to master or slave operation. Startup enables the AFE main clock only when the DAI was not already active. Prepare skips reconfiguration when another stream on the symmetric full-duplex DAI is already active; otherwise it builds `PCM_INTF_CON1_CONFIG_MASK` from master/slave flags, polarity bits, PCM/I2S format, sync length, one of 8/16/32/48 kHz rate encodings, 16-bit/32-BCLK or 24-bit/64-BCLK mode, and `PCM_INTF_CON1_EXT_MODEM`, then enables PCM1. Shutdown disables PCM1 and the main clock once no stream remains active.

State and persistence: The mutable interface mode is held in `afe_priv->dai_priv[MT8365_AFE_IO_PCM1]`. ALSA DAI symmetry flags enforce symmetric rate and sample bits, and runtime active counts prevent conflicting reconfiguration across playback/capture. Register state persists in `PCM_INTF_CON1` until disabled or overwritten.

Dependencies and integration points: Depends on MT8365 AFE clock helpers, `mt8365-reg.h` PCM bit definitions, ALSA SoC DAI callbacks, and DAPM routing between O07/O08 and I09/I22. The PCM1 DAI is a backend consumed by the MT8365 machine driver or device-tree-described links.

Risks: Supported rates are exactly 8, 16, 32, and 48 kHz despite the broader ASoC framework allowing many PCM rates elsewhere. Slave mode has a TODO for ASRC setup, so capture/playback synchronized to an external clock may be incomplete. `dai->symmetric_sample_bits` is used as the configured bit width; this relies on core DPCM negotiation having set it as expected. Only I2S formatting is accepted even though the register field has multiple PCM format values.

Test signals: PCM1 playback and capture at all four supported rates, S16 and S32 formats, master and slave clock-provider settings, all four inversion modes, simultaneous playback/capture to confirm prepare skip behavior, and register traces on `PCM_INTF_CON1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-dai-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-mt6357.c -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-mt6357.c

Purpose: Defines the MT8365 EVK machine driver for an MT6357 codec-based sound card. It describes FE and BE DAI links, DAPM routing, pinctrl state management for the internal ADDA link, and platform-driver binding through the common MediaTek sound-card probe path.

Important APIs and functions: The platform driver probes through `mtk_soundcard_common_probe()` using `mt8365_mt6357_card`. `mt8365_mt6357_dev_probe()` parses DAI link information, allocates machine private data, stores it in the common card data, and initializes GPIO/pinctrl state. `mt8365_mt6357_gpio_probe()` obtains pinctrl states named `default`, `dmic`, `miso_off`, `miso_on`, `mosi_off`, and `mosi_on`. `mt8365_mt6357_int_adda_startup()` and `mt8365_mt6357_int_adda_shutdown()` switch MOSI/MISO pin states around playback and capture. Static structures define DAI links for DL1, DL2, AWB, VUL, 2ND I2S, DMIC, and INT ADDA.

Control flow: Device-tree match data selects the `mt8365-mt6357` card descriptor. Probe runs the common card flow, then `parse_dai_link_info()` fills common card references. GPIO probe fetches every named pinctrl state; if a state exists, it is selected once during probe. At runtime the internal ADDA backend ops select `mosi_on` for playback startup and `miso_on` for capture startup, then select the corresponding off state at shutdown. Frontend links are dynamic DPCM links with post triggers and merged rates, while backend links are no-PCM codec/CPU connections.

State and persistence: `struct mt8365_mt6357_priv` stores the `pinctrl` handle and optional pinctrl states. The static `snd_soc_card` and DAI link array define persistent card topology. Pinctrl selections persist in the pin controller until another state is selected. The common `mtk_soc_card_data` carries machine private state and card data across common probe code.

Dependencies and integration points: Integrates with MT8365 AFE DAI names (`DL1`, `DL2`, `AWB`, `VUL`, `2ND I2S`, `DMIC`, `INT ADDA`), the codec component `mt6357-sound` and DAI `mt6357-snd-codec-aif1`, common MediaTek card helpers in `mtk-soc-card.h` and `mtk-soundcard-driver.h`, pinctrl, device tree compatible `mediatek,mt8365-mt6357`, and ALSA DPCM.

Risks: `mt8365_mt6357_gpio_probe()` errors are ignored by `mt8365_mt6357_dev_probe()`, so missing or broken pinctrl may not fail card registration. Probe selects all available states sequentially, leaving the final available state active, which depends on DTS state availability. Optional pin states are tolerated, but missing on/off states reduce electrical isolation. Static FE/BE names must match the AFE component DAI names exactly.

Test signals: Device-tree probe for `mediatek,mt8365-mt6357`, `aplay -l`/`arecord -l` card enumeration, DAPM graph for HDMI and DMIC routes, playback/capture over INT ADDA with pinctrl debugfs state changes, 2ND I2S HDMI route playback, and suspend/resume using `snd_soc_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-mt6357.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-reg.h

Purpose: Provides the MT8365 AFE register map and bit-field definitions used by the MT8365 ASoC platform drivers. It is the hardware ABI for top clock gates, memifs, interconnect matrices, I2S/PCM/DMIC/TDM/SPDIF/ASRC blocks, IRQ counters, ADDA controls, secure masks, and gain/control-monitor blocks.

Important APIs and definitions: The header defines register offsets from `AUDIO_TOP_CON0` through `AFE_SECURE_MASK_CONN27`, with `MAX_REGISTER` set to the final secure mask register. Important bit groups include `AUD_TCON*_PDN_*` power-down controls, `AFE_I2S_CON*` format/rate/enable fields, `AFE_ASRC_2CH_CON*` coefficient SRAM and calibration controls, `AFE_ADDA_*` sample-rate and ADDA enable fields, `PCM_INTF_CON1_*` PCM mode fields, `DMIC_TOP_CON_*` capture filter and channel fields, `AFE_CONN_24BIT_*` output width controls, `AFE_GAIN1_*`, and CM1/CM2 channel-mixer fields.

Control flow: This header has no executable flow, but it drives every `regmap_update_bits()`, `FIELD_PREP()`, and register-write sequence in the MT8365 AFE implementation. Its masks determine which hardware bits are preserved or overwritten during DAI prepare/shutdown, memif setup, DMIC setup, ASRC programming, and clock-gate management.

State and persistence: All definitions represent hardware registers whose values persist in the AFE block until modified, powered down, or reset. The header also models 64-bit DMA address support with base/end/current MSB registers for multiple memifs. `MAX_REGISTER` bounds regmap access.

Dependencies and integration points: Includes `linux/bitfield.h` and is consumed by MT8365 AFE common code, DAI drivers, memory-interface code, clock code, and machine integration. It aligns with register offsets documented for the MT8365 audio block and must match device-tree reg ranges and regmap stride.

Risks: Incorrect offsets or masks cause silent hardware misprogramming. Several macros encode zero-valued modes such as `PCM_INTF_CON1_MASTER_MODE` or `AFE_I2S_CON1_TDMOUT_TO_PAD`; they are meaningful only when paired with masks. Wide masks such as `PCM_INTF_CON1_CONFIG_MASK` and `DMIC_TOP_CON_CONFIG_MASK` require careful review when new bits are added. `MAX_REGISTER` must remain synchronized with the largest valid offset.

Test signals: Compile coverage for all MT8365 sound drivers, regmap debugfs register dumps, successful I2S/PCM/DMIC/ADDA playback and capture, IRQ counter behavior, 24-bit route setup through `AFE_CONN_24BIT`, and ASRC coefficient writes to `AFE_ASRC_2CH_CON12/13`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8365/mt8365-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/meson/Kconfig

Purpose: Declares the Amlogic Meson ASoC Kconfig menu and the symbols controlling AIU, AXG FIFO, TDM, SPDIF, PDM, card utilities, codec glue, GX/AXG sound cards, G12A routing controls, and the T9015 DAC.

Important entries: `SND_MESON_AIU` enables the older Meson8/GX Audio Input Unit and selects codec glue plus IEC958 support. `SND_MESON_AXG_FIFO` is a hidden common symbol selected by `SND_MESON_AXG_FRDDR` and `SND_MESON_AXG_TODDR`. `SND_MESON_AXG_TDM_FORMATTER` and `SND_MESON_AXG_TDM_INTERFACE` are hidden common TDM layers selected by `SND_MESON_AXG_TDMIN` and `SND_MESON_AXG_TDMOUT`. `SND_MESON_AXG_SOUND_CARD` and `SND_MESON_GX_SOUND_CARD` select or imply the needed frontend/backend drivers. `SND_MESON_AXG_SPDIFOUT`, `SND_MESON_AXG_SPDIFIN`, `SND_MESON_AXG_PDM`, `SND_MESON_G12A_TOACODEC`, `SND_MESON_G12A_TOHDMITX`, and `SND_SOC_MESON_T9015` expose individual endpoint/control choices.

Control flow: Kconfig evaluation is gated by `ARCH_MESON` or `COMPILE_TEST && COMMON_CLK`. Selected symbols pull in required helper modules, while `imply` suggests platform companions without forcing them.

State and persistence: User selections persist in the kernel `.config` and decide which objects from the Meson Makefile build into the kernel or modules.

Dependencies and integration points: Integrates with the parent ALSA SoC Kconfig tree, Common Clock framework, REGMAP MMIO, reset drivers, HDMI codec support, DRM Meson HDMI availability, and dynamic minor support.

Risks: Hidden common symbols rely on all public drivers selecting the right helper. `imply` does not guarantee dependencies are present, so runtime card topologies can still miss optional codecs or routing controls. Menu dependency on `COMMON_CLK` for compile testing is important because most drivers depend heavily on clock APIs.

Test signals: `allyesconfig`/`allmodconfig` compile coverage, menu visibility on Meson and COMPILE_TEST builds, module dependency checks, and build tests for minimal selections such as only SPDIFIN, only PDM, or only AIU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/meson/Makefile

Purpose: Maps Meson ASoC Kconfig symbols to composite module objects and single-driver objects. It defines which source files are linked into AIU, AXG FIFO/TDM/card/SPDIF/PDM, codec glue, G12A routing, and T9015 modules.

Important definitions: `snd-soc-meson-aiu-y` combines `aiu.o`, AIU codec control, encoders, and FIFO variants into one module. `snd-soc-meson-axg-fifo-y` provides the shared AXG FIFO helper, with FRDDR/TODDR as separate modules. TDM is split into formatter, interface, tdmin, and tdmout modules. Card utilities, codec glue, GX/AXG sound cards, G12A controls, and T9015 each have their own object lists. `obj-$(CONFIG_...)` lines bind the composite modules to Kconfig symbols.

Control flow: Kbuild uses the `*-y` object lists when the corresponding `obj-*` entry is enabled. Hidden helper symbols build common modules only when selected by public drivers.

State and persistence: No runtime state. Build output and module composition are determined by `.config`.

Dependencies and integration points: Mirrors symbol names from `Kconfig` and source-file boundaries in `sound/soc/meson`. Correct module composition is required for exported helper symbols such as AXG FIFO and TDM formatter routines.

Risks: Missing an object from a composite module causes unresolved symbols or absent DAI ops. Enabling helper modules independently without consumers can still produce modules with only exported helpers. New source files must be added both here and in Kconfig dependency chains.

Test signals: Incremental module builds for each symbol, link checks for `snd-soc-meson-aiu.ko`, `snd-soc-meson-axg-frddr.ko`, `snd-soc-meson-axg-tdmin.ko`, and allmodconfig link validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-acodec-ctrl.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-acodec-ctrl.c

Purpose: Implements the AIU internal analog codec control component for GXL-class SoCs. It routes AIU I2S or PCM data into the internal DAC path, constrains the DAC-facing output to two channels, and exposes DAPM controls plus a lane-select mixer control.

Important APIs and functions: `aiu_acodec_ctrl_register_component()` registers the component and three DAIs: `ACODEC I2S IN`, `ACODEC PCM IN`, and `ACODEC OUT`. `aiu_acodec_ctrl_mux_put_enum()` safely switches the source mux by disconnecting DAPM before rewriting LRCLK/BCLK source fields. `aiu_acodec_ctrl_input_hw_params()` wraps `meson_codec_glue_input_hw_params()` and limits advertised channel min/max to `AIU_ACODEC_OUT_CHMAX`. Component probe `aiu_acodec_ctrl_component_probe()` programs DIN skew.

Control flow: Input DAIs use codec-glue probe/remove/hw_params/set_fmt callbacks to capture format data. The DAPM mux selects disabled/I2S/PCM, updates both data LRCLK and BCLK/MCLK source fields, then reconnects the selected route. The output DAI uses codec-glue output startup to enforce the parameters captured from the selected input.

State and persistence: Codec-glue input data persists per DAI and is mutated during hw_params. AIU control register bits persist in `AIU_ACODEC_CTRL`, including source selection, DIN enable, DIN skew, and lane source.

Dependencies and integration points: Depends on AIU register definitions, dt-bindings component IDs, `meson-codec-glue`, ALSA DAPM, and AIU platform probe, which calls this registration only when `has_acodec` is true.

Risks: The DIN skew write is documented as required to avoid output saturation but not fully understood. Source switching must remain DAPM-disconnected while register fields change to avoid glitches. Channel narrowing to two channels assumes only one of four glue lanes reaches the DAC.

Test signals: GXL internal DAC playback through I2S and PCM sources, DAPM route changes for `ACODEC SRC`, lane-select control changes, 1/2-channel negotiation, and regmap checks of `AIU_ACODEC_CTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-acodec-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-codec-ctrl.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-codec-ctrl.c

Purpose: Implements the AIU HDMI codec control component. It routes AIU PCM or I2S streams into the HDMI codec-facing output and provides DAPM source selection over `AIU_HDMI_CLK_DATA_CTRL`.

Important APIs and functions: `aiu_hdmi_ctrl_register_component()` registers the HDMI control component and its `HDMI I2S IN`, `HDMI PCM IN`, and `HDMI OUT` DAIs. `aiu_codec_ctrl_mux_put_enum()` switches clock and data source fields while temporarily disconnecting the DAPM mux. Input DAIs use `meson_codec_glue_input_*` ops; the output DAI uses `meson_codec_glue_output_startup()`.

Control flow: DAPM source changes first force the mux to disabled, clear clock/data selection fields, then set both fields to the requested PCM or I2S source and restore DAPM power. Codec-glue input `hw_params` records stream parameters for the output side to consume during startup.

State and persistence: Source state persists in `AIU_HDMI_CLK_DATA_CTRL`. Codec-glue per-input state records format, rate, channel, and lane parameters while a route is active.

Dependencies and integration points: Registered by the AIU core for HDMI-capable topologies. Integrates with `meson-codec-glue`, HDMI codec components, device-tree DAI phandle translation through `aiu_of_xlate_dai_name()`, and DAPM routes from AIU encoders or FIFOs to HDMI.

Risks: The reset-then-set sequence is important because switching clock/data source independently could expose mismatched clocks to the HDMI codec. DAI name and component-id phandle translations must match dt-bindings. The component supports up to eight channels, so downstream HDMI codec limits must be negotiated correctly by DPCM.

Test signals: HDMI audio playback using I2S and PCM sources, DAPM mux changes under active/inactive routes, `aplay` multichannel negotiation, and regmap traces for `AIU_HDMI_CLK_DATA_CTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-codec-ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-i2s.c

Purpose: Implements the AIU I2S encoder DAI ops, configuring source descriptors, bit/sample clocks, LRCLK/BCLK polarity, channel constraints, sysclk rate, and clock enable sequencing for I2S output.

Important APIs and functions: Exported `aiu_encoder_i2s_dai_ops` supplies `startup`, `shutdown`, `hw_params`, `hw_free`, `set_fmt`, and `set_sysclk`. Key helpers are `aiu_encoder_i2s_setup_desc()`, `aiu_encoder_i2s_set_clocks()`, `aiu_encoder_i2s_set_legacy_div()`, `aiu_encoder_i2s_set_more_div()`, and `aiu_encoder_i2s_divider_enable()`.

Control flow: Startup constrains channels to either 2 or 8 and enables the I2S clock bulk. `set_fmt` accepts CPU bit/frame master mode only, handles I2S versus left-justified skew, and programs LRCLK/AOCLK inversion. `hw_params` disables the divider, resets the I2S fast pipeline, validates physical width and channel count, writes the descriptor mode, derives the MCLK/sample-rate oversampling ratio, programs a 64 BCLK/LRCLK ratio and divider, selects HDMI AMCLK, then reenables the divider. `hw_free` disables the divider.

State and persistence: The master clock rate is stored in the clock framework and used to derive dividers. AIU descriptor and clock-control register bits persist until reconfigured. No private heap state is allocated here.

Dependencies and integration points: Depends on the `struct aiu` clock arrays populated by `aiu.c`, platform data `has_clk_ctrl_more_i2s_div`, ALSA hw_params, and AIU CPU DAI registration. It feeds the I2S encoder playback DAPM route and can be routed onward to HDMI/internal codec controls.

Risks: The hardware has a special 16-bit/8-channel divider adjustment in the newer divider path; wrong handling causes incorrect BCLK. Legacy dividers support only powers 1,2,4,8. The code assumes the MCLK rate is already set by `set_sysclk()` and divisible into the requested sample rate by a multiple of 64. Only 16-bit and 32-bit physical widths are accepted.

Test signals: 2-channel and 8-channel playback, S16 and S24/S32 containers, I2S and left-justified formats with inversion variants, legacy Meson8 and newer GX/GXL divider behavior, sysclk changes from card drivers, and regmap traces on `AIU_I2S_SOURCE_DESC`, `AIU_CLK_CTRL`, and `AIU_CLK_CTRL_MORE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-spdif.c

Purpose: Implements the AIU SPDIF encoder DAI ops, including hold/unhold trigger control, IEC958 consumer channel-status programming, sample-width mode selection, SPDIF master-clock setup, and clock enable sequencing.

Important APIs and functions: Exported `aiu_encoder_spdif_dai_ops` supplies `startup`, `shutdown`, `trigger`, `hw_params`, and `hw_free`. Helpers include `aiu_encoder_spdif_divider_enable()`, `aiu_encoder_spdif_hold()`, and `aiu_encoder_spdif_setup_cs_word()`.

Control flow: Startup reparents the SPDIF MCLK selector to the dedicated `spdif_mclk`, then enables the SPDIF clock bulk. `hw_params` disables the divider, validates 16-bit or 32-bit physical widths, programs `AIU_958_MISC`, writes left/right IEC958 channel-status halfwords, sets the internal divider, sets MCLK to `rate * 128 * internal_div`, and enables the divider. Runtime trigger releases or asserts hold depending on start/stop/pause state. `hw_free` disables the divider and shutdown disables clocks.

State and persistence: Channel-status words persist in `AIU_958_CHSTAT_L/R*`; hold state persists in `AIU_958_CTRL`; format and clock divider state persist in `AIU_958_MISC` and `AIU_CLK_CTRL`.

Dependencies and integration points: Depends on ALSA IEC958 helper `snd_pcm_create_iec958_consumer_hw_params()`, AIU clock data, and AIU CPU DAI registration. It is connected through DAPM to the SPDIF FIFO or I2S FIFO via the AIU CPU SPDIF source mux.

Risks: Only PCM/uncompressed mode is configured; non-PCM bits are cleared. Incorrect MCLK parent selection or divider setup breaks SPDIF framing. Width validation excludes unusual containers. Trigger hold behavior must align with FIFO start/stop to avoid underrun noise.

Test signals: SPDIF playback at 32/44.1/48/88.2/96/176.4/192 kHz, S16 and S24/S32 containers, IEC958 status control inspection on receiver, pause/resume behavior, and clock/regmap tracing for `AIU_958_*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-encoder-spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-i2s.c

Purpose: Specializes the shared AIU FIFO implementation for I2S playback. It defines I2S FIFO PCM hardware limits, reset/prepare behavior, physical-width programming, IRQ periodicity, and DAI probe data binding.

Important APIs and functions: Exported `aiu_fifo_i2s_dai_ops` composes shared FIFO ops with I2S-specific `trigger`, `prepare`, `hw_params`, and probe. `aiu_fifo_i2s_dai_probe()` allocates common FIFO state and sets the I2S memory offset, block size, pclk, IRQ, and hardware constraints. Helpers are `aiu_fifo_i2s_trigger()`, `aiu_fifo_i2s_prepare()`, and `aiu_fifo_i2s_hw_params()`.

Control flow: Probe binds the FIFO to `AIU_MEM_I2S_START`, a 256-byte FIFO block, I2S pclk, and the I2S IRQ. Prepare runs the common FIFO reset then toggles `AIU_MEM_I2S_BUF_CNTL_INIT`. `hw_params` puts the I2S block in hold, configures DMA boundaries through common FIFO code, selects 16-bit or 32-bit memory mode, sets IRQ block count from period bytes divided by FIFO block size, forces left/right mode, and releases hold. Trigger resets the fast I2S path before delegating to the common FIFO enable/disable path.

State and persistence: The `struct aiu_fifo` attached to playback DMA data stores block size, IRQ, pclk, and register offset. Hardware state persists in I2S memory and misc registers until reconfigured.

Dependencies and integration points: Uses common `aiu_fifo.c`, AIU register offsets from `aiu.h`, AIU clock/IRQ fields from `struct aiu`, and ALSA PCM buffer management via `pcm_new`.

Risks: Period and buffer byte sizes must be multiples of 256 through the common constraints or IRQ block programming is invalid. Only physical widths 16 and 32 are accepted. Hold/release and fast reset sequencing is hardware-sensitive.

Test signals: I2S FIFO playback with mmap, pause/resume, period elapsed IRQ cadence, S16/S24/S32 containers, 2- and 8-channel streams, and register traces on `AIU_MEM_I2S_*` and `AIU_I2S_MISC`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-spdif.c

Purpose: Specializes the shared AIU FIFO implementation for SPDIF playback, configuring IEC958 FIFO/DCU behavior, period-byte IRQ generation, memory mode, and DAI probe state.

Important APIs and functions: Exported `aiu_fifo_spdif_dai_ops` composes common FIFO callbacks with SPDIF-specific `trigger`, `prepare`, `hw_params`, and probe. `aiu_fifo_spdif_dai_probe()` binds FIFO state to `AIU_MEM_IEC958_START`, SPDIF pclk, SPDIF IRQ, and SPDIF hardware limits. Helpers are `fifo_spdif_dcu_enable()`, `fifo_spdif_trigger()`, `fifo_spdif_prepare()`, and `fifo_spdif_hw_params()`.

Control flow: Prepare resets the common FIFO and toggles `AIU_MEM_IEC958_BUF_CNTL_INIT`. `hw_params` programs common DMA boundaries, configures DDR-read linear mode with optional 16-bit mode, writes bytes-per-frame/period interrupt count to `AIU_IEC958_BPF`, and disables compressed-sync default behavior for PCM mode. Trigger first enables/disables the common FIFO, then enables or disables the IEC958 DCU block.

State and persistence: Playback FIFO private data records the SPDIF memory offset and IRQ. Hardware state persists in `AIU_MEM_IEC958_CONTROL`, `AIU_IEC958_BPF`, and `AIU_IEC958_DCU_FF_CTRL`.

Dependencies and integration points: Uses the common AIU FIFO module, AIU SPDIF clock/IRQ data, and routes into the AIU SPDIF encoder DAI.

Risks: The probe defines `AIU_FIFO_SPDIF_BLOCK` as the PCM period minimum but sets `fifo_block` to 1 for common DMA boundary math; changing either without understanding the hardware can alter period constraints. Compressed IEC958 defaults are explicitly disabled for PCM, so non-PCM support would need new logic. Only 16- and 32-bit physical widths are supported.

Test signals: SPDIF PCM playback, pause/resume/stop trigger sequencing, IRQ cadence matching period bytes, S16 and S24/S32 containers, and regmap tracing of `AIU_MEM_IEC958_*` and `AIU_IEC958_DCU_FF_CTRL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo-spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.c

Purpose: Provides shared playback FIFO PCM operations for AIU I2S and SPDIF frontends. It handles DMA pointer reporting, FIFO enable/disable triggers, DMA boundary programming, IRQ registration, clock management, managed buffer allocation, and DAI private data allocation.

Important APIs and functions: `aiu_fifo_pointer()`, `aiu_fifo_trigger()`, `aiu_fifo_prepare()`, `aiu_fifo_hw_params()`, `aiu_fifo_startup()`, `aiu_fifo_shutdown()`, `aiu_fifo_pcm_new()`, `aiu_fifo_dai_probe()`, and `aiu_fifo_dai_remove()` are exported within the AIU module. `struct aiu_fifo` stores PCM limits, memory offset, FIFO block size, pclk, and IRQ.

Control flow: Startup applies PCM hardware constraints, enforces buffer and period byte step sizes based on `fifo_block`, enables pclk, and requests the FIFO IRQ. `hw_params` writes DMA start/read/end addresses, programs memory channel masks to read all channels, and sets FIFO memory boundaries. Prepare toggles the common FIFO init bit. Trigger toggles fill/empty enables. ISR calls `snd_pcm_period_elapsed()`. Shutdown frees the IRQ and disables pclk. `pcm_new` coerces a 32-bit DMA mask and installs a managed buffer sized to the FIFO hardware maximum.

State and persistence: Per-DAI FIFO state is allocated with `kzalloc_obj()` and attached as playback DMA data. Hardware DMA address registers persist until new hw_params or reset. IRQ registration is per open substream.

Dependencies and integration points: Called by `aiu-fifo-i2s.c` and `aiu-fifo-spdif.c`. Depends on ASoC component read/write APIs, Linux DMA mapping, clock APIs, and ALSA PCM runtime structures.

Risks: Pointer calculation casts runtime DMA address and hardware read pointer to 32-bit, matching the coerced DMA mask but unsuitable for wider addressing. Error cleanup depends on variant startup using common shutdown semantics. Period elapsed is raised on every IRQ without reading status in this common handler, so variant hardware must generate only intended period IRQs.

Test signals: PCM open/close leak checks, IRQ registration failures, 32-bit DMA mask setup, mmap playback pointer progression, period/buffer constraint tests, and underrun/stop/pause trigger behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.h

Purpose: Declares the shared AIU FIFO state structure and operation prototypes used by the I2S and SPDIF FIFO variants.

Important APIs and types: `struct aiu_fifo` carries the PCM hardware description, register memory offset, FIFO burst/block size, pclk, and IRQ. Prototypes cover DAI probe/remove, pointer, trigger, prepare, hw_params, startup, shutdown, and `pcm_new`.

Control flow: No executable logic. The header defines the call contract for variant files to compose their `snd_soc_dai_ops` from common FIFO helpers.

State and persistence: Declares the shape of per-DAI playback DMA data allocated by `aiu_fifo_dai_probe()`.

Dependencies and integration points: Included by `aiu.c`, `aiu-fifo.c`, `aiu-fifo-i2s.c`, and `aiu-fifo-spdif.c`. Forward declarations avoid pulling in full ALSA headers in every include site.

Risks: The common helper contract is playback-only; using it for capture would require new DMA-data accessors and pointer semantics. Any change to `struct aiu_fifo` must be reflected in both variant probes.

Test signals: Build coverage for AIU FIFO variants and module link checks for all declared helper functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu-fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu.c

Purpose: Implements the AIU platform driver and CPU component for Meson8/GX audio output. It registers AIU FIFO and encoder DAIs, exposes the SPDIF source DAPM mux, initializes regmap/clock/IRQ resources, and registers HDMI/internal-codec control components.

Important APIs and functions: `aiu_probe()` is the platform probe. `aiu_of_xlate_dai_name()` converts two-cell DAI phandles into DAI names. `aiu_cpu_component_probe()` and remove keep the I2S pclk enabled for SPDIF source control. `aiu_clk_get()` and `aiu_clk_bulk_get()` fetch global, I2S, and SPDIF clocks. Static `aiu_cpu_dai_drv[]` defines I2S FIFO, SPDIF FIFO, I2S Encoder, and SPDIF Encoder DAIs.

Control flow: Probe allocates `struct aiu`, reads SoC match data, resets the device, maps registers, creates a 32-bit regmap, obtains I2S/SPDIF IRQs, fetches clocks, registers the CPU component/DAIs, registers HDMI control, and conditionally registers internal DAC control when the platform has an acodec. Error paths unregister already-registered components. Remove unregisters all components attached to the device.

State and persistence: `struct aiu` stores the SPDIF master clock, per-interface clock arrays, IRQs, and platform flags. Regmap-backed AIU register state persists in hardware. Component registration creates ASoC DAI and DAPM graph state.

Dependencies and integration points: Depends on dt-bindings `meson-aiu.h`, regmap MMIO, reset, clock, platform IRQ resources named `i2s` and `spdif`, FIFO/encoder ops from sibling files, and codec-control registrations. Compatible strings distinguish GXBB, GXL, Meson8, and Meson8b platform quirks.

Risks: All AIU subcomponents share one physical regmap, so component order and clock availability matter. HDMI control registration is mandatory after CPU registration; internal DAC registration is conditional. DAI phandle translation requires exactly two args and matching component id. Component probe keeps I2S pclk enabled for a control that touches I2S misc registers, which affects power behavior.

Test signals: Device probe on all compatible strings, reset and regmap initialization, DAI phandle parsing from DT, DAPM route visibility for FIFO-to-encoder paths, HDMI and acodec component registration, and playback through I2S/SPDIF on GXBB/GXL/Meson8 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/aiu.h

Purpose: Defines shared AIU types, clock ids, platform flags, DAI operation externs, format masks, registration prototypes, DAI phandle helper prototype, and AIU register offsets.

Important APIs and types: `enum aiu_clk_ids` indexes pclk/aoclk/mclk/mixer clocks. `struct aiu_interface` groups clock bulk data and IRQ per I2S or SPDIF side. `struct aiu_platform_data` records SoC quirks such as internal acodec and newer I2S divider support. `struct aiu` is the root runtime state. The header declares `aiu_of_xlate_dai_name()`, control component registration functions, FIFO probe helpers, and extern DAI ops for FIFO and encoder variants.

Control flow: No executable logic. Constants define how sibling files address AIU registers such as `AIU_I2S_MISC`, `AIU_CLK_CTRL`, `AIU_MEM_I2S_*`, and `AIU_MEM_IEC958_*`.

State and persistence: Declares root and interface state stored by the platform driver. Register offsets correspond to persistent hardware state.

Dependencies and integration points: Included across AIU CPU, FIFO, encoder, and codec-control files. It is the internal ABI for the composite `snd-soc-meson-aiu` module.

Risks: Register offsets and clock index ordering must match device-tree clock lists and hardware manuals. `AIU_FORMATS` constrains all AIU CPU DAIs; adding formats requires validating every FIFO and encoder path.

Test signals: Build/link coverage of the composite AIU module, clock-name matching in DT, and runtime register access in all AIU subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/aiu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-card.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-card.c

Purpose: Implements the AXG sound-card machine driver glue that builds FE/BE DAI links from device tree, handles TDM slot parsing, configures codec and CPU TDM masks, adds loopback links, and delegates common card parsing to Meson card utilities.

Important APIs and functions: The platform driver probes with `meson_card_probe()` using `axg_card_match_data`. `axg_card_add_link()` classifies each CPU node as playback FE, capture FE, TDM interface, codec-control, or generic backend. `axg_card_parse_tdm()` allocates per-link TDM data, parses format/mclk/slot masks, sets link ops/init, and adds loopback when playback exists. `axg_card_tdm_dai_init()` programs codec DAI slots and calls `axg_tdm_set_tdm_slots()` for the CPU DAI. `axg_card_tdm_be_hw_params()` sets sysclk from `mclk-fs`.

Control flow: Common Meson card parsing calls `add_link` for each DT link. FRDDR/TODDR nodes become dynamic FE links. Codec-control backends get codec-to-codec params. TDM interface backends parse per-lane CPU masks (`dai-tdm-slot-tx-mask-N`/`rx-mask-N`), codec child masks, slot count/width, and optional `mclk-fs`; if playback slots exist, a synthetic capture-only `TDM Loopback` backend link is inserted immediately after the pad link.

State and persistence: `struct axg_dai_link_tdm_data` persists in `priv->link_data[rtd->id]`, holding mclk ratio, slot count/width, lane masks, and per-codec masks. DAI link arrays may be reallocated when loopback links are inserted. Slot settings persist in CPU and codec DAIs.

Dependencies and integration points: Depends on `meson-card` utilities, `axg-tdm.h` interface APIs, device-tree compatible prefixes, ASoC DPCM, and codec drivers supporting `snd_soc_dai_set_tdm_slot()`.

Risks: Slot-mask parsing uses max mask value to infer direction and slot count, so malformed masks can disable playback/capture or produce bad slot totals. Link insertion must keep `link_data` aligned with reallocated DAI links and balance OF node references. Codec mask order follows child-node order and must match codec DAI order. TDM slot count is capped at 32.

Test signals: AXG card probe with FRDDR/TODDR/TDM/SPDIF/PDM links, DT validation for TDM masks, loopback DAI visibility, multicodec TDM links, DPCM hw_params setting mclk, and error tests for no CPU slots or undersized slot counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.c

Purpose: Provides the shared PCM/component implementation for AXG/G12A playback and capture FIFOs. It manages DMA address registers, FIFO thresholds, interrupts, memory-arbiter reset, pclk, pointer reporting, trigger enable, managed buffers, and platform resource probing.

Important APIs and functions: Exported helpers include `axg_fifo_pcm_open()`, `axg_fifo_pcm_close()`, `axg_fifo_pcm_hw_params()`, `g12a_fifo_pcm_hw_params()`, `axg_fifo_pcm_hw_free()`, `axg_fifo_pcm_pointer()`, `axg_fifo_pcm_trigger()`, `axg_fifo_pcm_new()`, and `axg_fifo_probe()`. Internal helpers include `__dma_enable()`, `axg_fifo_ack_irq()`, and `axg_fifo_pcm_irq_block()`.

Control flow: Open applies broad PCM hardware limits, enforces burst alignment, requests a threaded IRQ, enables pclk, selects DDR-read status reporting, disables DMA and IRQs, clears pending interrupts, and deasserts the memory arbiter reset. `hw_params` programs start/finish addresses, interrupt period count, threshold as half of the smaller of period and FIFO depth, and repeat-count IRQ enable unless no-period-wakeup is requested. Trigger toggles DMA enable. IRQ handler acknowledges status and calls `snd_pcm_period_elapsed()` on repeat-count interrupts. Close asserts the arbiter reset, disables pclk, and frees IRQ. Probe maps registers, gets pclk/reset/irq, allocates the threshold regmap field, reads FIFO depth with a 256-byte fallback, and registers the SoC component/DAI from match data.

State and persistence: `struct axg_fifo` stores regmap, pclk, reset, threshold field, depth, and IRQ per platform device. PCM runtime DMA addresses persist in FIFO registers while a stream is configured. IRQ enable and DMA enable bits persist until hw_free/trigger/open reset.

Dependencies and integration points: Used by FRDDR and TODDR drivers through match data and component callbacks. Depends on regmap MMIO, OF IRQ, reset controller, clock controller, ALSA PCM, and ASoC component APIs.

Risks: Pointer reporting subtracts a 32-bit-cast DMA address from the status register; managed buffers should remain addressable by the hardware. Missing `amlogic,fifo-depth` falls back to the smallest known depth, which is safe but may reduce performance. IRQ status other than repeat-count is logged but not otherwise handled. The threshold calculation assumes period and depth are byte counts aligned to the burst size.

Test signals: FRDDR/TODDR playback/capture open-close, period wakeups and no-period-wakeup mode, underrun/stop/pause triggers, FIFO depth property present/missing, reset controller behavior, and regmap traces for FIFO start/finish/int/status registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.h

Purpose: Defines shared AXG FIFO constants, register offsets, interrupt bits, the FIFO runtime structure, match-data contract, and exported PCM/probe helper prototypes.

Important APIs and types: `AXG_FIFO_CH_MAX`, `AXG_FIFO_FORMATS`, and `AXG_FIFO_BURST` define generic FIFO PCM capabilities. Register constants cover `FIFO_CTRL0/1/2`, DMA address registers, status registers, and threshold/selector fields. `struct axg_fifo` stores per-device resources. `struct axg_fifo_match_data` lets FRDDR/TODDR drivers provide component driver, DAI driver, and threshold field layout.

Control flow: No executable logic. The header is the internal ABI between `axg-fifo.c` and frontend-specific FIFO drivers.

State and persistence: Declares resource state for one FIFO hardware block and register definitions for persistent FIFO hardware state.

Dependencies and integration points: Included by `axg-fifo.c`, `axg-frddr.c`, and TODDR companion code. Exports are used across separate modules, so prototypes must match symbol exports.

Risks: Changing format masks or channel maxima affects all AXG FIFO frontends. Register-field definitions are reused for multiple SoC variants and must match match-data field positions.

Test signals: Build/link coverage for FRDDR/TODDR modules, compile-time format support in DAI drivers, and runtime FIFO probe using match data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-fifo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-frddr.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-frddr.c

Purpose: Implements the AXG/G12A/SM1 FRDDR playback FIFO frontend DAI. It layers playback-specific DAI ops, FIFO depth tuning, G12A pointer reset, DAPM output routing, and SoC-variant source-selection controls over the shared AXG FIFO component.

Important APIs and functions: The platform driver uses shared `axg_fifo_probe()` with match data for `amlogic,axg-frddr`, `amlogic,g12a-frddr`, and `amlogic,sm1-frddr`. DAI ops include `axg_frddr_dai_startup()`, `axg_frddr_dai_shutdown()`, `axg_frddr_dai_hw_params()`, `g12a_frddr_dai_prepare()`, and `axg_frddr_pcm_new()`.

Control flow: Startup enables pclk and forces single-buffer mode. DAI hw_params trims FIFO depth to the smaller of period bytes and hardware depth, then writes the depth field. G12A prepare toggles `CTRL1_FRDDR_FORCE_FINISH` so the read pointer resets to `FIFO_INIT_ADDR`. Component callbacks from shared FIFO code perform open/close/hw_params/pointer/trigger. AXG exposes one demux from playback to OUT0-OUT7; G12A/SM1 expose three independently enabled source paths, with SM1 selection fields moved to `FIFO_CTRL2`.

State and persistence: Variant match data selects component widgets/routes and threshold field. Runtime FIFO state is held in `struct axg_fifo`. DAPM control settings persist in FIFO control registers and determine output routing.

Dependencies and integration points: Depends on `axg-fifo` exported helpers, ASoC DAPM, OF match data, regmap, and Meson card routing from FRDDR frontends to TDM/SPDIF/PDM backends.

Risks: Pclk is enabled both in DAI startup and shared PCM open paths for different purposes; imbalance would cause register-access failures or power leaks. G12A/SM1 route controls differ by register, so wrong match data misroutes audio. FIFO depth must not be programmed below one burst.

Test signals: Playback on AXG/G12A/SM1 compatibles, output route controls to OUT0-OUT7, multiple G12A/SM1 output source enables, low-latency small-period playback, pause/resume, and read-pointer reset after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-frddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-pdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-pdm.c

Purpose: Implements the AXG PDM capture DAI, including PDM clocking, channel enable/reset masks, HCIC/LPF/HPF filter programming, default FIR coefficient loading, sample-pointer timing, trigger enable, and platform probe.

Important APIs and functions: Runtime ops are `axg_pdm_dai_probe()`, `axg_pdm_dai_remove()`, `axg_pdm_startup()`, `axg_pdm_shutdown()`, `axg_pdm_hw_params()`, and `axg_pdm_trigger()`. Hardware helpers include `axg_pdm_enable()`, `axg_pdm_disable()`, `axg_pdm_filters_enable()`, `axg_pdm_get_os()`, `axg_pdm_set_sysclk()`, `axg_pdm_set_sample_pointer()`, `axg_pdm_set_channel_mask()`, and filter programming helpers for HCIC, LPF, and HPF.

Control flow: Probe maps registers, gets `pclk`, `dclk`, and `sysclk`, and registers the component. DAI probe enables pclk, sets/enables sysclk to the configured maximum, disables the device, clears filter bypass, programs HCIC/HPF controls, and writes all LPF coefficient taps through coefficient address/data registers. Startup enables dclk and filter blocks. `hw_params` accepts only 24- or 32-bit samples, computes oversampling from HCIC and three LPF downsample factors, sets sysclk and dclk, calculates sample-pointer capture position at 75 percent of the half dclk period, and enables the requested channel count. Trigger resets the AFIFO and toggles PDM enable.

State and persistence: `struct axg_pdm` stores config, regmap, and clocks. Static default filter coefficient tables persist in driver text and are loaded into hardware coefficient memory during DAI probe. Channel masks and filter settings persist in hardware until reprogrammed or reset.

Dependencies and integration points: Integrates with AXG sound card capture routes, `SND_SOC_DMIC` implied Kconfig support, regmap MMIO, Common Clock, and ALSA capture DAI negotiation.

Risks: Filter coefficients are fixed defaults with a TODO for firmware-configurable alternatives, so microphone-specific tuning is not represented. Accessing registers requires sysclk as well as pclk; missing clock sequencing can bus fault. The LPF tap count must fit below `PDM_LPF_MAX_STAGE`. Sample-pointer calculation warns and fails if sysclk/dclk ratios exceed the hardware pointer width.

Test signals: PDM capture at rates up to 48 kHz, 1-8 channel masks, S24/S32 captures, clock-rate traces for sysclk/dclk, coefficient memory loading, trigger start/stop AFIFO reset behavior, and capture quality/latency checks against expected filter response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-pdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifin.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifin.c

Purpose: Implements the AXG SPDIF input DAI and component controls. It configures input mode-detection timers/thresholds, exposes volatile capture-rate and IEC958 channel-status controls, handles reset sequencing, and registers capture capabilities derived from supported SPDIF modes.

Important APIs and functions: Runtime ops are `axg_spdifin_dai_probe()`, `axg_spdifin_dai_remove()`, and `axg_spdifin_prepare()`. Mode helpers include `axg_spdifin_sample_mode_config()`, `axg_spdifin_mode_timer()`, `axg_spdifin_write_timer()`, and `axg_spdifin_write_threshold()`. Controls include `axg_spdifin_rate_lock_get()`, `axg_spdifin_get_status()`, and IEC958 mask/status info callbacks. `axg_spdifin_get_dai_drv()` dynamically builds the DAI rate mask from mode rates.

Control flow: Probe maps registers, gets pclk/refclk, creates a DAI driver with IEC958 subframe capture format and mode-derived rate bits, and registers the component. DAI probe enables pclk, sets the reference clock, programs a 1 ms base timer, calculates timers and thresholds for seven sample-rate modes, enables refclk, and enables the SPDIFIN block. Prepare applies out/in reset sequencing. Controls read current mode/max-width status to report locked rate and read channel-status bytes by selecting status banks.

State and persistence: `struct axg_spdifin` stores config, regmap, and clocks. Mode thresholds persist in `SPDIFIN_CTRL2/4/5/6`; enable/reset/status selection persist in `SPDIFIN_CTRL0`. Captured channel status is volatile hardware state.

Dependencies and integration points: Depends on regmap MMIO, clock APIs, ALSA IEC958 control conventions, and AXG card capture routes. Compatible `amlogic,axg-spdifin` selects the seven standard rates and a 333333333 Hz reference.

Risks: The source comments document unreliable mode-change IRQ behavior, so the driver deliberately avoids stopping streams based on detected rate changes. Rate-lock is informational and may be zero during no-signal or glitches. Threshold math depends on actual refclk rate after `clk_set_rate()`. Capture accepts only IEC958 subframe format.

Test signals: Capture at 32/44.1/48/88.2/96/176.4/192 kHz, no-signal handling, volatile `Capture Rate Lock`, IEC958 status reads for both channel-status sources, reset prepare sequencing, and clock/regmap traces for mode timers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifout.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifout.c

Purpose: Implements the AXG SPDIF output DAI and component. It configures SPDIF framing, sample extraction from FIFO words, IEC958 channel-status words, mute via validity bit, input source DAPM routing, playback mixer controls, and mclk/pclk sequencing.

Important APIs and functions: Runtime ops are `axg_spdifout_startup()`, `axg_spdifout_shutdown()`, `axg_spdifout_hw_params()`, `axg_spdifout_trigger()`, and `axg_spdifout_mute()`. Helpers include `axg_spdifout_enable()`, `axg_spdifout_disable()`, `axg_spdifout_sample_fmt()`, and `axg_spdifout_set_chsts()`. Component bias callback `axg_spdifout_set_bias_level()` enables mclk in PREPARE and disables it on return to STANDBY.

Control flow: Startup enables pclk, disables the block, sets baseline data ordering, selects manual control for V/C/U bits, and writes a static swap configuration. `hw_params` sets mclk to `rate * 128`, configures channel mask and sample packing based on channel count and physical width, positions the MSB from actual sample width, and writes consumer IEC958 status into A and B channel registers while clearing the remaining status words. Trigger applies reset sequencing and enables/disables the block. Mute sets the SPDIF validity bit.

State and persistence: `struct axg_spdifout` stores regmap, mclk, and pclk. Routing, gain, mute, channel-status, and sample-format bits persist in SPDIFOUT registers. Bias level controls mclk lifetime independent of stream pclk startup.

Dependencies and integration points: Uses ALSA IEC958 helpers, regmap MMIO, clocks named `pclk` and `mclk`, DAPM source mux from IN0-IN2, and AXG sound-card routes from FRDDR/TDM outputs.

Risks: Comments note documentation has inverted meaning for V/U/C select bits; future changes must preserve the empirically correct manual-control semantics. Only 1 or 2 channels and 8/16/32 physical width modes are supported. Channel-status generation writes only the first 32 bits and clears the rest. MCLK and pclk are controlled by different lifecycle callbacks, so bias transitions matter.

Test signals: SPDIF playback at supported rates, S8/S16/S20/S24 samples, 1- and 2-channel streams, receiver IEC958 status verification, mute/unmute via validity bit, DAPM input-source switching, and bias-level clock enable traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.c

Purpose: Provides shared infrastructure for AXG TDM formatter blocks such as TDMIN and TDMOUT. It attaches formatter DAPM widgets to active TDM streams, manages formatter clocks and resets, prepares formatter registers through block-specific ops, distributes channel masks, and starts/stops all formatters associated with a stream.

Important APIs and functions: Exported APIs include `axg_tdm_formatter_set_channel_masks()`, `axg_tdm_formatter_event()`, `axg_tdm_formatter_probe()`, `axg_tdm_stream_start()`, `axg_tdm_stream_stop()`, `axg_tdm_stream_alloc()`, `axg_tdm_stream_free()`, and `axg_tdm_stream_set_cont_clocks()`. Internal helpers handle enable/disable, attach/detach, and DAPM power up/down.

Control flow: DAPM PRE_PMU resolves the backend stream through formatter ops, enables pclk, reparents formatter bit/sample clock inputs to the TDM interface clocks, stores the stream, and attaches the formatter. If the stream is already ready, attach immediately enables the formatter. Stream start marks the stream ready and enables every attached formatter; enable resets the formatter, sets sclk phase based on DAI format, calls block-specific prepare, enables sclk/lrclk, and invokes block-specific enable. Stream stop disables every attached formatter and clears ready. PRE_PMD detaches, disables, drops pclk, and clears the stream pointer. Continuous clock helper enables or disables interface mclk/sclk/lrclk based on `SND_SOC_DAIFMT_CONT`.

State and persistence: `struct axg_tdm_formatter` stores the current stream pointer, driver ops/quirks, clocks, reset, enabled flag, regmap, and list node. `struct axg_tdm_stream` stores formatter list, lock, stream parameters, mask, ready state, and continuous-clock state. Formatter register state persists until disabled/reset.

Dependencies and integration points: Used by TDMIN/TDMOUT formatter drivers and `axg-tdm-interface.c`. Depends on regmap, reset controls, clock parent/phase APIs, DAPM events, and `axg-tdm.h` format helpers.

Risks: Formatter attach/detach and stream start/stop are serialized by `ts->lock`; missing detach before stream free triggers warnings. Multi-lane restart can channel-shift on some SoCs unless the optional reset line is used before every start. Channel-mask distribution intentionally mimics hardware pair/lane ordering and is easy to break. Continuous-clock cleanup uses goto labels that also serve normal disable flow, so state transitions need careful review.

Test signals: TDMIN/TDMOUT DAPM power transitions, active-stream attach after formatter power-up and formatter power-up after active stream, multi-lane restart channel ordering, continuous-clock links, reset-line presence/absence, and mask distribution for nontrivial per-lane slot maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.h

Purpose: Declares the shared formatter driver contract for AXG TDM formatter blocks.

Important APIs and types: `struct axg_tdm_formatter_hw` carries hardware quirks such as skew offset. `struct axg_tdm_formatter_ops` lets a concrete formatter provide stream lookup, enable, disable, and prepare callbacks. `struct axg_tdm_formatter_driver` bundles component driver, regmap config, ops, and quirks for OF match data. Public prototypes expose channel-mask programming, DAPM event handling, and platform probe.

Control flow: No executable logic. Concrete formatter modules pass a `axg_tdm_formatter_driver` as match data to the common probe and use `axg_tdm_formatter_event()` in DAPM widgets.

State and persistence: Declares configuration structures that persist as static match data and drive runtime formatter state in `axg-tdm-formatter.c`.

Dependencies and integration points: Includes `axg-tdm.h` for stream/interface definitions and is included by TDM formatter implementations such as TDMIN/TDMOUT.

Risks: The ops contract assumes `get_stream()` can resolve a live `axg_tdm_stream` from DAPM graph topology. Incorrect quirks or regmap configs can break all formatter lifecycle code.

Test signals: Build/link coverage of formatter modules, OF match data validation, DAPM event invocation, and block-specific prepare callbacks receiving expected stream parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-formatter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-interface.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-interface.c

Purpose: Implements the AXG TDM interface DAI, which owns pad/loopback stream objects, validates TDM slot masks and widths, configures master/sample/bit clocks, enforces rate constraints and component-wide symmetry, and starts/stops attached formatters through the TDM stream API.

Important APIs and functions: Exported `axg_tdm_set_tdm_slots()` records per-lane TX/RX masks, slot count, slot width, channel maxima, and format masks. DAI ops include `set_sysclk`, `set_fmt`, `startup`, `hw_params`, `hw_free`, `trigger`, probe, and remove. Helpers include `axg_tdm_slots_total()`, `axg_tdm_iface_set_stream()`, `axg_tdm_iface_set_sclk()`, and `axg_tdm_iface_set_lrclk()`.

Control flow: DAI probe allocates an `axg_tdm_stream` for each stream direction with a widget. Card init calls `axg_tdm_set_tdm_slots()` before runtime to install masks and narrow channel/format capabilities. Startup rejects streams with no slots, applies an existing active component rate as a hard constraint or computes max rate from `MAX_SCLK / (slots * slot_width)`. `hw_params` validates the DAI format, checks channel count versus slots and sample width versus slot width, stores stream parameters, programs sclk/lrclk when CPU is clock master, and applies continuous clocks if requested. Trigger starts/stops the corresponding stream, which in turn enables/disables attached formatters. Bias level manages mclk when entering/leaving PREPARE.

State and persistence: `struct axg_tdm_iface` stores clocks, mclk rate, common format, slot geometry, and active rate. `axg_tdm_stream` objects are attached to playback/capture DMA data. DAI driver instances are duplicated at probe because slot masks mutate per-instance channel maxima and formats.

Dependencies and integration points: Called by `axg-card.c` during TDM backend initialization and by formatter code at stream start/stop. Uses common clock rate/phase/duty-cycle APIs, ASoC DAI and DAPM APIs, and `axg-tdm.h` inversion helpers.

Risks: CPU-master mode requires mclk; slave mode can omit it. MCLK must divide exactly into the desired bit clock if a fixed mclk rate was requested. I2S/left/right-justified formats reject slot counts above two, while DSP modes allow larger TDM frames. The error message says "has not slots" but the functional risk is missing mask configuration. Trigger ignores return from `axg_tdm_stream_start()`, so formatter-start failures may not propagate.

Test signals: TDM pad playback/capture, loopback capture, CPU master and slave clocking, `mclk-fs` sysclk requests, I2S versus DSP_A/B formats, continuous-clock links, invalid masks/slot widths, and multi-stream rate symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm-interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm.h

Purpose: Defines shared AXG TDM constants, stream/interface state structures, format masks, clock polarity helpers, stream lifecycle prototypes, and the TDM slot programming API.

Important APIs and types: `AXG_TDM_NUM_LANES`, `AXG_TDM_CHANNEL_MAX`, and `AXG_TDM_FORMATS` describe generic hardware capabilities. `struct axg_tdm_iface` stores sclk/lrclk/mclk and shared format/slot/rate state. `struct axg_tdm_stream` stores formatter list, lock, stream width/channel/mask data, ready flag, and continuous-clock state. Inline helpers `axg_tdm_lrclk_invert()` and `axg_tdm_sclk_invert()` centralize polarity interpretation. Prototypes expose stream allocation/start/stop/reset/continuous-clock and `axg_tdm_set_tdm_slots()`.

Control flow: No standalone executable flow beyond inline polarity helpers and stream reset, which stops then starts a stream. Runtime behavior is implemented in formatter and interface modules.

State and persistence: Declares state allocated by `axg-tdm-interface.c` and manipulated by formatter modules. The mask pointer is owned by card/link data and referenced by streams.

Dependencies and integration points: Included by AXG card, TDM interface, TDM formatter, TDMIN, and TDMOUT code. It is the shared ABI across separately built Meson TDM modules.

Risks: The polarity helpers encode subtle ASoC format/inversion semantics; changing them affects both interface clock phase and formatter compensation. Stream mask lifetime must outlive streams because only pointers are stored. `AXG_TDM_CHANNEL_MAX` allows large topologies but actual masks still cap active channels.

Test signals: Build/link coverage, TDM format inversion tests, stream reset behavior, and card-slot mask lifetime through probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmin.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmin.c

Purpose: Implements the AXG/G12A/SM1 TDM input formatter. It selects one of 16 TDM input pins, resolves the capture TDM stream through DAPM graph traversal, prepares input skew/format/slot/channel-mask registers, and delegates lifecycle management to the shared TDM formatter framework.

Important APIs and functions: The platform driver probes through `axg_tdm_formatter_probe()` with `axg_tdmin_drv` match data. Formatter ops are `axg_tdmin_get_tdm_stream()`, `axg_tdmin_prepare()`, `axg_tdmin_enable()`, and `axg_tdmin_disable()`. DAPM includes 16 AIF inputs, a `SRC SEL` mux, a `DEC` PGA with `axg_tdm_formatter_event()`, and an `OUT` AIF output.

Control flow: DAPM route traversal in `axg_tdmin_get_be()` walks upstream paths until it finds a backend DAI output and returns that DAI's capture stream. Formatter power-up in the common code attaches to that stream. Prepare computes bit skew from a SoC quirk plus format-specific adjustment, sets I2S-mode versus DSP behavior, compensates LRCLK inversion, programs slot width, clears LSB-first behavior so first received bit lands at bit 31, writes a static swap mask, and calls `axg_tdm_formatter_set_channel_masks()` for `TDMIN_MASK0..3`. Enable applies output/input reset sequencing and sets `TDMIN_CTRL_ENABLE`; disable clears it.

State and persistence: Static match data supplies a skew offset of 3 and the regmap range through `TDMIN_MUTE3`. Runtime state is held by the common formatter object. Selected input source, skew, mode, slot width, swap, and masks persist in TDMIN registers.

Dependencies and integration points: Depends on `axg-tdm-formatter` common code, `axg-tdm.h` polarity helpers, ASoC DAPM graph functions, and AXG card TDM links that expose capture streams.

Risks: Recursive DAPM graph traversal assumes a sane route graph and connected source paths. Skew programming is format-sensitive and includes a hardware quirk; wrong values cause bit misalignment. Channel masks depend on stream parameters having been validated by the interface before formatter prepare. The same driver data is used for AXG, G12A, and SM1 compatibles, so any SoC-specific divergence would need new match data.

Test signals: TDM capture from each input mux source, I2S/left-justified/DSP_A/DSP_B formats, LRCLK inversion variants, multi-lane masks, 8/16/24/32-bit slots, DAPM power transitions around `DEC`, and repeated start/stop checking channel alignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmin.c -->
