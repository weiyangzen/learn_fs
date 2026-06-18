# subset-b-006532 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmout.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmout.c

Purpose: implements the Amlogic AXG/G12A/SM1 TDM output formatter component. It turns selected TDM input streams into a formatted serial output, programs slot/sample geometry, gain/mute/mask registers, and exposes DAPM routes for ASoC graph routing.

Important APIs/types/functions: registers through `axg_tdm_formatter_probe` using `axg_tdm_formatter_driver` instances. Key helpers are `axg_tdmout_get_be`, `axg_tdmout_get_tdm_stream`, `axg_tdmout_prepare`, `axg_tdmout_enable`, and `axg_tdmout_disable`. It depends on `struct axg_tdm_stream`, `struct axg_tdm_formatter_ops`, `axg_tdm_formatter_set_channel_masks`, and `axg_tdm_formatter_event`.

Control flow: DAPM powers the `"ENC"` PGA, which calls the generic formatter event path. The driver recursively follows enabled sink paths to find the backend DAI, obtains its playback TDM stream, prepares `TDMOUT_CTRL0/CTRL1` from the stream format/slot geometry/physical width, writes swap and channel masks, then deasserts resets and enables the block. Disable clears `TDMOUT_CTRL0_ENABLE`.

State and persistence: state is hardware register state in the MMIO regmap. Per-SoC differences are immutable match-data quirks: AXG uses skew offset 1, G12A/SM1 use skew offset 2, and SM1 has five input mux choices plus a different gain-enable bit.

Dependencies and integration: integrates with ASoC DAPM, ALSA controls for lane volumes/gain enable/input mux, device-tree compatibles `amlogic,axg-tdmout`, `amlogic,g12a-tdmout`, and `amlogic,sm1-tdmout`, and shared Meson TDM formatter infrastructure.

Risks: only I2S, left-justified, DSP_A, and DSP_B timing are accepted; unsupported physical widths fail at prepare time. Incorrect DAPM graph wiring can make backend stream discovery return null. Clock polarity is corrected by re-inverting LRCLK, so mistakes in `dai_fmt` propagate directly to bad framing.

Test signals: probe success for each compatible, mixer visibility for lane gain/mux controls, DAPM route power-up of `"ENC"`, playback with 8/16/32-bit physical widths, and audible/channel-mask validation across AXG/G12A/SM1 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-tdmout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-toddr.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/axg-toddr.c

Purpose: implements the Amlogic TODDR frontend capture FIFO DAI. It captures audio from one selected internal input into memory through the shared AXG FIFO PCM layer.

Important APIs/types/functions: DAI ops include `axg_toddr_dai_startup`, `axg_toddr_dai_shutdown`, `axg_toddr_dai_hw_params`, `axg_toddr_pcm_new`, and G12A variants `g12a_toddr_dai_prepare` and `g12a_toddr_dai_startup`. Component callbacks are delegated to `axg_fifo_pcm_*` or `g12a_fifo_pcm_hw_params`.

Control flow: startup enables the FIFO peripheral clock, selects original non-resampled signed single-buffer capture, and for G12A/SM1 enables channel synchronization. `hw_params` maps physical width 8/16/32 to FIFO packing type, sets MSB/LSB extraction fields, and leaves DMA buffer programming to the FIFO component. G12A prepare toggles `CTRL1_TODDR_FORCE_FINISH` to reset the write pointer before capture.

State and persistence: capture state is held in the FIFO registers and clock enable state. DAPM input source selection is stored in either `FIFO_CTRL0` for AXG/G12A or `FIFO_CTRL1` for SM1. Match data changes threshold bitfields and available input count.

Dependencies and integration: depends on `axg-fifo.h`, ASoC DAPM, regmap, and the shared FIFO platform driver. Device-tree compatibles select AXG, G12A, or SM1 behavior.

Risks: resampling is explicitly not supported. Unsupported physical widths return `-EINVAL`. Capture channel ordering on G12A depends on the `CTRL0_TODDR_SYNC_CH` workaround and force-finish pointer reset. Wrong mux selection captures silence or the wrong internal source.

Test signals: capture open/close through the FIFO PCM component, correct input mux exposure, stable first-channel placement on G12A/SM1, pointer movement during recording, and no clock/regmap errors on repeated startup/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/axg-toddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/g12a-toacodec.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/g12a-toacodec.c

Purpose: implements the Amlogic G12A/SM1 glue codec routing block from internal I2S/TDM sources to the internal analog codec output.

Important APIs/types/functions: private state is `struct g12a_toacodec` with regmap fields for data, LRCLK, and BCLK source selection. Key functions are `g12a_toacodec_mux_put_enum`, `g12a_toacodec_input_hw_params`, component probes for G12A/SM1, and `g12a_toacodec_probe`. It reuses `meson_codec_glue_input_*` and `meson_codec_glue_output_startup`.

Control flow: probe resets the device, maps registers, allocates SoC-specific regmap fields, and registers four DAIs: three inputs and one output. When the DAPM mux changes, it temporarily disconnects the mux, writes data/LRCLK/BCLK selectors to the same source, updates MCLK selector, then restores DAPM power. Input hw_params stores source stream constraints via codec glue and clamps output channels to the two-channel internal DAC lane.

State and persistence: mux selection, lane selection, enable, and static clock inversion bits live in `TOACODEC_CTRL0`. Runtime stream constraints are stored in per-input glue data associated with DAIs.

Dependencies and integration: depends on Meson TDM format definitions, `meson-codec-glue`, dt-bindings IDs, reset controller, regmap, and ASoC DAPM controls. It is selected by `amlogic,g12a-toacodec` or `amlogic,sm1-toacodec`.

Risks: the code assumes I2S A/B/C map to matching MCLK sources; a FIXME notes this may be wrong for future clock topologies. Source switches must update data and clocks atomically enough to avoid DAPM routing glitches. Output is limited to one lane/two channels even if input streams advertise more.

Test signals: successful component probe initializes clock inversion bits, mux changes produce matching data/LRCLK/BCLK fields, lane select works for both bit layouts, and internal DAC playback works for all three I2S sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/g12a-toacodec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/g12a-tohdmitx.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/g12a-tohdmitx.c

Purpose: implements the G12A HDMI transmitter audio glue codec, routing internal I2S and SPDIF sources to HDMI-facing output DAIs.

Important APIs/types/functions: key mux callbacks are `g12a_tohdmitx_i2s_mux_put_enum` and `g12a_tohdmitx_spdif_mux_put_enum`. DAI ops are built from `meson_codec_glue_input_*` and `meson_codec_glue_output_startup`. `g12a_tohdmi_component_probe` initializes static clock capture inversion.

Control flow: probe resets the block, maps a 32-bit regmap, and registers seven DAIs: three I2S inputs, one I2S output, two SPDIF inputs, and one SPDIF output. DAPM mux writes keep data and clock selectors in sync while temporarily disconnecting the path. DAPM switches gate the shared output enable bit for the active path.

State and persistence: source selection, clock selection, inversion, and output enable are all in `TOHDMITX_CTRL0`. Per-input hardware parameters are cached by `meson-codec-glue` for constraint propagation to output startup.

Dependencies and integration: uses ASoC DAPM, Meson codec glue, dt-bindings IDs, reset control, regmap, and the `amlogic,g12a-tohdmitx` compatible.

Risks: I2S and SPDIF output switches share the same enable bit, so DAPM sequencing matters. Source mux callbacks assume matching data and clock source indices. SPDIF and I2S support different PCM format masks; mismatched routes should be rejected through constraints but need coverage.

Test signals: DAPM routes for all I2S/SPDIF paths, successful HDMI audio playback from each source, mixer source changes without stale clocks, and format/rate constraints for SPDIF versus I2S outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/g12a-tohdmitx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/gx-card.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/gx-card.c

Purpose: provides the Amlogic GX machine driver that turns sound-card device-tree child nodes into ASoC DPCM frontend/backend links.

Important APIs/types/functions: local state `struct gx_dai_link_i2s_data` stores `mclk_fs`. Important functions are `gx_card_add_link`, `gx_card_parse_i2s`, `gx_card_i2s_be_hw_params`, and `gx_card_cpu_identify`.

Control flow: generic `meson_card_probe` calls match-data `gx_card_add_link` for each DT child. FIFO CPU DAIs become dynamic frontend links. Other links become backend links; AIU codec-control links get codec-to-codec parameters, while I2S encoder links also parse DAI format and `mclk-fs` for sysclk setup during hw_params.

State and persistence: per-link I2S data is devm allocated and stored in `meson_card.link_data[index]`; card/link arrays are managed by common Meson card utilities. Runtime clock configuration is derived from PCM params and `mclk_fs`.

Dependencies and integration: integrates with `meson-card-utils.c`, AIU compatible names, ASoC DPCM, DT child link descriptions, and the `amlogic,gx-sound-card` compatible.

Risks: CPU DAI role detection uses string matching on DAI names such as `"FIFO"`, `"CODEC CTRL"`, and `"I2S Encoder"`, making it sensitive to naming changes. Missing `mclk-fs` silently skips sysclk programming.

Test signals: card registration from DT, correct FE/BE split, codec-to-codec link creation, I2S sysclk setting on hw_params, and playback/capture through GX AIU FIFO and encoder paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/gx-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-card-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/meson-card-utils.c

Purpose: shared helper implementation for Meson machine drivers. It parses DT sound-card links, allocates link arrays, builds FE/BE links, handles optional routing/widgets, and registers/unregisters the card.

Important APIs/types/functions: exports `meson_card_i2s_set_sysclk`, `meson_card_reallocate_links`, `meson_card_parse_dai`, `meson_card_parse_daifmt`, `meson_card_set_be_link`, `meson_card_set_fe_link`, `meson_card_probe`, and `meson_card_remove`.

Control flow: `meson_card_probe` allocates `struct meson_card`, copies match data, sets card owner/device/name, parses optional widgets/routing, calls `meson_card_add_links`, then registers with `devm_snd_soc_register_card`. Link creation reallocates `card.dai_link` and `link_data`, then invokes the machine-specific `add_link` callback for each DT child.

State and persistence: per-card state is devm allocated except link arrays and link-data arrays, which use `krealloc` and are freed by `meson_card_remove` through `meson_card_clean_references`. OF node references acquired in link components are released explicitly.

Dependencies and integration: depends on ASoC OF helpers, DAPM route/widget parsers, `meson-card.h`, and match-data callbacks supplied by concrete machine drivers such as GX.

Risks: `meson_card_reallocate_links` frees the new links allocation if link-data allocation fails, which is dangerous if `krealloc` moved the original pointer and may leave stale card state. Link names use `node->full_name`, so DT path changes affect ALSA stream names. Reference cleanup must stay matched to parsed components.

Test signals: malformed DT with no links or missing codecs returns errors; optional widgets/routing parse correctly; FE links are dynamic with dummy codecs; BE links parse all child codecs; remove releases OF references without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-card-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-card.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/meson-card.h

Purpose: declares the shared Meson sound-card data structures and helper APIs used by Meson machine drivers.

Important APIs/types/functions: defines `DT_PREFIX`, `struct meson_card_match_data` with an `add_link` callback, and `struct meson_card` containing `snd_soc_card`, match data, and per-link private data. It declares sysclk, link allocation, DAI parse, FE/BE link setup, probe, and remove helpers.

Control flow: this header has no runtime flow but defines the contract: a platform driver supplies match data whose `add_link` callback is invoked by `meson_card_probe`; helper functions then build ASoC links from DT nodes.

State and persistence: `struct meson_card` is the persistent card-level state. `link_data` is an array of machine-specific pointers aligned with `card.dai_link` indices.

Dependencies and integration: includes only forward declarations plus ALSA parameter declarations to keep consumers light. Used by `gx-card.c` and `meson-card-utils.c`.

Risks: the callback API passes a mutable link index, so machine drivers must increment/consume it consistently. The `DT_PREFIX` macro couples CPU identification helpers to `"amlogic,"` compatible strings.

Test signals: compile coverage for all Meson machine drivers, successful link-data indexing, and no ABI drift between declarations and exported helper definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-card.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.c

Purpose: provides common helper logic for Meson codec glue blocks that expose multiple input DAIs and one or more output DAIs with propagated runtime constraints.

Important APIs/types/functions: exports `meson_codec_glue_input_get_data`, `meson_codec_glue_input_hw_params`, `meson_codec_glue_input_set_fmt`, `meson_codec_glue_output_startup`, `meson_codec_glue_input_dai_probe`, and `meson_codec_glue_input_dai_remove`. Internal helpers locate DAPM widgets and store per-input `struct meson_codec_glue_input`.

Control flow: input DAI probe allocates glue input state and binds it to the DAI playback widget. Input `hw_params` copies rate/channel/format intervals into that state; input `set_fmt` records the DAI format. Output startup walks source DAPM paths and applies the selected input constraints to the output substream.

State and persistence: state is per-input DAI devm-like allocation controlled by probe/remove, stored as DAI private data and widget private data. It persists while the component is registered and is updated on hw_params.

Dependencies and integration: used by G12A to-acodec and to-hdmitx glue drivers. Depends on ASoC DAPM graph traversal and ALSA runtime constraint APIs.

Risks: constraint propagation depends on correct DAPM source discovery; a missing or inactive source can leave outputs unconstrained or fail startup. The helper stores the last input parameters, so unusual graph changes before output startup need careful sequencing.

Test signals: input probe/remove memory lifecycle, output startup constraints matching active input, route switching across multiple inputs, and rejection of incompatible output params after input hw_params.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.h -->
# sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.h

Purpose: declares the common Meson codec-glue input state and helper functions used by internal DAC and HDMI glue codecs.

Important APIs/types/functions: `struct meson_codec_glue_input` stores `snd_soc_pcm_stream params` and `fmt`. Declarations cover input data retrieval, input hw_params/set_fmt/probe/remove, and output startup.

Control flow: no executable flow; this is the contract that glue drivers wire into their `snd_soc_dai_ops`.

State and persistence: exposes the state layout that input DAIs use to remember last negotiated stream parameters and format.

Dependencies and integration: includes ALSA ASoC and PCM parameter types; consumed by `g12a-toacodec.c`, `g12a-tohdmitx.c`, and implemented by `meson-codec-glue.c`.

Risks: because drivers can mutate `params` after helper hw_params, callers must preserve invariants expected by output startup. Header changes affect multiple codec glue drivers.

Test signals: compile coverage from all Meson glue drivers and runtime validation that `meson_codec_glue_input_get_data` returns usable state after DAI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/meson-codec-glue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/t9015.c -->
# sources/distributed-fs/ceph-client/sound/soc/meson/t9015.c

Purpose: implements the Amlogic T9015 internal stereo DAC codec driver, including volume/mute controls, DAPM widgets/routes, bias sequencing, and I2S format selection.

Important APIs/types/functions: private `struct t9015` holds the analog supply regulator. Key functions are `t9015_dai_set_fmt`, `t9015_set_bias_level`, and `t9015_probe`. The component driver exposes controls for DAC volume, ramp/mute modes, mono mode, and channel source muxes.

Control flow: probe enables and resets baseline analog register values through regmap and registers one playback DAI. `set_fmt` supports I2S mode only and configures data inversion for normal/inverted bit clocks. Bias transitions enable VMID/bias/reference buffers and DAC/lineout blocks on prepare/on, then soft-mute and power down on standby/off.

State and persistence: codec state is mostly register-backed in `BLOCK_EN`, `VOL_CTRL*`, `LINEOUT_CFG`, and `POWER_CFG`. Regulator enablement and bias level are managed by ASoC component lifecycle.

Dependencies and integration: uses platform MMIO regmap, regulator named by DT, ASoC controls/DAPM, and `amlogic,t9015` compatible. Playback supports 1-2 channels and common 16/20/24/32-bit formats up to 192 kHz.

Risks: bias sequencing is analog-pop sensitive; mistakes can cause noise or no output. Only I2S format is accepted. Register defaults are written manually rather than through a regmap defaults table, so probe failures partway through can leave partial hardware state.

Test signals: codec probe with regulator present, mixer volume/mute/ramp controls, DAPM power transitions without pops, I2S playback with normal and inverted clock settings, and suspend/resume register behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/meson/t9015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/Kconfig

Purpose: defines Kconfig options for Freescale MXS ASoC support and the MXS SGTL5000 machine driver.

Important APIs/types/functions: `SND_MXS_SOC` is the menuconfig root, depending on `ARCH_MXS || COMPILE_TEST` and `COMMON_CLK`, and selecting `SND_SOC_GENERIC_DMAENGINE_PCM`. `SND_SOC_MXS_SGTL5000` depends on `I2C` and selects `SND_SOC_SGTL5000`.

Control flow: Kconfig selection enables compilation of SAIF/PCM support and, optionally, the SGTL5000 board driver.

State and persistence: no runtime state; it persists build-time feature relationships.

Dependencies and integration: feeds `sound/soc/mxs/Makefile` object selection and ensures DMAEngine PCM and codec dependencies are available.

Risks: board audio will not build unless the parent menu is enabled; SGTL5000 selection assumes I2C. `COMPILE_TEST` allows non-MXS builds but runtime hardware dependencies still apply.

Test signals: `allyesconfig`, `allmodconfig`, MXS defconfig, and dependency resolution for SGTL5000 with I2C enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/Makefile

Purpose: maps MXS ASoC Kconfig symbols to kernel objects.

Important APIs/types/functions: builds `snd-soc-mxs.o` from `mxs-saif.o`, `snd-soc-mxs-pcm.o` from `mxs-pcm.o`, and `snd-soc-mxs-sgtl5000.o` from `mxs-sgtl5000.o`.

Control flow: when `CONFIG_SND_MXS_SOC` is set, both SAIF and PCM helper modules are linked; when `CONFIG_SND_SOC_MXS_SGTL5000` is set, the machine driver is linked.

State and persistence: build-only state in object lists.

Dependencies and integration: aligned with `Kconfig` and the SAIF driver’s call to `mxs_pcm_platform_register`.

Risks: separating PCM and SAIF into two objects means symbol export/import must stay correct. Missing object selection would leave unresolved machine-driver or platform registration symbols.

Test signals: module build for `CONFIG_SND_MXS_SOC=m`, built-in build, and modpost symbol checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.c

Purpose: provides the MXS DMAEngine PCM registration helper and hardware constraints used by the SAIF DAI.

Important APIs/types/functions: `snd_mxs_hardware` defines MMAP, pause/resume, interleaved, half-duplex, period, buffer, and FIFO limits. `mxs_dmaengine_pcm_config` wraps it. `mxs_pcm_platform_register` exports registration via `devm_snd_dmaengine_pcm_register`.

Control flow: SAIF probe calls `mxs_pcm_platform_register`, which registers the DMAEngine PCM component with `SND_DMAENGINE_PCM_FLAG_HALF_DUPLEX`.

State and persistence: no mutable state here; DMAEngine PCM core owns runtime PCM buffers after registration.

Dependencies and integration: depends on `sound/dmaengine_pcm.h` and is consumed by `mxs-saif.c` through `mxs-pcm.h`.

Risks: hardware constraints are conservative but shared for playback/capture; incorrect period/buffer sizes can cause DMA underrun or ALSA constraint failures. Half-duplex flag prevents simultaneous independent PCM operation.

Test signals: PCM device creation after SAIF probe, DMAEngine channel binding, ALSA hw_params constraint negotiation, and playback/capture smoke tests around min/max period sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.h

Purpose: declares the MXS PCM platform registration helper.

Important APIs/types/functions: `mxs_pcm_platform_register(struct device *dev)` is the only exported API.

Control flow: no runtime flow; `mxs-saif.c` includes this header and calls the helper during probe.

State and persistence: no state.

Dependencies and integration: keeps the SAIF driver independent from the PCM helper implementation while allowing modular symbol export.

Risks: signature drift would break the SAIF build. The header does not include `struct device` forward declaration, relying on including files to provide it.

Test signals: compile and modpost coverage for MXS SAIF plus PCM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.c -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.c

Purpose: implements the Freescale MXS SAIF CPU DAI driver, including SAIF master/slave clocking, MCLK export, DAI format setup, DMA-triggered playback/capture, IRQ error accounting, and PCM registration.

Important APIs/types/functions: global `mxs_saif[2]` indexes the two SAIF instances. Exported helpers `mxs_saif_get_mclk` and `mxs_saif_put_mclk` allow codecs/machine drivers to use SAIF MCLK. DAI ops include `mxs_saif_set_dai_sysclk`, `mxs_saif_set_dai_fmt`, `mxs_saif_startup`, `mxs_saif_hw_params`, `mxs_saif_prepare`, and `mxs_saif_trigger`.

Control flow: probe resolves the SAIF alias ID, optional `fsl,saif-master` phandle, clock, MMIO, IRQ, and registers the DAI plus DMAEngine PCM. Startup clears reset/clock-gate and prepares the clock. `hw_params` programs master clock rate, word length, 48xfs mode, and TX/RX direction. Trigger enables master and possibly local clocks, starts RUN, primes or drains `SAIF_DATA`, and tracks running state; stop waits one sample period before disabling.

State and persistence: `struct mxs_saif` tracks clock, base, id/master id, current rate, MCLK use, ongoing flag, underrun/overrun counters, and running/stopped state. Hardware control/status registers hold format and run state.

Dependencies and integration: depends on DT aliases, optional master phandle, common clock framework, raw MMIO set/clear registers, IRQ handling, `mxs-pcm`, and ASoC DAI registration. SAIF0 can register an exported `mxs_saif_mclk` clock provider.

Risks: global two-entry state assumes only two SAIFs and correct probe ordering for master references. Clock-rate changes are rejected while the master is ongoing; simultaneous streams must share rate. Raw MMIO and busy polling make ordering important. Error counters are debug-only and do not stop streams.

Test signals: probe of both SAIF instances with correct aliases, MCLK get/put from SGTL5000 path, I2S and left-justified playback/capture, shared-rate enforcement, IRQ handling for FIFO underflow/overflow, and suspend/resume clock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.h -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.h

Purpose: defines MXS SAIF register offsets, bit masks, helper macros, MCLK ID, driver state structure, and exported MCLK helper declarations.

Important APIs/types/functions: register groups include `SAIF_CTRL`, `SAIF_STAT`, `SAIF_DATA`, and `SAIF_VERSION`. `struct mxs_saif` stores device, clock, MCLK, MMIO base, IDs, rate, error counters, and state enum. Exports `mxs_saif_put_mclk` and `mxs_saif_get_mclk`.

Control flow: no executable flow, but macro definitions are directly used to compose control register writes in `mxs-saif.c`.

State and persistence: defines the persistent per-controller state used by the SAIF driver.

Dependencies and integration: includes `mxs-pcm.h` and is used by the SGTL5000 machine driver for MCLK APIs.

Risks: register bit definitions are hardware contract; incorrect masks can corrupt adjacent fields. The exposed `struct mxs_saif` makes implementation details visible to local compilation units.

Test signals: compile coverage, register programming validation on hardware, and SGTL5000 machine-driver linkage to exported MCLK helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-saif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-sgtl5000.c -->
# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-sgtl5000.c

Purpose: implements the MXS board machine driver for SGTL5000 codec connections over SAIF.

Important APIs/types/functions: `mxs_sgtl5000_hw_params` chooses MCLK ratio and sets codec/CPU clocks. DAI links are declared for playback and capture with SGTL5000 and SAIF components. Probe parses DT codec/cpu phandles and registers `snd_soc_card`.

Control flow: on hw_params, the driver uses 256fs MCLK at 96 kHz and 512fs otherwise, sets SGTL5000 sysclk, sets SAIF sysclk/MCLK, and relies on the SAIF DAI for clock generation. Probe fills link component OF nodes from DT and registers the card; remove clears card drvdata.

State and persistence: card/link structures are static, with runtime OF-node assignments during probe. Clock state lives in SGTL5000 and SAIF drivers.

Dependencies and integration: depends on `mxs-saif` exported MCLK behavior, SGTL5000 codec driver, DT bindings for `audio-codec`/`cpu-dai`, DAPM headphone/speaker/mic widgets, and ASoC card registration.

Risks: static card/link data can be problematic if multiple instances are probed. Clock ratio assumptions are SGTL5000-specific. Missing DT phandles fail probe.

Test signals: card registration on MXS boards, 44.1/48/96 kHz playback with correct MCLK, DAPM widget visibility, and probe deferral behavior when codec or CPU DAI is not ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-sgtl5000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/Kconfig

Purpose: defines build-time configuration for PXA2xx, PXA SSP, MMP SSPA, and Spitz ASoC support.

Important APIs/types/functions: root `SND_PXA2XX_SOC` selects `SND_PXA2XX_LIB`; AC97 selects new AC97 bus and PXA AC97 library; I2S is tristate selected by boards; SSP depends on `ARCH_PXA`; MMP SSPA depends on `ARCH_MMP`; Spitz selects I2S and WM8750.

Control flow: Kconfig symbols control which CPU DAI, platform, and machine drivers are compiled by the PXA Makefile.

State and persistence: build-time dependency state only.

Dependencies and integration: binds platform architecture symbols, legacy GPIO requirement for compile testing, codec selections, and ALSA library dependencies.

Risks: `SND_PXA2XX_SOC_I2S` has no prompt and is usually selected indirectly. `SND_PXA_SOC_SSP` lacks `COMPILE_TEST`, limiting coverage. AC97 requires `AC97_BUS=n` and selects `AC97_BUS_NEW`.

Test signals: PXA/MMP defconfigs, allyesconfig/allmodconfig dependency checks, and ensuring Spitz selects I2S/WM8750 correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/Makefile

Purpose: maps PXA/MMP ASoC Kconfig symbols to object files.

Important APIs/types/functions: builds `pxa2xx-pcm.o`, `pxa2xx-ac97.o`, `pxa2xx-i2s.o`, `pxa-ssp.o`, `mmp-sspa.o`, and Spitz machine object according to config symbols.

Control flow: object lists are included in the kernel build based on selected symbols.

State and persistence: build system state only.

Dependencies and integration: aligned with PXA Kconfig and exported PXA2xx PCM library functions used by AC97/I2S/SSP components.

Risks: missing object inclusion causes unresolved symbols for machine drivers or absent DAIs. Built-in/module combinations need symbol exports from shared libraries.

Test signals: module and built-in builds for each symbol combination, especially Spitz selecting I2S and AC97 selecting PXA library support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.c -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.c

Purpose: implements the Marvell MMP SSPA CPU DAI and PCM component for serial audio playback/capture.

Important APIs/types/functions: private `struct sspa_priv` stores TX/RX bases, DMA data, clocks, running count, and cached SP/CTL values. DAI ops include `mmp_sspa_set_dai_fmt`, `mmp_sspa_hw_params`, `mmp_sspa_trigger`, clock setters, startup/shutdown, and probe. Component callbacks include custom `mmp_pcm_mmap`, `mmp_sspa_open`, and `mmp_sspa_close`.

Control flow: platform probe maps RX/TX registers, gets clocks, registers optional DMAEngine PCM for DT systems, registers component/DAI, enables runtime PM and audio clock. Open verifies hardware is idle, writes reset/flush configuration, clears reset, and writes initial CTL. hw_params maps sample formats to SSPA word/sample sizes, sets frame width/period, configures bitclk for DT, and writes TX or RX control. Trigger always enables RX for hardware reasons, enables TX only for playback, and disables RX when the shared running count reaches zero.

State and persistence: cached `sp` and `ctrl` fields persist desired port format across open/hw_params. `running_cnt` coordinates shared RX hardware. Runtime PM and clocks track device active state.

Dependencies and integration: depends on `mmp-sspa.h`, DMAEngine PCM, runtime PM, clock framework, ASoC DAI/component APIs, and optional DT compatible `marvell,mmp-sspa`.

Risks: `running_cnt` is not protected by a lock in trigger paths. DT mode returns `-ENOTSUPP` for legacy clock setter APIs and expects bitclk clock rate programming in hw_params. Custom mmap maps noncached DMA pages and must match buffer allocation semantics.

Test signals: DT and non-DT probe, playback/capture startup with shared RX enable, 8/16/24/32-bit formats, runtime PM balance, DMA mmap behavior, and stop sequences driving running count back to zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.h -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.h

Purpose: defines Marvell MMP SSPA register offsets, bit masks, sample-size encodings, clock-source IDs, and PLL IDs.

Important APIs/types/functions: register offsets include `SSPA_D`, `SSPA_CTL`, `SSPA_SP`, and FIFO/interrupt registers. Macros compose CTL frame/word/sample-size fields and SP enable/reset/frame-sync fields. Clock IDs include `MMP_SSPA_CLK_PLL`, `MMP_SSPA_CLK_VCXO`, `MMP_SSPA_CLK_AUDIO`, `MMP_SYSCLK`, and `MMP_SSPA_CLK`.

Control flow: no runtime flow; the macros are consumed by `mmp-sspa.c` format, clock, and trigger code.

State and persistence: no state, only hardware definitions.

Dependencies and integration: local header for the MMP SSPA DAI driver and any future board-specific users.

Risks: field macros do not mask input values, so callers must pass valid encoded widths. Incorrect bit definitions would break serial port timing and clocking.

Test signals: compile coverage and hardware validation of all supported sample widths and master/slave mode fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/mmp-sspa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.c -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.c

Purpose: implements the PXA2xx/PXA3xx SSP ASoC CPU DAI, including clock source/PLL control, I2S/DSP/TDM formatting, DMA parameters, runtime trigger, and suspend/resume register save/restore.

Important APIs/types/functions: private `struct ssp_priv` stores the requested `ssp_device`, optional external clock, sysclk, DAI format, and PM register snapshots. DAI ops include `pxa_ssp_set_dai_sysclk`, `pxa_ssp_set_dai_fmt`, `pxa_ssp_set_dai_tdm_slot`, `pxa_ssp_set_dai_tristate`, `pxa_ssp_hw_params`, `pxa_ssp_trigger`, probe/remove, startup/shutdown.

Control flow: DAI probe requests the SSP by DT phandle or legacy ID and optional extclk. Startup enables clocks, disables SSP when first active, allocates per-substream DMA data, and sets channel names. hw_params sets DMA width/burst, applies deferred DAI format if inactive, configures data size, PLL/dividers, I2S PSP timing, and validates TDM slots. Trigger toggles TX/RX service bits and SSP enable based on ALSA trigger commands.

State and persistence: SSP hardware registers hold active configuration; `ssp_priv` tracks desired and configured format to avoid redundant reprogramming. PM saves SSCR0/SSCR1/SSTO/SSPSP while inactive or active.

Dependencies and integration: uses PXA SSP core APIs (`pxa_ssp_request*`, read/write helpers), `sound/pxa2xx-lib` PCM component callbacks, DMAEngine PCM data, optional DT compatible `mrvl,pxa-ssp-dai`, and local `pxa-ssp.h`.

Risks: format changes are only safe while inactive; active hw_params returns without reconfiguration. Network/TDM mode requires slot masks or fails. Clocking differs by SSP type, and PXA3xx dithered clock paths need careful validation. Busy-waiting on SSSR can hang if hardware misbehaves.

Test signals: DT and legacy probe, I2S/DSP_A/DSP_B formats, master/slave combinations, TDM slot setup, 16/32-bit DMA widths, suspend/resume with active and inactive streams, and no DMA data leaks across startup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.h -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.h

Purpose: declares PXA SSP clock source and divider constants used by machine drivers and the SSP DAI.

Important APIs/types/functions: defines `PXA_SSP_CLK_PLL`, `PXA_SSP_CLK_EXT`, `PXA_SSP_CLK_NET`, `PXA_SSP_CLK_AUDIO`, `PXA_SSP_CLK_NET_PLL`, divider IDs `PXA_SSP_AUDIO_DIV_ACDS`, `PXA_SSP_AUDIO_DIV_SCDB`, `PXA_SSP_DIV_SCR`, audio divider values, network divider values, and `PXA_SSP_PLL_OUT`.

Control flow: no executable flow; values are passed to DAI clock APIs.

State and persistence: no mutable state.

Dependencies and integration: consumed by `pxa-ssp.c` and board/machine code that configures SSP clocks.

Risks: constants are ABI-like for machine drivers; changing values would silently alter clock selection. Some constants are historical and not all are consumed in the current driver.

Test signals: compile coverage of users and clock configuration tests for each clock source path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa-ssp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-ac97.c

Purpose: implements the PXA2xx AC97 ASoC CPU DAI and AC97 controller binding, including reset/read/write callbacks and DMA data for stereo, aux, and mic FIFOs.

Important APIs/types/functions: `pxa2xx_ac97_ops` wraps AC97 controller read/write/reset operations from `pxa2xx-lib`. Startup callbacks select DMA data for HiFi, aux, or mic DAIs. Probe registers the AC97 controller and ASoC component with three DAIs.

Control flow: platform probe validates single-port use, derives DMA FIFO physical addresses from the MEM resource, probes AC97 hardware, registers `snd_ac97_controller`, stores it as driver data, and registers ASoC DAIs. Remove unregisters the controller and removes hardware. PM delegates to PXA AC97 hardware suspend/resume helpers.

State and persistence: DMA address structures are static but filled at probe. AC97 controller state is owned by ALSA AC97 core. Hardware state is handled by pxa2xx-lib.

Dependencies and integration: depends on `sound/ac97/controller.h`, `sound/pxa2xx-lib.h`, DMAEngine PCM, platform resource layout, and DT compatibles for PXA250/270/300 AC97.

Risks: static DMA data assumes one physical AC97 port. Probe registers the AC97 controller before ASoC component; later registration failure may rely on devm unwinding but controller unregister is only in remove. Mic DAI rejects playback explicitly.

Test signals: AC97 codec enumeration, warm/cold reset behavior, stereo/aux/mic capture/playback DMA channels, suspend/resume, and DT resource address mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.c

Purpose: implements the legacy PXA2xx I2S CPU DAI and component using the PXA2xx PCM library.

Important APIs/types/functions: global `struct pxa_i2s_port pxa_i2s`, `clk_i2s`, `clk_ena`, and `i2s_reg_base` hold controller state. DAI ops include `pxa2xx_i2s_set_dai_fmt`, `pxa2xx_i2s_hw_params`, `pxa2xx_i2s_trigger`, startup/shutdown, probe/remove, and PM save/restore.

Control flow: platform probe maps registers and sets DMA FIFO addresses. DAI probe gets `I2SCLK`, resets the controller, disables replay/record, and initializes DMA data. hw_params enables the clock, selects DMA data, programs master/format/FIFO thresholds, enables service interrupts, and sets `SADIV` for supported rates. Trigger starts by enabling replay/record and `SACR0_ENB`; shutdown disables the stream direction and turns off the clock when both directions are disabled.

State and persistence: controller state is global, so it assumes one I2S controller instance. PM snapshots `SACR0/SACR1/SAIMR/SADIV`. DMA data structures are static.

Dependencies and integration: uses `sound/pxa2xx-lib` PCM callbacks, `pxa2xx-i2s.h`, platform resources, and fixed-rate divider programming.

Risks: `if (!(SACR0 & SACR0_ENB))` appears to test the register-offset macro rather than the register value, so inactive configuration logic is effectively wrong. Global state prevents multiple independent instances. Unsupported formats are not explicitly rejected in `set_dai_fmt` for all default cases.

Test signals: stereo 16-bit playback/capture at all listed rates, clock enable/disable balance, suspend/resume register restore, and regression coverage for the inactive-port configuration condition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.h

Purpose: declares the PXA2xx I2S sysclk ID.

Important APIs/types/functions: defines `PXA2XX_I2S_SYSCLK` as clock ID 0.

Control flow: no executable flow; machine drivers pass this ID to `snd_soc_dai_set_sysclk`.

State and persistence: no state.

Dependencies and integration: used by `pxa2xx-i2s.c` and the Spitz machine driver.

Risks: minimal; value changes would break machine-driver clock API expectations.

Test signals: compile coverage and machine-driver hw_params calling the I2S sysclk API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-pcm.c

Purpose: registers the PXA2xx PCM platform component that exposes pxa2xx-lib PCM callbacks to ASoC.

Important APIs/types/functions: `pxa2xx_soc_platform` sets `.legacy_dai_naming = 1`; probe calls `devm_snd_soc_register_component`.

Control flow: platform driver `pxa-pcm-audio` registers the component at probe time. Actual PCM operations live in shared `pxa2xx-lib` callbacks used by CPU DAI components.

State and persistence: no driver-private state; component lifecycle is devm-managed.

Dependencies and integration: selected by `SND_PXA2XX_SOC`, provides the platform component used with PXA AC97/I2S/SSP paths.

Risks: this is a thin registration shim; missing probe means old machine drivers depending on `pxa-pcm-audio` will have no PCM platform. No OF match is present, so legacy platform-device creation is expected.

Test signals: platform device probe, ASoC component registration, and PXA machine drivers finding the PCM component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/pxa2xx-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/spitz.c -->
# sources/distributed-fs/ceph-client/sound/soc/pxa/spitz.c

Purpose: implements the Sharp Zaurus Spitz/Borzoi/Akita machine driver using PXA2xx I2S and WM8750 codec, with GPIO-controlled jack/speaker/mic routing.

Important APIs/types/functions: global state stores selected jack and speaker functions plus mic and mute GPIO descriptors. Key functions are `spitz_ext_control`, `spitz_startup`, `spitz_hw_params`, user controls `spitz_get/set_jack` and `spitz_get/set_spk`, `spitz_mic_bias`, and `spitz_probe`.

Control flow: probe rejects non-Spitz/Borzoi/Akita machines, gets GPIOs, initializes default jack/speaker states, and registers a static ASoC card. Startup prevents capture when headphone-only mode is selected. hw_params sets WM8750 and PXA I2S sysclk to `SPITZ_AUDIO_CLOCK`. User mixer controls update DAPM pins and GPIO mute/mic-bias state.

State and persistence: jack/speaker mode is global static process state. GPIO outputs persist hardware mute and mic-bias control. ASoC DAPM pins reflect current route selection.

Dependencies and integration: depends on mach type checks, GPIO consumer API, WM8750 codec, PXA2xx I2S sysclk ID, and legacy platform alias `spitz-audio`.

Risks: global static card/state prevents multiple instances. Board detection uses legacy `machine_is_*` macros. GPIO polarity must match board wiring or audio routes mute incorrectly. Capture is mode-dependent and can return `-EINVAL`.

Test signals: probe on each supported Zaurus model, mixer controls for jack/speaker modes, headphone/speaker mute GPIO behavior, mic bias event behavior, and playback/capture routing through WM8750.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/pxa/spitz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/Kconfig

Purpose: defines Qualcomm ASoC build options for LPASS CPU/platform/HDMI/CDC DMA, board machine drivers, QDSP6 DSP stack, SoundWire helpers, and offload utilities.

Important APIs/types/functions: root `SND_SOC_QCOM` depends on `ARCH_QCOM || COMPILE_TEST`. LPASS symbols select `REGMAP_MMIO`; SoC variants select CPU/platform/HDMI/CDC pieces. Machine drivers such as `SND_SOC_APQ8016_SBC` and `SND_SOC_MSM8996` select common helpers and QDSP6 dependencies.

Control flow: Kconfig dependencies determine which platform and machine objects are compiled and which lower-level DSP/clock/codec dependencies are selected.

State and persistence: build-time configuration only.

Dependencies and integration: feeds `qcom/Makefile` and ensures APR, COMMON_CLK, I2C, SOUNDWIRE, codec, and helper selections for each board family.

Risks: complex select chains can hide missing runtime dependencies. Several machine drivers require QDSP6/APR and SoundWire; incorrect dependencies cause build or probe failures. Indentation in the QDSP6 USB block is unusual but syntactically meaningful to Kconfig.

Test signals: allmodconfig/allyesconfig, individual SoC defconfigs, dependency resolution for APR/SoundWire/I2C variants, and compile tests of LPASS-only versus QDSP6-backed cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/Makefile

Purpose: maps Qualcomm ASoC Kconfig symbols to platform, machine, common, offload, and QDSP6 subdirectory objects.

Important APIs/types/functions: builds LPASS CPU/CDC DMA/HDMI/platform/SoC-variant objects, machine drivers for APQ8016/APQ8096/SC/SDM/SM/X1E boards, `common.o`, SoundWire helpers, USB offload utils, and descends into `qdsp6/`.

Control flow: kernel build includes objects based on config symbols. Platform objects provide reusable exported symbols consumed by SoC-specific modules.

State and persistence: build-system object state only.

Dependencies and integration: aligned with `Kconfig`; LPASS APQ8016 object uses exported generic LPASS CPU probe/remove; machine drivers use `common.o` helpers.

Risks: object naming must match module aliases and Kconfig symbols. Missing common object selection causes unresolved machine helper references. QDSP6 subdirectory only builds under `CONFIG_SND_SOC_QDSP6`.

Test signals: modular and built-in builds for each Qualcomm SoC symbol and modpost coverage for exported LPASS/common symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/apq8016_sbc.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/apq8016_sbc.c

Purpose: implements APQ8016 SBC and MSM8916 QDSP6 machine-driver setup for MI2S routing, jack detection, backend ops, and sound-card registration.

Important APIs/types/functions: `struct apq8016_sbc_data` stores card, IOMUX registers, jack, setup flag, and MI2S clock reference counts. Important functions are `apq8016_dai_init`, `apq8016_sbc_add_ops`, `msm8916_qdsp6_dai_init`, QDSP6 startup/shutdown, backend hw_params fixup, and probe.

Control flow: probe allocates card data, parses DAI links with `qcom_snd_parse_of`, maps mic/spkr IOMUX resources, stores drvdata, applies compatible-specific link ops, and registers the card. DAI init configures MI2S TLMM/IOMUX bits, creates headset jack once, sets button key mappings, sets codec MCLK, and attaches the jack to codecs. QDSP6 backend ops force 48 kHz stereo S16 and reference-count LPAIF bit clock enable per MI2S port.

State and persistence: IOMUX MMIO bits persist board routing; `jack_setup` avoids duplicate jack creation; `mi2s_clk_count[]` keeps shared backend bit clock balanced.

Dependencies and integration: depends on Qualcomm common OF parser, dt-bindings for APQ8016 LPASS/Q6AFE IDs, QDSP6 AFE IDs, codec jack support, and resources named `mic-iomux` and `spkr-iomux`.

Risks: reference counts are not explicitly locked. IOMUX writes are read-modify-write without regmap locking. `qdsp6_dai_get_lpass_id` must stay synchronized with QDSP6 DAI IDs. Default MCLK and fixed BE params may not suit nonstandard codecs.

Test signals: card probe for both compatibles, MI2S route playback/capture, jack insertion/button events, QDSP6 backend clock count balance across concurrent streams, and fixed BE hw_params negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/apq8016_sbc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/apq8096.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/apq8096.c

Purpose: implements the APQ8096/MSM8996 machine driver for QDSP6-based audio with WCD9335 clocking, jack setup, and backend parameter fixups.

Important APIs/types/functions: key functions are `apq8096_be_hw_params_fixup`, `msm_snd_hw_params`, `apq8096_init`, `apq8096_add_be_ops`, and platform probe. It uses `qcom_snd_parse_of` and `qcom_snd_wcd_jack_setup`.

Control flow: probe allocates an ASoC card, parses OF links, adds backend ops/fixups to `no_pcm` links, and registers the card. Runtime hw_params sets codec sysclk to the WCD9335 default MCLK. Init performs WCD jack setup for relevant runtime links. BE fixup forces 48 kHz stereo.

State and persistence: state is mostly ASoC card/link configuration and codec sysclk state; no large private structure is used.

Dependencies and integration: depends on QDSP6 stack, Qualcomm common helpers, WCD codec jack integration, COMMON_CLK, and the `qcom,apq8096-sndcard` compatible.

Risks: fixed 48 kHz stereo BE constraints may reject alternate topologies. WCD jack setup depends on codec component support. Probe relies on DT links being parseable by common helper.

Test signals: APQ8096 card registration, backend link ops attached, headset jack events, codec MCLK setting, and playback/capture through QDSP6 frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/apq8096.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/common.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/common.c

Purpose: provides shared Qualcomm machine-driver helpers for parsing DT sound cards and setting up WCD/DisplayPort jacks.

Important APIs/types/functions: exports `qcom_snd_parse_of`, `qcom_snd_wcd_jack_setup`, and `qcom_snd_dp_jack_setup`. It defines common jack widgets and headset jack pins.

Control flow: `qcom_snd_parse_of` reads card name/model, optional audio routing/widgets, allocates DAI links from DT children, parses CPU/platform/codec components, assigns names/stream names, and sets link flags. WCD jack setup creates a headset jack, maps button keys, and attaches it to codec components. DP jack setup creates a display/HDMI jack and attaches it to HDMI codec components.

State and persistence: parsed links and component arrays are devm-managed on the card device. Jack objects are stored in machine-driver private data passed by callers or codec components.

Dependencies and integration: used by Qualcomm machine drivers including APQ8016 and APQ8096. Depends on ASoC OF parsing, DAPM widgets/routes, jack APIs, and codec component jack callbacks.

Risks: DT parsing is topology-sensitive; malformed child nodes can produce partial card/link allocations. Link naming uses fixed-size buffers. Jack setup must handle codecs that return `-ENOTSUPP` while still propagating real failures.

Test signals: DT cards with multiple links/codecs/platforms, optional widgets/routing, headset button mapping, DP jack setup, and error paths for malformed OF nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/common.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/common.h

Purpose: declares shared Qualcomm ASoC machine-driver helper APIs and LPASS port sizing.

Important APIs/types/functions: defines `LPASS_MAX_PORT` as `SENARY_MI2S_TX + 1`. Declares `qcom_snd_parse_of`, `qcom_snd_wcd_jack_setup`, and `qcom_snd_dp_jack_setup`.

Control flow: no executable flow; machine drivers call these helpers during probe/runtime init.

State and persistence: no state in the header.

Dependencies and integration: includes QCOM LPASS dt-bindings so `LPASS_MAX_PORT` tracks DAI IDs. Used by APQ8016, APQ8096, and other Qualcomm cards.

Risks: `LPASS_MAX_PORT` depends on binding enum ordering; changes to dt-bindings can affect array sizing. Helper signatures must match common.c exports.

Test signals: compile coverage of all Qualcomm machine drivers and array bounds checks in users that size per-port state from `LPASS_MAX_PORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-apq8016.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-apq8016.c

Purpose: supplies APQ8016-specific LPASS CPU DAI definitions, register layout, clock initialization, and DMA channel allocation hooks for the generic LPASS CPU/platform code.

Important APIs/types/functions: defines `apq8016_lpass_cpu_dai_driver[]`, `apq8016_lpass_alloc_dma_channel`, `apq8016_lpass_free_dma_channel`, `apq8016_lpass_init`, `apq8016_lpass_exit`, and `apq8016_data` as `struct lpass_variant`.

Control flow: platform driver matches APQ8016 compatibles and delegates probe/remove to generic LPASS CPU functions. Variant init bulk-gets/enables PCNOC clocks, gets `ahbix-clk`, sets its rate, and enables it. DMA allocation chooses RDMA channels for playback and WRDMA channels for capture using a bitmap.

State and persistence: variant data is static. Runtime clock handles, clock bulk arrays, and DMA bitmap are stored in generic `struct lpass_data`.

Dependencies and integration: depends on APQ8016 LPASS dt-bindings, `lpass.h`, register macros, generic `asoc_qcom_lpass_cpu_platform_probe`, and LPASS platform PCM registration.

Risks: DAI names include historical spelling `"Quatenary"`, which may be ABI-visible. Bitmap allocation must match RDMA/WRDMA channel ranges. Clock enable errors must unwind bulk clocks correctly.

Test signals: APQ8016 LPASS probe, all four MI2S DAIs, playback/capture DMA allocation exhaustion, clock rate setup for `ahbix-clk`, and remove/shutdown clock disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-apq8016.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cdc-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cdc-dma.c

Purpose: implements LPASS codec DMA DAI operations for RXTX/VA CDC DMA paths used by newer Qualcomm audio macros.

Important APIs/types/functions: key helpers include `__lpass_get_dmactl_handle`, `__lpass_get_codec_dma_intf_type`, `__lpass_platform_codec_intf_init`, and DAI ops `lpass_cdc_dma_daiops_startup`, `shutdown`, `hw_params`, and `trigger`. Exports `asoc_qcom_lpass_cdc_dma_dai_ops`.

Control flow: startup enables codec memory clocks/resources for the selected DMA interface. hw_params initializes the correct RXTX or VA DMA interface register field, programs DMA control fields through variant regmap fields, and configures channel/format-related interface selection. Trigger enables or disables DMA based on ALSA trigger commands. Shutdown drops clocks/resources.

State and persistence: per-stream DMA control handles are resolved from `struct lpass_data` and variant mappings. Codec memory clock state persists while streams are active.

Dependencies and integration: depends on LPASS register macros, `is_cdc_dma_port`, variant DMA field definitions, codec memory clocks parsed by `lpass-cpu.c`, and LPASS platform PCM code.

Risks: DAI ID to interface mapping is critical and easy to break as bindings grow. Clock/resource enablement must stay balanced across startup failures and trigger errors. CDC DMA register maps differ between RXTX and VA regions.

Test signals: startup/hw_params/trigger for RX, TX, and VA CDC DMA ports, interface register programming, codec memory clock rates/enables, and DMA capture/playback with period interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cdc-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cpu.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cpu.c

Purpose: implements the generic Qualcomm LPASS CPU DAI driver and platform probe support for MI2S, HDMI, and CDC DMA-capable variants.

Important APIs/types/functions: DAI ops are exported as `asoc_qcom_lpass_cpu_dai_ops` and `_ops2`. Major helpers include `lpass_cpu_init_i2sctl_bitfields`, MI2S startup/shutdown/hw_params/prepare/trigger, regmap access filters for CPU/HDMI/RXTX/VA maps, `lpass_hdmi_init_bitfields`, OF SD-line parsing, CDC clock parsing, `asoc_qcom_lpass_cpu_platform_probe`, remove, and shutdown.

Control flow: probe rejects devices where `qcom,adsp` owns audio resources, allocates `lpass_data`, loads variant data, parses child DAI nodes for HDMI/CDC enablement and MI2S SD-line masks, maps LPASS MMIO regions, initializes regmaps, runs variant init, obtains MI2S clocks, allocates I2SCTL regmap fields, initializes HDMI fields if needed, registers CPU DAIs, and registers the LPASS platform. Runtime MI2S startup prepares OSR/BIT clocks; hw_params programs bit width, SD-line mode, mono/stereo, and bit clock rate; prepare/trigger manage LRCLK/BCLK and speaker/mic enable fields.

State and persistence: `struct lpass_data` persists variant pointers, regmaps, regmap fields, clocks, SD-line modes, HDMI/CDC flags, prepared-clock booleans, and DMA maps. Register caches are flat regmap caches with volatile current pointer/IRQ status registers.

Dependencies and integration: central integration point for `lpass.h`, LPASS register macros, SoC variant drivers, LPASS platform PCM, HDMI/CDC DAI ops, DT child nodes, and common clock/regmap frameworks.

Risks: complex clock balancing between prepare, trigger, shutdown, and suspend paths; shared BCLK use requires careful enable counts. OF SD-line parsing defaults to 8-channel compatibility and can mask DT omissions. Regmap readable/writeable filters must match variant register ranges exactly. Probe mutates variant DAI channel limits for quad modes, which can affect static variant data.

Test signals: probe for APQ8016/SC variants with and without HDMI/CDC nodes, MI2S playback/capture for 1/2/4/6/8 channels, SD-line DT validation, clock enable-count tests across pause/suspend/resume, regmap access warnings, and platform PCM DMA operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.c

Purpose: implements LPASS HDMI/DisplayPort DAI operations for configuring HDMI audio metadata, channel status, stream format, and RDMA start/stop.

Important APIs/types/functions: key DAI ops are `lpass_hdmi_daiops_hw_params`, `lpass_hdmi_daiops_prepare`, and `lpass_hdmi_daiops_trigger`, exported as `asoc_qcom_lpass_hdmi_dai_ops`.

Control flow: hw_params configures HDMI TX control reset/legacy bits, stream enable and metadata fields, channel allocation/status/user bits, parity calculation, and DMA channel metadata based on PCM params. Prepare primes HDMI/DP metadata before stream start. Trigger enables or disables the HDMI RDMA path on START/RESUME/PAUSE_RELEASE and STOP/SUSPEND/PAUSE_PUSH.

State and persistence: HDMI-specific regmap fields allocated in `lpass-cpu.c` are stored in `struct lpass_data` and persist across stream operations. Runtime register state includes channel status, user bits, metadata, stream enable, and DMA control.

Dependencies and integration: depends on LPASS HDMI register field setup from `lpass_hdmi_init_bitfields`, LPASS platform DMA allocation, ASoC DAI framework, and DP/HDMI machine-driver routes.

Risks: channel-status metadata must match PCM parameters or sinks may reject audio. HDMI register fields are variant-specific; missing field allocation causes runtime failures. Trigger must synchronize with RDMA setup/teardown to avoid underruns.

Test signals: HDMI/DP playback at supported sample rates/formats/channels, sink channel-status validation, RDMA trigger start/stop, suspend/resume, and jack/ELD integration in machine drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.c -->
