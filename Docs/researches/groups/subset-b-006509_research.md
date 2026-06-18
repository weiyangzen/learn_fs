# Research: subset-b-006509

Grouped research for ALSA SoC generic card helpers plus Google, Hisilicon, Imagination, and Intel ASoC build glue under `sources/distributed-fs/ceph-client/sound/soc`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2-custom-sample.c -->
# sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2-custom-sample.c

Purpose: sample platform driver showing how a custom card can embed `struct simple_util_priv`, reuse `audio_graph2_parse_of()`, override graph-card2 hooks, and replace DAI link ops/card probe behavior. It is documentation-by-code for board-specific customization of `audio-graph-card2`.

Important APIs/types/functions: `struct custom_priv` wraps `simple_util_priv`; `simple_to_custom()` recovers the wrapper; `custom_hooks` provides `.hook_pre`, `.hook_post`, `.custom_normal`, `.custom_dpcm`, and `.custom_c2c`; `custom_ops` overrides startup while reusing `simple_util_shutdown()` and `simple_util_hw_params()`. `custom_probe()` allocates private data, sets a short card name, and delegates OF parsing to `audio_graph2_parse_of()`.

Control flow: platform probe allocates `custom_priv`, initializes `simple_priv->ops`, then calls the generic graph parser. The parser invokes `custom_hook_pre()` before link discovery, the custom link callbacks around each graph link type, and `custom_hook_post()` after parsing. The post hook replaces `card->probe` with `custom_card_probe()`, which sets an example custom parameter and then calls `graph_util_card_probe()` for jack initialization.

State and persistence: all state is devm-managed and tied to the platform device. The only custom state is `custom_params`, set to `1` at card probe time. Runtime stream state is handled by the shared simple-card utilities.

Dependencies/integration: depends on `sound/graph_card.h`, generic graph-card2 exported functions, ASoC card registration performed by `audio_graph2_parse_of()`, and the compatible string `audio-graph-card2-custom-sample`.

Risks: this sample trusts the generic parser for all allocation and registration; a real custom driver would need stricter validation around hook side effects. `custom_startup()` logs then delegates, so it must preserve the shared startup error semantics. The sample compatible is intentionally long and the actual card name is shortened, which can surprise tests that match names.

Test signals: useful smoke tests are module probe with a minimal audio graph DT, log verification that pre/post/link hooks ran, and playback/capture startup confirming custom ops call through to shared clock setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2-custom-sample.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2.c -->
# sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2.c

Purpose: generic ASoC machine driver for `audio-graph-card2` DT bindings. It converts OF graph links into `snd_soc_dai_link` arrays for normal CPU-codec links, DPCM front/back ends, codec-to-codec links, and multi-CPU/multi-codec topologies.

Important APIs/types/functions: `enum graph_type` classifies graph nodes; exported `audio_graph2_link_normal()`, `audio_graph2_link_dpcm()`, `audio_graph2_link_c2c()`, and `audio_graph2_parse_of()` are the public extension points. Internal helpers include `graph_get_type()`, `graph_get_next_multi_ep()`, `graph_parse_node()`, `graph_parse_daifmt()`, `graph_parse_bitframe()`, `graph_link_init()`, `graph_count_*()`, and `graph_for_each_link()`. `struct graph2_custom_hooks` allows external hook/callback substitution.

Control flow: probe allocates `simple_util_priv` and calls `audio_graph2_parse_of()`. Parsing sets card metadata, runs optional pre hook, walks the DT `links` phandle list once to count link component cardinalities, allocates arrays via `simple_util_init_priv()`, parses amplifier GPIO/widgets/routing, walks `links` again to populate each DAI link, parses card name and aux devices, then registers the card. Link parsing resolves endpoints, remote endpoints, TDM, clocks, dai names, DAI formats, direction flags, `mclk-fs`, trigger order, and shared ops.

State and persistence: persistent driver state is devm-allocated inside `simple_util_priv`: DAI links, properties, DAIs, DLCs, codec conf, optional PA GPIO, and card drvdata. Runtime stream state is not stored here; the shared ops in simple-card-utils manage clock enable/disable and hw_params. Device-node references are held in link components and released by `simple_util_remove()`.

Dependencies/integration: depends on OF graph APIs, `sound/graph_card.h`, `simple-card-utils`, ASoC DAI/component lookup, GPIO descriptors, and DT properties such as `links`, `routing`, `widgets`, `mclk-fs`, `playback-only`, `capture-only`, bit/frame master flags, and trigger order. It exports symbols used by the custom sample and potential custom machine drivers.

Risks: multi-endpoint mapping is sensitive to OF graph shape; invalid N:M mappings return `-EINVAL`, and the code relies on ordered `port@id` lookup for overlay stability. Reference handling is complex around `__free(device_node)` plus manual `of_node_put()`. `graph_link_init()` parses `port_cpu` trigger order twice and never explicitly parses `port_codec` in that duplicated slot, which is a potential copy/paste defect. `graph_count_c2c()` uses nested `of_node_get()` calls and should be watched for reference balance. DTs with too many links hit `SNDRV_MAX_LINKS`.

Test signals: compile coverage with `CONFIG_SND_AUDIO_GRAPH_CARD2`; DT overlay tests for normal, DPCM, codec-to-codec, 1:N/N:M multi links; probe/unprobe leak checks; runtime tests for `mclk-fs`, trigger order, link direction, and auto-selectable format negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/audio-graph-card2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/simple-card-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/generic/simple-card-utils.c

Purpose: shared helper library for generic simple-card and audio-graph-card drivers. It centralizes DT parsing, DAI link allocation, clock/TDM setup, conversion constraints, jack helpers, codec-to-codec defaults, and cleanup.

Important APIs/types/functions: exported helpers include `simple_util_parse_convert()`, `simple_util_is_convert_required()`, `simple_util_parse_daifmt()`, `simple_util_parse_tdm_width_map()`, `simple_util_set_dailink_name()`, `simple_util_parse_card_name()`, `simple_util_parse_clk()`, `simple_util_startup()`, `simple_util_shutdown()`, `simple_util_hw_params()`, `simple_util_be_hw_params_fixup()`, `simple_util_dai_init()`, canonicalization helpers, widget/routing/pin/jack parsers, `simple_util_init_priv()`, `simple_util_remove()`, `graph_util_card_probe()`, `graph_util_parse_dai()`, link direction, and trigger-order parsing.

Control flow: probe users first count link component cardinalities, call `simple_util_init_priv()` to allocate contiguous link/property/DAI/DLC arrays, then fill those arrays. At PCM startup, clocks are enabled for all CPU and codec DAIs and fixed sysclk constraints are applied. At hw_params, `mclk-fs` drives clock rate programming and `snd_soc_dai_set_sysclk()`, then TDM slot maps are applied. Shutdown reverses non-fixed sysclk and disables clocks. DAI init programs static sysclk/TDM and auto-populates codec-to-codec params when all runtime components are codecs.

State and persistence: `simple_util_priv` owns devm arrays for DAI links, DAI props, DAIs, link components, codec conf, optional aux jacks, and GPIO jack state. `simple_util_data` stores requested convert-rate/channels/sample-format and is used during DPCM BE fixup. Clocks and OF nodes remain associated with DAI props until card removal.

Dependencies/integration: depends on ASoC core, OF/OF graph parsing, common clock framework, GPIO consumer API, jack helpers, PCM params, and DT bindings from `dt-bindings/sound/audio-graph.h`. It is the shared dependency for `simple-card.c`, `audio-graph-card2.c`, and custom graph-card drivers.

Risks: clock enable error unwinding must stay aligned with loop indices; fixed sysclk plus `mclk-fs` rejects non-divisible rates at startup. DAI lookup has two paths, direct DAI args and fallback DLC resolution, and mishandled node references can leak or underflow. `graph_util_parse_trigger_order()` uses a static local `order`, which is harmless for sequential use but unnecessary shared state. Conversion sample format parsing accepts only a small string table.

Test signals: unit-like DT probes for convert properties, TDM width maps, fixed clocks, missing/legacy clock provider flags, jack GPIOs, aux jack components, and codec-to-codec links. Runtime PCM tests should verify startup failure unwinds all clocks and hw_params applies sysclk/TDM in CPU-first and codec-first modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/simple-card-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/simple-card.c -->
# sources/distributed-fs/ceph-client/sound/soc/generic/simple-card.c

Purpose: generic `simple-audio-card` / `simple-scu-audio-card` machine driver. It parses either DT-described simple card links or legacy platform data into ASoC card/link structures and registers the card.

Important APIs/types/functions: `simple_probe()` is the platform entry point; `simple_get_dais_count()`, `simple_count_noml()`, and `simple_count_dpcm()` size allocations; `simple_parse_of()` handles widgets/routing/pin switches/aux devices; `simple_for_each_link()` and `__simple_for_each_link()` iterate CPU/codec child nodes; `simple_dai_link_of()` handles normal links; `simple_dai_link_of_dpcm()` handles DPCM FE/BE links. `simple_ops` delegates stream ops to simple-card-utils.

Control flow: probe allocates private/card state, counts DAI links, initializes arrays with `simple_util_init_priv()`, then parses DT if present. DT parsing loops CPU-side first and codec-side second to keep stable DPCM numbering. Normal links parse CPU, codec, optional platform, canonicalize CPU/platform, set format/direction/trigger/mclk, and name the link. DPCM links create dynamic FE CPU-dummy links or no-PCM BE dummy-CPU links, parse conversion properties, and attach BE fixups. Legacy platform data fills one link directly.

State and persistence: per-card state is devm-managed in `simple_util_priv`. Link properties persist in `simple_dai_props`; DPCM codec prefixes are stored in codec conf. Additional devices under `simple-audio-card,additional-devs` are populated and depopulated by a devm action.

Dependencies/integration: integrates with `sound/simple_card.h`, `sound/soc-dai.h`, `simple-card-utils`, OF platform population, and DT properties prefixed with `simple-audio-card,`. It can select DPCM behavior only for the `simple-scu-audio-card` compatible via match data.

Risks: DPCM selection is heuristic: many child nodes or convert properties switch behavior, so malformed DT can produce unexpected FE/BE splits. The iterator treats child counts and additional-devs specially; changes to binding layout can affect parsing. Legacy platform-data path requires many non-null fields and has less validation than DT path. Link count must not exceed `SNDRV_MAX_LINKS`.

Test signals: DT probe tests for old top-level syntax, new `dai-link` nodes, optional `plat`, `additional-devs`, `aux-devs`, DPCM conversion, routing/widgets/pin-switches, and legacy platform-data fallback. Runtime tests should verify stable PCM numbering for multi-link DPCM cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/simple-card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/test-component.c -->
# sources/distributed-fs/ceph-client/sound/soc/generic/test-component.c

Purpose: synthetic ASoC component/DAI platform driver for testing simple-card and audio-graph-card topologies. It can act as CPU or codec and optionally exposes verbose component and DAI callbacks.

Important APIs/types/functions: `struct test_priv`, `struct test_adata`, DAI ops `test_ops`/`test_verbose_ops`, component callbacks, synthetic PCM callbacks, `test_driver_probe()`, and compatible strings such as `test-cpu`, `test-codec`, and verbose variants. It declares wide dummy PCM capabilities and auto-selectable DAI formats.

Control flow: probe gets match data, counts OF graph endpoints, allocates component driver, one DAI driver per graph port, and name storage. CPU mode enables PCM buffer/pointer/trigger behavior and legacy DAI naming; codec mode marks `endianness` so utilities identify it as a codec. Each graph port becomes a playback/capture DAI. Component registration exposes optional verbose callbacks depending on match data.

State and persistence: per-device state includes dynamic DAI/component descriptors, generated names, optional active substream, and delayed work. Trigger start schedules periodic work that calls `snd_pcm_period_elapsed()`; trigger stop clears the substream and cancels work. Managed allocations tie state to platform device lifetime.

Dependencies/integration: depends on OF graph endpoint layout, ASoC component/DAI registration, delayed workqueue, and PCM managed buffer APIs. It is an integration test peer for generic machine drivers and graph bindings.

Risks: `test_component_pointer()` uses a static pointer shared by all instances/substreams, which is fine for a test stub but not per-device-safe. The delayed work continuously reschedules every 10 ms while active, so trigger stop and remove ordering matter. It logs heavily in verbose modes. Probe rejects nodes with zero endpoints.

Test signals: instantiate with CPU and codec compatible strings in graph DTs; verify DAI format logs, TDM slot logs, automatic format selection, PCM period callbacks, DAPM IN/OUT routes, and verbose component lifecycle callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/generic/test-component.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/google/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/google/Kconfig

Purpose: Kconfig menu for Google ASoC platform support. It currently exposes one tristate option, `SND_SOC_CHV3_I2S`, for the Chameleon v3 I2S device.

Important APIs/types/functions: build-time symbol `SND_SOC_CHV3_I2S`; user-facing prompt "Google Chameleon v3 I2S device".

Control flow: when selected as built-in or module, the corresponding Makefile compiles `chv3-i2s.o`.

State and persistence: no runtime state; only kernel configuration state.

Dependencies/integration: no explicit dependencies are declared here, so broader ASoC menu context must ensure sound/ASoC prerequisites. Integrates with `sound/soc/google/Makefile`.

Risks: lack of explicit dependencies can permit compile-test combinations that rely on outer menu constraints. Help text is minimal and gives no DT compatible or platform prerequisites.

Test signals: Kconfig coverage should verify `CONFIG_SND_SOC_CHV3_I2S=m/y` includes `chv3-i2s.o` and that unset excludes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/google/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/google/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/google/Makefile

Purpose: build glue for Google ASoC platform drivers.

Important APIs/types/functions: maps `obj-$(CONFIG_SND_SOC_CHV3_I2S)` to `chv3-i2s.o`.

Control flow: kbuild includes `chv3-i2s.c` only when the Kconfig symbol is enabled.

State and persistence: no runtime state.

Dependencies/integration: coupled to `google/Kconfig` and the source object name.

Risks: object list has no aggregate library; additional Google drivers must be appended carefully.

Test signals: inspect built objects for enabled/disabled `CONFIG_SND_SOC_CHV3_I2S`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/google/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/google/chv3-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/google/chv3-i2s.c

Purpose: ASoC component/DAI and custom PCM implementation for the Google Chameleon v3 I2S interface, backed by MMIO ring-buffer registers and a shared IRQ block.

Important APIs/types/functions: `struct chv3_i2s_dev` stores register bases, active substreams, and TX fetch size. DAI capabilities support 1-128 channels, continuous 8-96 kHz, S32_LE. PCM callbacks include `chv3_dma_open()`, `close()`, `pcm_new()`, `hw_params()`, `prepare()`, `pointer()`, and `ack()`. `chv3_i2s_isr()` reports periods. `chv3_i2s_probe()` maps resources, requests IRQ, and registers the component.

Control flow: probe maps two MMIO regions, reads TX IRQ constant, registers an IRQ handler, then registers one DAI/component. PCM open sets hardware constraints and stores the active RX/TX substream. `pcm_new()` allocates maximum-size managed DMA buffers manually. Prepare resets RX or TX, writes DMA base/size/IRQ period registers, enables the stream, and unmasks IRQs. ALSA ack writes consumer/producer indices from `appl_ptr`; pointer reads hardware producer/consumer index and lags playback by one frame to avoid full-buffer deadlock.

State and persistence: runtime state is active RX/TX substream pointers and `tx_bytes_to_fetch`. Hardware state consists of ring base/size, producer/consumer indices, enables, reset bits, and IRQ masks. Buffers are allocated per PCM substream and retained by ALSA until device teardown.

Dependencies/integration: depends on two platform MMIO resources, one IRQ, ASoC component registration, ALSA DMA buffer allocation, and DT compatible `google,chv3-i2s`. It does not use dmaengine; hardware directly consumes physical DMA buffer addresses.

Risks: ISR calls `snd_pcm_period_elapsed()` on stored substream pointers without null checks, relying on IRQ masking/stream lifecycle. `frame_bytes` is computed as `runtime->frame_bits * 8`, which appears dimensionally suspect because ALSA frame bits normally convert to bytes by dividing by 8; this may affect playback pointer lag. Manual DMA allocation must fit hardware address width. TX IRQ period divides by `tx_bytes_to_fetch`, so a zero or unexpected hardware constant would fault or misprogram.

Test signals: hardware or emulator tests for ring index wraparound, playback full-buffer behavior, ack/pointer monotonicity, IRQ period generation, open/close races, and max buffer allocation. Static tests should flag null substream ISR paths and frame-size arithmetic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/google/chv3-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/hisilicon/Kconfig

Purpose: Kconfig menu for Hisilicon ASoC platform support.

Important APIs/types/functions: `SND_I2S_HI6210_I2S` tristate selects `SND_SOC_GENERIC_DMAENGINE_PCM`.

Control flow: enabling the symbol builds the HI6210 I2S controller driver and ensures generic dmaengine PCM support.

State and persistence: compile-time configuration only.

Dependencies/integration: paired with `hisilicon/Makefile`; broader sound menu supplies ASoC dependencies.

Risks: help text is terse and does not mention required clocks/syscon/DT compatible. The config symbol lacks architecture gating, so compile-test coverage may depend on all included headers being portable.

Test signals: kbuild with `CONFIG_SND_I2S_HI6210_I2S=m/y` should build `hi6210-i2s.o` and select generic DMA engine PCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/hisilicon/Makefile

Purpose: kbuild mapping for Hisilicon ASoC platform driver objects.

Important APIs/types/functions: maps `obj-$(CONFIG_SND_I2S_HI6210_I2S)` to `hi6210-i2s.o`.

Control flow: object inclusion follows the Kconfig tristate.

State and persistence: no runtime state.

Dependencies/integration: coupled to `hisilicon/Kconfig` and `hi6210-i2s.c`.

Risks: minimal build file; future drivers need explicit object mapping.

Test signals: enabled symbol should produce the driver object; disabled symbol should omit it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/hi6210-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/hisilicon/hi6210-i2s.c

Purpose: ASoC CPU DAI driver for the Hisilicon HI6210 I2S S2/BT interface, using MMIO codec/I2S registers, sysctrl regmap clock/reset gates, and dmaengine PCM.

Important APIs/types/functions: `struct hi6210_i2s` stores clocks, sysctrl, base addresses, DMA data, stream format state, and a spinlock. DAI ops are `hi6210_i2s_startup()`, `shutdown()`, `set_fmt()`, `hw_params()`, `trigger()`, and DAI probe. Probe maps registers, gets syscon and clocks, registers dmaengine PCM and ASoC component.

Control flow: startup deasserts resets, enables clocks, sets the I2S base rate to 49.152 MHz, enables sysctrl gates, masks I2S IRQs, resets FIFOs, configures routing/muxes, and releases software reset. `set_fmt()` validates master/slave and I2S/left/right-justified formats and stores it. `hw_params()` validates sample format/rate/channels, configures FIFO thresholds, clock enables, mixers, format bits, DMA address/width/burst, frame mode, data signedness, and master-mode sample-rate fields. Trigger toggles S2 RX/TX enable bits under spinlock. Shutdown disables clocks and asserts reset.

State and persistence: runtime state includes selected format, master flag, rate, channels, bits, channel length, and DMA data for playback/capture. Hardware register state is reprogrammed per startup/hw_params. Clocks and sysctrl references persist for device lifetime.

Dependencies/integration: depends on common clock framework, syscon regmap phandle `hisilicon,sysctrl-syscon`, clocks `dacodec` and `i2s-base`, dmaengine PCM, and DT compatible `hisilicon,hi6210-i2s`. Register definitions come from `hi6210-i2s.h`.

Risks: supported DAI declaration advertises only stereo 48 kHz 16-bit signed/unsigned, while `hw_params()` contains cases for 8-192 kHz and 24-bit, so reachable behavior depends on constraints from the machine driver/core. It uses `dma_data->addr_width = 3` for 24-bit, which DMA engines may not accept universally. Startup has many hard-coded sysctrl bits and assumes BT/S2 routing. Capture path sets DMA address but much register setup appears playback/downlink oriented.

Test signals: boot/probe on HI6210/HI6220 DT, clk/reset/syscon error injection, playback/capture at advertised 48 kHz 16-bit, trigger toggling, dmaengine slave config, and register trace comparison for master/slave and justified formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/hi6210-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/hi6210-i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/hisilicon/hi6210-i2s.h

Purpose: register offset, bit-field, and enum definitions for the HI6210 I2S/audio codec block used by `hi6210-i2s.c`.

Important APIs/types/functions: defines offsets such as `HII2S_SW_RST_N`, `HII2S_IF_CLK_EN_CFG`, `HII2S_FS_CFG`, `HII2S_I2S_CFG`, FIFO threshold registers, IRQ registers, channel FIFOs, and bit masks/shifts for word length, clocks, mixers, sample-rate selectors, and S2 I2S format. Enums describe supported word sizes, sample-rate encodings, I2S formats, gains, and SRC modes.

Control flow: no executable control flow; constants are consumed by register read/modify/write sequences in the C driver.

State and persistence: represents hardware register layout; no software state.

Dependencies/integration: included only by `hi6210-i2s.c`; uses `BIT()` macro from Linux headers included by the C file before this header.

Risks: many bit definitions are hardware-specific and unvalidated at compile time. Incorrect masks/shifts silently corrupt adjacent hardware fields. The header includes registers unused by the current driver, which can invite assumptions about unimplemented S1/S3/voice paths.

Test signals: hardware register trace tests, build coverage for all macros used in `hi6210-i2s.c`, and comparison against vendor TRM definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/hisilicon/hi6210-i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/img/Kconfig

Purpose: Kconfig menu for Imagination Technologies ASoC platform and codec drivers, gated to MIPS or compile-test builds.

Important APIs/types/functions: options `SND_SOC_IMG_I2S_IN`, `SND_SOC_IMG_I2S_OUT`, `SND_SOC_IMG_PARALLEL_OUT`, `SND_SOC_IMG_SPDIF_IN`, `SND_SOC_IMG_SPDIF_OUT`, and `SND_SOC_IMG_PISTACHIO_INTERNAL_DAC`. The digital interface drivers select `SND_SOC_GENERIC_DMAENGINE_PCM`.

Control flow: selected symbols drive object inclusion in the IMG Makefile.

State and persistence: configuration-time only.

Dependencies/integration: depends on `MIPS || COMPILE_TEST`; each option maps to a platform driver or codec driver.

Risks: DAC option does not select regulator/syscon dependencies because those are framework-level dependencies assumed elsewhere. Help text is platform-generic and does not include compatible strings.

Test signals: kconfig matrix for each symbol as module/built-in, especially compile-test on non-MIPS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/img/Makefile

Purpose: kbuild mapping for Imagination ASoC drivers.

Important APIs/types/functions: maps six Kconfig symbols to `img-i2s-in.o`, `img-i2s-out.o`, `img-parallel-out.o`, `img-spdif-in.o`, `img-spdif-out.o`, and `pistachio-internal-dac.o`.

Control flow: each driver object is compiled independently when its config is enabled.

State and persistence: no runtime state.

Dependencies/integration: paired with `img/Kconfig` and the driver source files in the same directory.

Risks: no aggregate object; object names must track source file names exactly.

Test signals: kbuild object inclusion for each config symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-in.c -->
# sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-in.c

Purpose: ASoC CPU DAI driver for the Imagination I2S input controller, using dmaengine PCM and runtime/system PM.

Important APIs/types/functions: `struct img_i2s_in` stores MMIO base, sys clock, DMA data, max/active channel pairs, channel register base, DAI driver, and suspend snapshots. DAI ops include trigger, hw_params, set_fmt, and DAI probe. Custom DMA config sets source burst based on channel count.

Control flow: probe maps registers, reads `img,i2s-channels`, computes channel register base, enables runtime PM, initializes/reset hardware, allocates suspend register storage, registers component and dmaengine PCM. `set_fmt()` resumes PM, disables active channels, applies inversion and I2S/left-justified format bits across channels, then restores enables. `hw_params()` validates even channel count and S16/S24/S32 formats, checks sys clock versus bit clock, programs global/channel packing/filter settings, flushes FIFOs, and enables active channels. Trigger toggles the master enable bit.

State and persistence: state tracks `active_channels`, `max_i2s_chan`, DMA FIFO address/width, and register snapshots for system sleep. Runtime PM controls the sys clock. Hardware channel registers persist until reset or suspend/resume restore.

Dependencies/integration: requires platform MMIO resource, `img,i2s-channels`, optional reset `rst`, clock `sys`, dmaengine PCM, and DT compatible `img,i2s-in`.

Risks: channel count must be even and within hardware range; bad DT can move `channel_base` incorrectly. Optional top-level reset fallback relies on manual disable of existing state. `pm_runtime_put()` is used without autosuspend; clock churn may be visible in repeated set_fmt calls. Clock-rate filter thresholds must match hardware tolerances.

Test signals: probe with/without reset, capture for S16/S24/S32 and multiple channel pairs, sys-clock insufficiency rejection, suspend/resume register restore, and dmaengine slave config burst sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-out.c -->
# sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-out.c

Purpose: ASoC CPU DAI driver for the Imagination I2S output controller, supporting multi-channel S32_LE playback through dmaengine PCM.

Important APIs/types/functions: `struct img_i2s_out` contains MMIO, sys/ref clocks, reset, DMA data, active/max channel count, force-clock flag, DAI driver, and suspend snapshots. Key functions are runtime PM callbacks, `img_i2s_out_reset()`, DAI trigger/hw_params/set_fmt/probe, DMA prepare callback, and platform probe/remove/suspend/resume.

Control flow: probe maps resources, gets channel count, reset and clocks, allocates suspend storage, resumes PM, initializes global/channel registers, resets hardware, sets DMA data, registers component and dmaengine PCM. `set_fmt()` programs master/slave, continuous/gated clock, inversion, and I2S/left-justified channel timing under PM. `hw_params()` accepts only S32_LE, chooses a ref clock near rate*256 or rate*384, programs clock selector and active channel count, and enables the requested channel lanes. Trigger start enables clock/data; stop resets the block while preserving selected config.

State and persistence: persistent driver state includes `force_clk_active`, `active_channels`, DMA FIFO info, and saved registers. Runtime PM enables/disables sys and ref clocks. Reset sequencing rewrites saved channel/global config.

Dependencies/integration: requires MMIO, `img,i2s-channels`, reset `rst`, clocks `sys` and `ref`, dmaengine PCM, and DT compatible `img,i2s-out`.

Risks: only S32_LE is supported despite hardware format fields; machine drivers must constrain formats. `clk_set_rate()` return is ignored after selecting the rounded rate, relying on later `clk_get_rate()` to infer actual clock. Reset on stop can be disruptive if another stream/shared clock existed. Channel base calculation depends on power-of-two rounded max channel count.

Test signals: playback across supported rates/channel counts, continuous clock mode, master/slave and inversion combinations, stop/reset/restart cycles, suspend/resume restore, and DMA destination burst scaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-i2s-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-parallel-out.c -->
# sources/distributed-fs/ceph-client/sound/soc/img/img-parallel-out.c

Purpose: ASoC CPU DAI driver for Imagination parallel audio output, using dmaengine PCM for stereo S24/S32 playback.

Important APIs/types/functions: `struct img_prl_out` stores MMIO, sys/ref clocks, reset, DMA FIFO data, and device pointer. DAI ops are trigger, hw_params, set_fmt, and DAI probe. Runtime PM callbacks control the ref clock while the sys clock is enabled for the device lifetime after probe.

Control flow: probe maps registers, gets reset and clocks, enables sys clock, initializes edge mode, resets hardware, enables runtime PM, sets DMA FIFO parameters, and registers component plus dmaengine PCM. `hw_params()` validates stereo S24/S32, sets ref clock to rate*256, and toggles high-packing for S32. `set_fmt()` allows normal bit clock with normal or inverted frame and writes edge selection under PM. Trigger start sets module enable; stop resets hardware while preserving non-enable bits.

State and persistence: minimal state; hardware control register holds format/edge/enable bits. Runtime PM only gates `clk_ref`; sys clock is explicitly disabled on remove or error.

Dependencies/integration: needs MMIO, reset `rst`, clocks `sys` and `ref`, dmaengine PCM, and DT compatible `img,parallel-out`.

Risks: `clk_set_rate()` return is ignored. Only stereo is supported. Sys clock is not part of runtime PM suspend/resume and remains enabled while the device is bound. Reset must preserve control bits correctly across stop.

Test signals: stereo S24/S32 playback, frame inversion format tests, trigger stop/start reset behavior, runtime PM ref-clock gating, and error paths after sys clock enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-parallel-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-in.c -->
# sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-in.c

Purpose: ASoC CPU DAI driver for Imagination SPDIF input with dmaengine PCM, IEC958 status controls, configurable lock thresholds, and single/multiple frequency acquisition modes.

Important APIs/types/functions: `struct img_spdif_in` stores MMIO, sys clock, DMA data, lock/tracking settings, frequency configuration, active flag, suspend snapshots, and cached write-only ACLKGEN registers. Helpers calculate clock generator values. DAI controls expose IEC958 status, multi-frequency acquire rates, lock frequency, TRK, and thresholds. DAI ops are trigger, hw_params, and probe.

Control flow: probe maps resources, gets sys clock, resumes PM, resets hardware via reset control or soft reset, initializes spinlock/default lock/TRK values, writes control register, registers component and dmaengine PCM. `hw_params()` accepts stereo S32_LE and programs single-rate clock generation. Mixer controls can program multi-rate clock generators while inactive. Trigger start sets SRT and single/multi SRD mode under lock and marks active; stop clears SRT and active. Suspend saves readable registers and resume rewrites cached write-only aclkgen registers plus snapshots.

State and persistence: lock-protected state includes active/inactive, `multi_freq`, `single_freq`, `multi_freqs`, `trk`, lock thresholds, and cached ACLKGEN values. Runtime PM controls the sys clock. IEC958 status is read from hardware.

Dependencies/integration: requires MMIO, clock `sys`, optional reset `rst`, dmaengine PCM, ALSA kcontrols, and compatible `img,spdif-in`.

Risks: user controls reject changes while active, so user-space must sequence configuration before capture. `img_spdif_in_get_lock_freq()` indexes `multi_freqs` from hardware SAM value minus one without explicit range check; unexpected hardware status could read out of bounds. Lock threshold controls accept signed values but pack into masked fields, so sign extension behavior depends on intended hardware representation. Clock-gen calculation loops until hold >= 120 and assumes valid sys clock/rate ratios.

Test signals: capture at supported rates, single vs multi acquire controls, IEC958 status reads, lock/unlock frequency reporting, suspend/resume restoring write-only registers, EBUSY behavior for active control changes, and fuzz tests for SAM status values if hardware can expose invalid encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-out.c -->
# sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-out.c

Purpose: ASoC CPU DAI driver for Imagination SPDIF output with dmaengine PCM and IEC958 playback channel-status controls.

Important APIs/types/functions: `struct img_spdif_out` stores MMIO, sys/ref clocks, reset, DMA data, spinlock, and suspend snapshots. Controls expose IEC958 playback mask/default. DAI ops implement trigger, hw_params, and DAI probe. `img_spdif_out_reset()` preserves control and channel status across hardware reset.

Control flow: probe maps registers, gets reset/clocks, enables runtime PM, initializes control register and reset state, initializes lock, sets DMA FIFO info, registers component and dmaengine PCM. `hw_params()` accepts stereo S32_LE, chooses ref clock close to rate*256 or rate*384, and sets the clock selector bit from actual clock. Trigger start sets SRT; stop resets under lock. IEC958 control get/set reads/writes CSL/CSH registers under spinlock. Suspend saves CTL/CSL/CSH and resume restores them.

State and persistence: software state is mostly lock and saved registers. Hardware holds IEC958 channel status and transmit control. Runtime PM gates sys/ref clocks.

Dependencies/integration: requires MMIO, reset `rst`, clocks `sys` and `ref`, dmaengine PCM, ALSA controls, and compatible `img,spdif-out`.

Risks: `clk_set_rate()` return is ignored; actual clock is sampled afterward, but a failed set may leave poor-rate output. Trigger start is not locked while stop/reset and kcontrol writes are, so concurrent control and stream operations should be considered. Only S32_LE stereo is supported.

Test signals: playback rate tests, IEC958 status get/set persistence across reset and suspend/resume, trigger start/stop cycles, clock selector validation, and runtime PM error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/img-spdif-out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/pistachio-internal-dac.c -->
# sources/distributed-fs/ceph-client/sound/soc/img/pistachio-internal-dac.c

Purpose: ASoC codec driver for the Pistachio SoC internal DAC, controlling power/reset through a syscon regmap and a `VDD` regulator.

Important APIs/types/functions: `struct pistachio_internal_dac` stores regmap, regulator, and mute flag. DAPM exposes a DAC and AOUTL/AOUTR outputs; control `Playback Switch` maps to the power-down bit. `pistachio_internal_dac_reg_writel()` writes indirect GTI registers. Runtime PM callbacks power the DAC and regulator on/off. Probe configures supply voltage selection, powers the DAC, enables runtime PM, and registers one playback DAI.

Control flow: probe allocates state, gets `img,cr-top` syscon and `VDD` regulator, enables regulator, validates voltage as 1.8 V or 3.3 V, writes power select, cycles DAC power, enables runtime PM, then registers the codec component/DAI. Runtime resume enables regulator and powers the DAC; runtime suspend powers off then disables regulator. Remove disables PM, powers off, and disables regulator.

State and persistence: driver state is regulator/regmap handles and unused `mute`. Hardware state persists in top-level DAC control, reset, GTI indirect write, and power registers. Runtime PM owns current power state after probe.

Dependencies/integration: depends on syscon/regmap phandle `img,cr-top`, regulator named `VDD`, ASoC codec registration, and compatible `img,pistachio-internal-dac`.

Risks: regulator is enabled in probe before runtime PM and may be disabled twice only through carefully paired error/remove paths. Only two exact voltages are accepted. `mute` field is unused. The indirect register write sequence has no readback or completion polling.

Test signals: probe with 1.8 V and 3.3 V supplies, invalid-voltage rejection, runtime suspend/resume power sequencing, DAPM route visibility, playback DAI constraints, and regulator/syscon failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/img/pistachio-internal-dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/intel/Kconfig

Purpose: top-level Kconfig for Intel ASoC platform, DSP, ACPI match, codec, and board-driver support.

Important APIs/types/functions: exposes `SND_SOC_INTEL_SST_TOPLEVEL`, `SND_SOC_INTEL_CATPT`, `SND_SOC_INTEL_HASWELL`, `SND_SST_ATOM_HIFI2_PLATFORM`, PCI/ACPI Atom variants, `SND_SOC_ACPI_INTEL_MATCH`, `SND_SOC_ACPI_INTEL_SDCA_QUIRKS`, `SND_SOC_INTEL_KEEMBAY`, and `SND_SOC_INTEL_AVS`. It sources AVS boards and generic Intel boards Kconfig files.

Control flow: the SST toplevel boolean gates legacy SST/CATPT/Atom options. ACPI match helpers are available when either SST or SOF Intel toplevel is enabled. Keembay and AVS are independent platform options. Selected symbols pull in dependencies such as ACPI match helpers, DSP config, DMA, topology, HDA, and coredump support.

State and persistence: kernel configuration only; no runtime code.

Dependencies/integration: tightly integrated with the broader Intel ASoC tree, SOF top-level option, ACPI, PCI, X86, Keembay architecture, DMA, HDA, and board Kconfig files.

Risks: option interactions are subtle, especially Atom ACPI being mutually exclusive with SOF support as documented in help. Hidden symbols are selected by visible options and can affect build closure. `default y` on `SND_SOC_INTEL_SST_TOPLEVEL` changes menu exposure on X86/compile-test.

Test signals: kconfig dependency tests for X86, ACPI, PCI, SOF coexistence, Atom PCI/ACPI variants, AVS, Keembay, and sourced board menus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/Makefile

Purpose: top-level kbuild dispatch for Intel ASoC subdirectories.

Important APIs/types/functions: includes `common/` and `boards/` when `CONFIG_SND_SOC` is enabled; includes `atom/`, `catpt/`, `keembay/`, and `avs/` based on their platform config symbols.

Control flow: kbuild recurses into enabled subdirectories and builds their objects.

State and persistence: build-time only.

Dependencies/integration: maps symbols from `intel/Kconfig` to subtrees. Boards and common support are tied to the global ASoC symbol rather than platform-specific symbols.

Risks: broad inclusion of `boards/` and `common/` under `CONFIG_SND_SOC` means those subdirectories must self-gate their objects correctly. Adding new platform directories requires matching Kconfig and Makefile entries.

Test signals: build matrix across `CONFIG_SND_SOC`, CATPT, Atom, Keembay, and AVS symbols confirming correct subdirectory recursion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/Makefile

Purpose: kbuild file for Intel Atom HiFi2 SST platform support.

Important APIs/types/functions: defines composite object `snd-soc-sst-atom-hifi2-platform-y` from `sst-mfld-platform-pcm.o`, `sst-mfld-platform-compress.o`, and `sst-atom-controls.o`; includes that composite and the `sst/` DSP subdirectory when `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM` is enabled.

Control flow: selecting the hidden base Atom HiFi2 platform symbol builds both PCM/compress/control support and the DSP driver subtree.

State and persistence: build-time only.

Dependencies/integration: driven by `SND_SST_ATOM_HIFI2_PLATFORM`, selected by PCI and ACPI variants in Intel Kconfig.

Risks: the composite object and `sst/` subtree are controlled by the same symbol, so partial builds are not possible through Kconfig. Source file names must remain aligned with legacy Merrifield/Baytrail/Cherrytrail support.

Test signals: module/built-in builds for Atom PCI and ACPI options should produce `snd-soc-sst-atom-hifi2-platform` and recurse into `atom/sst/`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/Makefile -->
