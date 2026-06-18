# subset-b-006537 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rz-ssi.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/rz-ssi.c

Purpose: Renesas RZ/G2L SSIF-2 ASoC CPU DAI and PCM component driver. It exposes one stereo playback/capture DAI named `rz-ssi-dai`, supports 8-48 kHz S16/S24/S32 I2S, and can run either DMA or interrupt-driven PIO.

Important APIs, types, and functions: `struct rz_ssi_priv` owns MMIO, clocks, reset, IRQs, DMA channels, duplex flags, and cached hw params. `struct rz_ssi_stream` tracks the ALSA substream, DMA ring positions, period counter, FIFO depth, running state, error counters, DMA channel, and selected transfer function. Key DAI callbacks are `rz_ssi_startup`, `rz_ssi_shutdown`, `rz_ssi_dai_hw_params`, `rz_ssi_dai_set_fmt`, and `rz_ssi_dai_trigger`. PCM callbacks are `rz_ssi_pcm_open`, `rz_ssi_pcm_pointer`, and `rz_ssi_pcm_new`. Probe wires clocks `ssi`, `ssi_sfr`, `audio_clk1`, `audio_clk2`, named IRQs, optional DMA channels `tx`, `rx`, or `rt`, runtime PM, and the platform driver for `renesas,rz-ssi`.

Control flow: `hw_params` validates stereo and sample width, enforces identical params while a duplex peer is running, software-resets the SSI, then calls `rz_ssi_clk_setup` to choose master clock/divider and program word lengths. Trigger start initializes stream state, configures DMA or falls back to PIO, queues initial transfers, and enables TX/RX with duplex coordination. PIO IRQs move frames through FIFO registers and update ALSA periods. DMA callbacks update pointers and continuously submit one-period DMA descriptors. Error IRQs stop, clear flags, refill a few descriptors/FIFO chunks, and restart.

State and persistence: State is in runtime memory and hardware registers only. `hw_params_cache`, stream buffer positions, `dup` flags, DMA channel handles, and error counters are reset across stream lifecycle. Runtime suspend asserts the reset; resume deasserts it, with reg state rebuilt by ALSA callbacks.

Dependencies and integration: Depends on ALSA SoC, DMAEngine, device tree clocks/IRQs/resets, `pm_runtime`, and Renesas SSIF registers. It integrates with generic ASoC machine links as a CPU DAI and uses managed PCM buffers rather than a separate dmaengine PCM component.

Risks and edge cases: Full duplex is delicate because hardware reset affects both directions; the driver requires identical params and has special `one_stream_triggered` sequencing. Clock selection only accepts exact dividers in `ckdv`. DMA fallback mutates both stream transfer callbacks globally. `irq_rt` shares playback DMA channel semantics when only a combined request line exists. Pointer accounting assumes period-sized DMA descriptors and can misreport if callbacks arrive after stop, though guards reduce that.

Test signals: Boot/probe should show DMA enabled or PIO fallback and register the DAI. Playback/capture at 16/24/32-bit stereo rates should advance periods without underrun/overrun logs. Duplex should reject mismatched rates/formats and start both directions without stuck LRCK. Suspend/resume and STOP/START loops should not leave SSI busy or FIFOs uncleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/rz-ssi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/sh7760-ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/sh7760-ac97.c

Purpose: Small SuperH SH7760 AC97 machine driver. It creates a `soc-audio` platform device for one AC97 link between CPU DAI `hac-dai.0`, codec `ac97-codec/ac97-hifi`, and platform `sh7760-pcm-audio`.

Important APIs, types, and functions: Uses `SND_SOC_DAILINK_DEFS`, one `snd_soc_dai_link`, one `snd_soc_card`, and module init/exit functions `sh7760_ac97_init` and `sh7760_ac97_exit`. It directly accesses the IPSEL pinmux register at `0xFE400034` with `__raw_readw/__raw_writew`.

Control flow: Module init sets AC97 pinmux bits `(3 << 10)`, allocates a `soc-audio` platform device, stores the card as driver data, and adds the device. Exit unregisters the platform device.

State and persistence: Only static module state is kept: the `snd_soc_card`, DAI link, and allocated platform device pointer. Pinmux writes persist in hardware until changed elsewhere; the driver does not restore old IPSEL bits on exit.

Dependencies and integration: Depends on legacy ASoC `soc-audio`, SH7760 HAC/PCM drivers, AC97 codec support, and board-specific MMIO assumptions.

Risks and edge cases: Raw hard-coded pinmux access bypasses pinctrl and has no error handling or cleanup. The machine has no device-tree matching, no dynamic resources, and no clock or GPIO handling. Probe failures only clean up the platform device, not IPSEL.

Test signals: Loading the module should instantiate one "SH7760 AC97" card. Audio depends on HAC and sh7760 PCM drivers binding. Unload should remove the card, while pinmux state may remain enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/sh7760-ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/siu.h -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/siu.h

Purpose: Shared header for the Renesas/SuperH SIU ASoC driver and its firmware format. It defines SPB firmware memory layout, SIU register offsets, common runtime structures, and cross-file exports used by `siu_dai.c` and `siu_pcm.c`.

Important APIs, types, and functions: `struct siu_spb_param` describes one SPB routing program entry. `struct siu_firmware` embeds FIR coefficients, PRAM program blocks, YRAM defaults, and up to 32 SPB params. Kernel-only structs include `siu_info` for global device resources, `siu_stream` for one playback/capture DMA stream, and `siu_port` for per-port duplex, PCM, stream, STFIFO, and TRDAT state. Exports include `siu_ports`, `siu_component`, `siu_i2s_data`, `siu_init_port`, and `siu_free_port`.

Control flow: This file has no executable flow, but it establishes the shared data model: DAI probe loads firmware into `siu_info`, PCM component allocates `siu_port`, and stream callbacks use `siu_port_info()` to map a substream to the platform-device id.

State and persistence: State is in global `siu_i2s_data` and `siu_ports[SIU_PORT_NUM]`, making the driver effectively singleton per SIU block. Firmware arrays are copied into `siu_info->fw` and later rewritten before programming PRAM/YRAM.

Dependencies and integration: Depends on ALSA SoC/PCM headers, DMAEngine, SuperH DMA `sh_dma.h`, raw MMIO helpers, and platform ids for SIU port A/B.

Risks and edge cases: The header codifies "only one SIU port can be used at a time"; global state makes multi-device instances unsafe. Firmware structure size and binary `siu_spb.bin` must match exactly. `siu_port_info()` trusts `pdev->id`.

Test signals: Build coverage should catch firmware-layout or register macro mismatches. Runtime validation comes from successful SIU probe, firmware load, PCM creation for the expected port id, and DMA stream start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/siu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/siu_dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/siu_dai.c

Purpose: Renesas SH7343/SH7722 SIU CPU DAI driver. It loads SIU SPB firmware, maps PRAM/XRAM/YRAM/register windows, configures the SIU serial format/clocking, starts and stops the SPB program, and exposes mixer volume controls.

Important APIs, types, and functions: Global `siu_i2s_data` holds the active `siu_info`. `siu_flags` maps port A/B and playback/capture to IFCTL format bits. `siu_dai_start/stop`, `siu_dai_spbAselect`, `siu_dai_spbBselect`, `siu_dai_spbstart`, and `siu_dai_spbstop` program hardware and firmware memory. `siu_init_port`/`siu_free_port` allocate per-port ALSA control state. DAI ops are `startup`, `shutdown`, `prepare`, `set_sysclk`, and `set_fmt`; probe requests firmware `siu_spb.bin` and registers `siu_i2s_dai`.

Control flow: Probe allocates `siu_info`, copies firmware, maps memory subregions, registers the component/DAI, then enables runtime PM. Startup applies PCM constraints and resets/configures core registers. Prepare selects SPB paths, opens the port, sets data packing, starts the SPB, and marks playback/capture active. Shutdown clears active flags and stops SPB/SIU only after both streams are inactive. `set_fmt` writes I2S or left-justified IFCTL bits; `set_sysclk` reparents and rates the selected SuperH clock.

State and persistence: Port state includes active stream bitmask, volumes, and firmware-derived FIFO/TRDAT values. Volume controls write SBDVCA/SBDVCB immediately and cache values in `siu_port`. Firmware in `siu_i2s_data->fw` is modified before loading into YRAM.

Dependencies and integration: Depends on `siu.h`, `asm/siu.h`, `asm/clock.h`, firmware loader, SuperH clock API, and the PCM component exported by `siu_pcm.c`.

Risks and edge cases: Singleton global state and one-SPB limitation prevent safe multi-instance use. Firmware copy uses `fw_entry->size` without explicit struct-size validation. Clock references are manually acquired and released around every `set_sysclk`. Shutdown refuses to stop if DMA flags are still set, leaving cleanup to PCM code.

Test signals: Probe must load `siu_spb.bin` and map all regions. Playback/capture prepare should start SPB without `-EBUSY`. Mixer writes should update volume registers. Format/clock tests should reject unsupported formats or output-clock directions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/siu_dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/siu_pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/siu_pcm.c

Purpose: PCM platform/component side of the Renesas SIU driver. It allocates DMA channels, schedules one-period DMA transfers through a high-priority workqueue, toggles SIU FIFOs, reports ALSA pointer/period progress, and creates/free SIU port state.

Important APIs, types, and functions: Global `siu_ports` stores per-port state. Stream start/stop helpers are `siu_pcm_stmwrite_start/stop` and `siu_pcm_stmread_start/stop`. DMA submission is in `siu_pcm_wr_set` and `siu_pcm_rd_set`; completion uses `siu_dma_tx_complete`; deferred queuing uses `siu_io_work`. Component callbacks are `siu_pcm_open`, `close`, `prepare`, `trigger`, `pointer`, `pcm_new`, and `pcm_free`. The exported `siu_component` is registered by `siu_dai.c`.

Control flow: `pcm_new` selects port by platform-device id, calls `siu_init_port`, configures a managed DMA buffer, stores the PCM pointer, and initializes work items. Open selects TX/RX slave ids from platform data and requests a DMA channel using a SuperH DMA filter. Prepare validates buffer-period divisibility, caches sizes/format/frame count, and trigger starts or stops stream-specific DMA. Each work item submits the current period; completion advances `cur_period`, queues the next work item, and calls `snd_pcm_period_elapsed`.

State and persistence: `siu_stream` stores substream, format, buffer size, period size, current period, transfer count, DMA channel/descriptor/cookie, and read/write flag. Hardware FIFO state is toggled by STFIFO masks derived from firmware. State is volatile and reset at close/free.

Dependencies and integration: Depends on `siu_i2s_data` from `siu_dai.c`, platform data `struct siu_platform` for DMA slave ids, SuperH DMAEngine, ALSA managed DMA buffers, and system high-priority workqueue.

Risks and edge cases: The DMA completion callback name is TX-specific but used for capture too. Workqueue scheduling after stop relies on `rw_flg` checks. `dma_request_channel` and platform-data slave ids are legacy and can fail silently on DT-only systems. Pointer granularity is one period, not actual DMA residue. `siu_pcm_free` assumes `siu_ports[pdev->id]` exists.

Test signals: Open should allocate the expected DMA channel per stream. Prepare should reject non-period-aligned buffers. START should produce repeated period elapsed events; STOP should clear FIFO enable bits and stop new work. Free should cancel both work items without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/siu_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/ssi.c -->
# sources/distributed-fs/ceph-client/sound/soc/renesas/ssi.c

Purpose: Legacy SuperH SH7760/SH7780 SSI I2S CPU DAI driver. It directly controls SSI registers for simplex playback or capture, including sample width, channel count, clock divider, bus format, and DMA enable.

Important APIs, types, and functions: `struct ssi_priv` stores hard-coded MMIO base, requested sysclk, and an `inuse` simplex guard. Main DAI ops are `ssi_startup`, `ssi_shutdown`, `ssi_trigger`, `ssi_hw_params`, `ssi_set_sysclk`, `ssi_set_clkdiv`, and `ssi_set_fmt`. `sh4_ssi_dai` exposes one or two DAIs depending on CPU subtype. Probe registers `sh4_ssi_component`.

Control flow: Startup rejects concurrent use of the same SSI. `hw_params` computes CR bits for direction, even channel count 2-8, data word length, and system word length. `set_fmt` programs I2S/left/right-justified mode, gated clock, inversion, and clock-provider bits. Trigger START sets DMA and enable bits; STOP clears them. There is no IRQ or DMA descriptor handling here; a separate platform PCM driver is expected.

State and persistence: Driver state is static per SoC DAI. Register writes persist until overwritten. `sysclk` is cached but not used to compute dividers. `inuse` is not protected by a lock.

Dependencies and integration: Depends on compile-time SuperH CPU subtype, raw MMIO, ALSA SoC DAI registration, and external board code for pinmux and clock source setup.

Risks and edge cases: Hard-coded physical register addresses and raw dereferences are fragile. Simplex exclusion has a FIXME about locking and can race. Several switch statements intentionally fall through to encode bitfields; maintainers must preserve that pattern. No runtime PM, reset, or pinctrl integration exists.

Test signals: Loading should register `ssi-dai.0` and maybe `ssi-dai.1`. Invalid odd channels or unsupported sample widths should fail. START/STOP should toggle CR_DMAEN/CR_EN. Board tests should verify pinmux and external bit clock configuration separately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/renesas/ssi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/Kconfig

Purpose: Kconfig menu for Rockchip ASoC controller and machine drivers. It controls build availability for I2S, I2S/TDM, PDM, SAI, SPDIF, and several board-specific codec/HDMI sound cards.

Important APIs, types, and functions: Configuration symbols include `SND_SOC_ROCKCHIP_I2S`, `SND_SOC_ROCKCHIP_I2S_TDM`, `SND_SOC_ROCKCHIP_PDM`, `SND_SOC_ROCKCHIP_SAI`, `SND_SOC_ROCKCHIP_SPDIF`, `SND_SOC_ROCKCHIP_MAX98090`, `SND_SOC_ROCKCHIP_RT5645`, `SND_SOC_RK3288_HDMI_ANALOG`, and `SND_SOC_RK3399_GRU_SOUND`. Controller symbols select `SND_SOC_GENERIC_DMAENGINE_PCM`; PDM selects `RATIONAL`; SPDIF selects `SND_PCM_IEC958`. Machine symbols select their codec/controller dependencies.

Control flow: This is declarative build configuration. The menu is visible for `ARCH_ROCKCHIP` or `COMPILE_TEST` and requires `HAVE_CLK`. Selecting a board driver pulls in the needed controller and codec drivers.

State and persistence: No runtime state. The selected symbols persist only in kernel `.config` and determine objects built by the Makefile.

Dependencies and integration: Integrates Rockchip ASoC with kernel build system and codec Kconfig symbols such as MAX98090, RT5645, HDMI codec, ES8328, RT5514, DA7219, DMIC, and MAX98357A.

Risks and edge cases: Board drivers depend on I2C/GPIOLIB/SPI as needed, but real device-tree and pinctrl requirements are not expressible here. `COMPILE_TEST` can build code on non-Rockchip platforms where runtime resources are absent.

Test signals: `allyesconfig`/`COMPILE_TEST` builds should include selected objects. Enabling a machine symbol should automatically enable its controller and codec dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/Makefile

Purpose: Rockchip ASoC object mapping for Kbuild. It maps Kconfig symbols to controller and machine-driver object files.

Important APIs, types, and functions: Defines module object aggregates for `snd-soc-rockchip-i2s`, `snd-soc-rockchip-i2s-tdm`, `snd-soc-rockchip-pdm`, `snd-soc-rockchip-sai`, `snd-soc-rockchip-spdif`, `snd-soc-rockchip-max98090`, `snd-soc-rockchip-rt5645`, `snd-soc-rk3288-hdmi-analog`, and `snd-soc-rk3399-gru-sound`.

Control flow: Kbuild appends objects to `obj-$(CONFIG_...)` according to selected Kconfig symbols. Each aggregate currently contains one `.o`.

State and persistence: No runtime state; affects build outputs and module names.

Dependencies and integration: Consumes symbols declared in `Kconfig` and source files in the same directory, including files not in this work item such as `rockchip_sai.c` and `rockchip_spdif.c`.

Risks and edge cases: Missing object entries would make a Kconfig option build no code; stale entries would break builds. Module names are ABI-visible to packaging/scripts.

Test signals: `make sound/soc/rockchip/` or full kernel builds with each symbol enabled should produce the expected `.o`/module artifacts without unresolved references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3288_hdmi_analog.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3288_hdmi_analog.c

Purpose: RK3288 machine driver for boards with an analog codec plus HDMI audio on a shared Rockchip I2S controller. It builds a multi-codec ASoC card with DAPM pins for analog headphone and HDMI output.

Important APIs, types, and functions: `struct rk_drvdata` stores optional headphone-enable GPIO. `rk_hp_power` drives that GPIO from DAPM events. `rk_hw_params` selects MCLK rates based on sample rate and calls `snd_soc_dai_set_sysclk` on CPU and analog codec DAIs. `rk_init` sets optional headphone jack GPIO detection. Probe parses `rockchip,model`, `rockchip,audio-codec`, codec DAI name, `rockchip,i2s-controller`, and `rockchip,routing`.

Control flow: Probe allocates machine data, binds card/device, requests optional `rockchip,hp-en` GPIO, parses card name and phandles, assigns CPU/platform/codec nodes into a single DAI link, parses routing, stores drvdata, and registers the card. During stream setup, `hw_params` chooses 12.288 MHz, 24.576 MHz, or 11.2896 MHz MCLK. DAPM toggles headphone power.

State and persistence: Static card and DAI link definitions are mutated with of-nodes during probe. Runtime state is limited to GPIO descriptor and jack object. GPIO state follows DAPM.

Dependencies and integration: Depends on Rockchip I2S CPU DAI, HDMI codec, analog codec named by device tree, optional headset GPIO, ALSA jack helpers, and device-tree routing.

Risks and edge cases: Static globals make multiple instances unsafe. HDMI codec component name `hdmi-audio-codec.2.auto` is hard-coded for the second codec slot. `snd_soc_jack_add_gpios` legacy GPIO jack setup has no explicit cleanup. Unsupported rates fail in `hw_params`.

Test signals: Device tree probe should create a card with "Analog" and "HDMI" controls. Jack GPIO should report headphone state when present. Playback at common 44.1/48/96/192 kHz rates should program expected MCLKs; unsupported rates should fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3288_hdmi_analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3399_gru_sound.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3399_gru_sound.c

Purpose: RK3399 GRU machine driver supporting a variable set of codecs: CDN DP/HDMI, DA7219 headset codec, DMIC codec, MAX98357A speaker amp, RT5514 I2C capture codec, and RT5514 SPI DSP wake path.

Important APIs, types, and functions: `rockchip_sound_*_hw_params` functions set per-link MCLK policy; DA7219 also sets PLL sysclk. `rockchip_sound_cdndp_init` and `rockchip_sound_da7219_init` create jack objects and button mappings. `rockchip_dais` defines six DAI templates. `rockchip_routes` maps DAPM route sets per link. `dailink_match` and `rockchip_sound_codec_node_match` identify codecs by compatible string and optional bus type. `rockchip_sound_of_parse_dais` builds the active DAI-link array dynamically from `rockchip,cpu` and `rockchip,codec` phandles.

Control flow: Probe parses available codec phandles in order, filters unavailable nodes, matches each to a DAI template, picks CPU0 for most links, CPU1 for DP, and the codec node itself for RT5514 DSP SPI, copies matching DAPM routes, reads optional `dmic-wakeup-delay-ms`, and registers the card. Startup limits formats to S16_LE and rates to 8-96 kHz. Runtime hw_params sets MCLK to rate*256 or fixed audio-family clocks and delays after DMIC/RT5514 capture if configured.

State and persistence: Static card and jack objects persist for the module. Dynamic dai_link and routes arrays are devm-allocated. `dmic_wakeup_delay` is a module-global property value.

Dependencies and integration: Depends on Rockchip I2S, codec drivers for MAX98357A/RT5514/DA7219/HDMI/DMIC, I2C and SPI bus devices, ALSA jack/input key mapping, and device tree ordering of codec phandles.

Risks and edge cases: Codec matching silently skips unavailable or unmatched nodes, so missing audio paths may not fail probe. Static global `dmic_wakeup_delay` and jack objects are not multi-instance safe. CPU phandle references are not released. Rate constraints are broad but codec-specific fixed MCLK code rejects 192 kHz for DA7219.

Test signals: Boot should register links only for available GRU codecs. Jack events should appear for DP and headset buttons. Per-link playback/capture should set MCLKs and apply DMIC delay. Device-tree permutations should be tested for absent optional codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rk3399_gru_sound.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.c

Purpose: Rockchip I2S controller CPU DAI driver using regmap and generic DMAEngine PCM. It supports playback/capture up to 8 channels, 8-192 kHz, S8/S16/S20_3LE/S24/S32 formats, optional GRF pin direction routing, and runtime PM.

Important APIs, types, and functions: `struct rk_i2s_dev` owns clocks, regmap, GRF regmap, DMA data, capability flags, TX/RX active flags, master-mode flag, bclk ratio, pinctrl states, and spinlock. Key DAI ops are `rockchip_i2s_set_fmt`, `rockchip_i2s_hw_params`, `rockchip_i2s_trigger`, `rockchip_i2s_set_bclk_ratio`, `rockchip_i2s_set_sysclk`, and DAI probe. Register access policy is defined by `rockchip_i2s_*_reg`; probe initializes clocks, regmap, DAI capabilities from `dma-names`, pinctrl, PM, component, and dmaengine PCM.

Control flow: `set_fmt` resumes PM and programs master/slave, inversion, and I2S/left/right/DSP formats in TXCR/RXCR/CKR. `hw_params` computes BCLK/LRCK dividers in master mode, programs sample width and channel select, optionally writes GRF IO direction from TX channel count, sets DMA watermarks, and configures clock mode for symmetric links. Trigger enables/disables DMA and XFER bits per stream, coordinating shared stop/clear when both TX and RX are idle and toggling optional BCLK pinctrl.

State and persistence: Register state is cached with REGCACHE_FLAT; runtime suspend cache-only disables MCLK, resume syncs cache after enabling MCLK. `tx_start`/`rx_start` are protected by spinlock. DAI caps are determined once from DT.

Dependencies and integration: Depends on clocks `i2s_hclk` and `i2s_clk`, optional `rockchip,grf`, optional pinctrl states `bclk_on/off`, DMA request names `tx`/`rx`, ALSA SoC, regmap, PM runtime, and generic DMAEngine PCM.

Risks and edge cases: `pm_runtime_get_sync` return is not checked in `set_fmt`. GRF routing derives direction from TXCR even for capture cases. Static `symmetric_rate` behavior changes TRCM to TX-only under some link conditions. Missing `bclk_off` when `bclk_on` exists fails probe.

Test signals: Probe should expose playback/capture only when corresponding DMA names exist. `aplay`/`arecord` should start XFER and DMA bits, then clear on stop. Runtime suspend/resume should preserve register configuration. Multi-channel tests should validate GRF IO direction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.h

Purpose: Register definition header for the base Rockchip I2S controller driver and its machine-driver users.

Important APIs, types, and functions: Defines bitfields for TXCR/RXCR format, channel select, word width, CKR master/slave and clock dividers, FIFO level, DMA control, interrupts, transfer start/stop, clear logic, TX/RX data registers, divider ids, channel constants, register offsets, and IO direction GRF encodings.

Control flow: No executable code. The macros are consumed by `rockchip_i2s.c` to build regmap updates and by machine drivers for shared divider identifiers.

State and persistence: No state. Macro values map directly to hardware register layout and therefore must remain consistent with SoC manuals.

Dependencies and integration: Requires Linux `BIT` and standard kernel integer macros from including translation units. Integrates with regmap access tables and GRF writes in the I2S driver.

Risks and edge cases: Incorrect shifts or masks can corrupt adjacent hardware fields. The IO direction values differ from the TDM header, so cross-using base I2S and I2S/TDM macros would be unsafe. Comments include typos but not behavioral issues.

Test signals: Build coverage plus runtime audio format/channel tests are the main validation. Register dumps during 2/4/6/8-channel playback should match expected CSR and GRF direction fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.c

Purpose: Rockchip I2S/TDM controller DAI driver. It extends the base I2S model with TDM slots, separate TX/RX master clocks, reset controls, synchronized TX/RX clock modes, optional IO multiplexing, path routing, and SoC-specific GRF setup.

Important APIs, types, and functions: `struct rk_i2s_tdm_dev` holds clocks, resets, regmap/GRF, DMA data, SoC data, master/TDM/multiplex flags, frame width, TRCM mode, lane routes, refcount, and DAI pointer. DAI ops include `set_fmt`, `hw_params`, `trigger`, `set_sysclk`, `set_bclk_ratio`, and `set_tdm_slot`. Helpers handle MCLK enable, runtime PM, reset/clear (`rockchip_snd_xfer_clear`), shared TRCM start/stop (`rockchip_snd_txrxctrl`), IO multiplex, path validation/config, and SoC GRF init.

Control flow: Probe reads TRCM sync properties, initializes DAI capabilities from `dma-names`, gets GRF/resets/clocks, maps registers, configures DMA addresses, validates optional TX/RX route arrays, enables clocks, sets DMA watermarks and TRCM bits, runs SoC init, then registers component and dmaengine PCM. `set_fmt` writes master/slave, inversion, base format, and TDM frame-sync/shift fields when TDM mode is active. `hw_params` sets clock rates/dividers, width/channel fields, optionally updates both TX/RX in synchronized TRCM mode while pausing active transfer, and applies IO multiplex constraints. Trigger starts/stops TX, RX, or shared TX/RX depending on TRCM.

State and persistence: Regmap uses flat cache and PM sync. `refcount` under spinlock coordinates shared synchronized transfer. `mclk_tx_freq` and `mclk_rx_freq` cache target sysclk values from machine drivers. Path arrays persist after DT parsing.

Dependencies and integration: Depends on clocks `hclk`, `mclk_tx`, `mclk_rx`, optional resets `tx-m`/`rx-m`, optional `rockchip,grf`, generic DMAEngine PCM, SoC match data for PX30/RK1808/RK3308/RK3568/RV1126, and DT properties for TRCM, IO multiplex, and lane routes.

Risks and edge cases: Synchronized reset admits a race because reset bulk atomicity is unavailable. Refcount underflow would break shared transfer if trigger calls are unbalanced. TRCM non-TXRX requires GRF; missing GRF fails SoC init. IO multiplex supports only a 10-channel aggregate constraint. Route properties must provide exactly four unique entries.

Test signals: Probe matrix should cover SoCs with and without SoC data. Playback/capture/TDM slot tests should validate dividers, frame width, and route fields. Duplex synchronized TRCM should start both sides together, pause safely on hw_params changes, and clear/reset on stop. Suspend/resume should sync regcache.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.h -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.h

Purpose: Register and GRF macro header for the Rockchip I2S/TDM controller driver.

Important APIs, types, and functions: Defines TXCR/RXCR fields including per-path lane routing, CKR, FIFO, DMA, interrupt, XFER/CLR, TDM frame controls, CLKDIV, register offsets, HIWORD update helper, and SoC-specific GRF clock-routing constants for PX30, RK1808, RK3308, RK3568, and RV1126.

Control flow: No executable code. `rockchip_i2s_tdm.c` uses these macros for regmap updates, route validation, TDM slot programming, and SoC init writes.

State and persistence: No runtime state. Constants encode hardware ABI for multiple SoC families.

Dependencies and integration: Includes `linux/hw_bitfield.h` for `FIELD_PREP_WM16_CONST` and uses Linux bit macros. Integrates with device-tree match data in the TDM driver.

Risks and edge cases: Base I2S and TDM headers use similar names with different IO direction encodings, so accidental inclusion misuse can misroute pins. HIWORD update constants must match GRF write-mask conventions. TDM frame macros subtract one from widths, so callers must validate nonzero slot/frame widths.

Test signals: Compile coverage across all supported SoCs plus register dump validation for TRCM TX-only/RX-only, IO multiplex, TDM slot width, and lane routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_max98090.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_max98090.c

Purpose: Rockchip machine driver for boards using MAX98090 analog audio, HDMI audio, or both. It builds the appropriate ASoC card based on device-tree codec phandles and wires DAPM, jack detection, MCLK setup, and a TS3A227E headset accessory device.

Important APIs, types, and functions: Defines three card variants: analog, HDMI, and analog+HDMI. `rk_aif1_hw_params` selects MCLK for common 44.1/48 kHz families and skips codec sysclk errors for HDMI. `rk_aif1_startup` constrains period size to 240 for PL330 stress behavior. `rk_98090_headset_init` creates headset/button jack and calls `ts3a227e_enable_jack_detect`. `rk_jack_event` force-enables/disables `MICBIAS` and `SHDN` DAPM pins on microphone presence. Probe selects card variant from `rockchip,audio-codec` and `rockchip,hdmi-codec`.

Control flow: Probe parses I2S controller, optional audio and HDMI codecs, mutates the selected static DAI links with CPU/platform/codec nodes, requires `rockchip,headset-codec` when analog audio exists, parses card name, and registers the card. Runtime init registers the jack notifier or HDMI jack. Startup applies the period constraint, and hw_params programs CPU/codec clocks.

State and persistence: Static cards, links, jacks, notifier, and aux device are module-global. DAPM pin state changes on jack events. OF node pointers are stored in static link structures.

Dependencies and integration: Depends on Rockchip I2S, MAX98090, optional HDMI codec, TS3A227E headset codec, PL330-related period constraint, and device-tree phandles.

Risks and edge cases: Static globals make multiple cards unsafe. Probe does not release OF nodes. Requiring headset codec for any analog path may prevent analog audio without TS3A227E. The fixed period size is conservative but can surprise users. Comment typo names MAX90809.

Test signals: DT variants should create analog-only, HDMI-only, and combined cards. Headset insertion should toggle MICBIAS/SHDN and report buttons. Playback should work at supported rates and enforce 240-frame periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_max98090.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.c

Purpose: Rockchip PDM capture controller DAI driver. It configures PDM clocks, decimation/sample-rate controls, channel paths, DMA read thresholds, high-pass filters, runtime PM, and generic DMAEngine PCM for capture-only audio.

Important APIs, types, and functions: `struct rk_pdm_dev` owns clocks, regmap, DMA data, reset, and hardware version. Clock helpers are `get_pdm_clk`, `get_pdm_ds_ratio`, `get_pdm_cic_ratio`, and `samplerate_to_bit`. DAI ops are `rockchip_pdm_set_fmt`, `rockchip_pdm_trigger`, and `rockchip_pdm_hw_params`. Probe sets version from compatible, gets optional reset, configures regmap/DMA, clocks, runtime PM, component, initial stopped RX state, optional `rockchip,path-map`, and dmaengine PCM.

Control flow: `hw_params` ignores playback, selects a parent PDM clock for the sample rate, sets the clock rate, programs fractional divider and reset for RK3308/RV1126 variants when changed, chooses CIC/DS ratio, enables HPF and PDM clock, programs left-justified mode for newer variants, sets sample width and path enables from channel count, and sets DMA read level to `8 * channels`. Trigger toggles DMA read and RX start/clear. Runtime PM enables/disables `pdm_clk` and `pdm_hclk`; system sleep marks regcache dirty and syncs on resume.

State and persistence: Register defaults are cached through regmap. `version` controls hardware-specific paths. Optional path-map writes lane routing once at probe. No persistent storage beyond clocks/registers.

Dependencies and integration: Depends on clocks `pdm_clk`/`pdm_hclk`, reset `pdm-m` for RK3308-like versions, compatible match data, rational approximation support, DMAEngine PCM, and ALSA SoC.

Risks and edge cases: `rockchip_pdm_path_parse` returns the count when path-map is absent or wrong; absent is accepted only when it is `-ENOENT`. Probe enables `hclk`, then runtime resume may enable it again when runtime PM is disabled path is used; remove disables both clocks explicitly. Fractional divider reset interrupts active capture if params change. Only even 2/4/6/8 channels are accepted.

Test signals: Probe should register capture-only DAI and DMA address at RXFIFO. Captures at 8-192 kHz and 2/4/6/8 channels should program expected DS/CIC ratios and produce samples. Suspend/resume should preserve configuration. Invalid path-map or channel counts should fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.h -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.h

Purpose: Register definition header for the Rockchip PDM capture controller.

Important APIs, types, and functions: Defines register offsets for system control, CTRL0/CTRL1, clock, HPF, FIFO, DMA, interrupts, RX FIFO data, data valid, and version. Bit macros cover RX start/stop/clear, PDM path enables, left/right-justified mode, sample-rate selector, valid data width, fractional divider numerator/denominator, path routing, clock ratios, clock polarity, downsample/CIC ratios, HPF controls, and DMA read threshold.

Control flow: No executable code. `rockchip_pdm.c` uses these macros for `regmap_update_bits` and DMA address setup.

State and persistence: No state; constants must match hardware register layout for all supported PDM versions.

Dependencies and integration: Uses Linux `BIT`/`GENMASK` from including source. Integrates with regmap read/write filters and hardware-specific code paths in the PDM driver.

Risks and edge cases: Macros such as `PDM_VDW(X)` and `PDM_DMA_RDL(X)` assume nonzero inputs. `PDM_CLK_CTRL` shares low bits between DS ratio and CIC ratio meanings depending on hardware version, so callers must select the correct mask.

Test signals: Build and register-dump validation during sample-rate/channel tests should confirm expected CTRL0, CLK_CTRL, HPF, and DMA_CTRL fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_pdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_rt5645.c -->
# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_rt5645.c

Purpose: Rockchip machine driver for boards using RT5645/RT5650 analog codec on a Rockchip I2S controller.

Important APIs, types, and functions: Defines one static DAI link named `rt5645` with codec DAI `rt5645-aif1`, DAPM widgets/routes for headphones, speakers, headset mic, and internal mic, and DAPM pin controls. `rk_aif1_hw_params` sets CPU and codec MCLK to 12.288 MHz or 11.2896 MHz families. `rk_init` creates headset/button jack and calls `rt5645_set_jack_detect`. Probe parses codec and I2S phandles plus `rockchip,model`; remove releases stored OF nodes.

Control flow: Probe assigns card device, parses `rockchip,audio-codec`, parses `rockchip,i2s-controller`, sets platform node to CPU node, parses card name, and registers the card. On error and remove, it drops OF references. Runtime init configures jack reporting. `hw_params` rejects unsupported sample rates and programs clocks.

State and persistence: Static card, DAI link, and jack objects are module-global. OF node references are stored until remove or probe error. No extra runtime-private allocation is used.

Dependencies and integration: Depends on Rockchip I2S, RT5645 codec driver, ALSA jack/input support, and device-tree phandles.

Risks and edge cases: Static globals are not multi-instance safe. Only specific rate families are accepted. Jack detect passes the same jack object for headphone, mic, and button reporting, matching codec API expectations but coupling all events to one object.

Test signals: Probe should create the named card and controls. Headset insertion/buttons should report through the RT5645 jack. Playback/capture at supported rates should set both CPU and codec clocks; missing phandles should fail and release references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_rt5645.c -->
