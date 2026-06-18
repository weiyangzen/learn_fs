# Research: subset-b-006418

Grouped source-tree-aligned research for ALSA SoC Atmel/Microchip, Au1x, and Broadcom audio files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-i2s-mcc.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-i2s-mcc.c

## Purpose
Microchip I2S Multi-Channel Controller CPU DAI driver. It exposes playback and capture DAIs for sam9x60/sama7g5 I2SMCC blocks, configures I2S/left-justified/TDM data framing, selects pclk or gclk clocking, and binds the hardware holding registers to dmaengine PCM.

## Important APIs, Types, And Functions
- `struct mchp_i2s_mcc_soc_data` carries SoC differences: number of data pin pairs and FIFO availability.
- `struct mchp_i2s_mcc_dev` persists regmap, pclk/gclk handles, DMA data, selected DAI format, sysclk/frame settings, TDM slots, channel count, ready wait queues, and gclk state flags.
- DAI ops are `mchp_i2s_mcc_set_sysclk`, `mchp_i2s_mcc_set_bclk_ratio`, `mchp_i2s_mcc_set_dai_fmt`, `mchp_i2s_mcc_set_dai_tdm_slot`, `mchp_i2s_mcc_startup`, `mchp_i2s_mcc_hw_params`, `mchp_i2s_mcc_trigger`, and `mchp_i2s_mcc_hw_free`.
- `mchp_i2s_mcc_config_divs()` searches pclk/gclk rounded rates using an LCM of sysclk and bclk, then programs IMCKDIV/ISCKDIV and source clock bits.
- `mchp_i2s_mcc_interrupt()` acknowledges stop-drain ready interrupts and wakes TX/RX wait queues.
- `mchp_i2s_mcc_probe()` maps registers, creates regmap, requests IRQ, gets clocks, parses OF match data and `microchip,tdm-data-pair`, registers the component/DAI and dmaengine PCM.

## Control Flow
Probe builds the device state, enables the peripheral clock for register access, registers the DAI, and sets DMA addresses to `THR` and `RHR`. Startup resets the IP only when neither direction is running. `hw_params` validates the requested format, clock-provider mode, channel count, sample format, TDM mask, FIFO mode, and DMA burst size; if another stream is already running it rejects mismatched mode registers. Trigger start enables clock and either TX or RX; trigger stop disables the stream and enables ready interrupts so `hw_free` can wait up to 500 ms for final data availability before disabling clocks.

## State And Persistence
Runtime state is in memory only: selected format, requested sysclk/frame length, TDM slots, active channel count, DMA maxburst, and gclk prepare/enable flags. Hardware configuration persists in MRA/MRB until reset or reprogramming. There is no disk persistence. Wait queues bridge interrupt state into stop cleanup.

## Dependencies And Integration Points
Depends on Linux ASoC, dmaengine PCM, regmap MMIO, clocks, IRQs, and OF compatible data. It integrates with machine drivers through standard DAI format/sysclk/TDM callbacks and with DMA via `snd_soc_dai_init_dma_data` and `devm_snd_dmaengine_pcm_register`.

## Risks
Clock-rate selection is central: bad gclk/pclk rounding or missing gclk can reject otherwise valid audio modes. Full-duplex mode is constrained by symmetric rate, sample bits, and channels and by exact MRA/MRB reuse when one stream is already active. TDM masks must be contiguous and identical for RX/TX; nonstandard daisy-chain layouts are rejected. Stop relies on ready interrupts and a timeout fallback; missed interrupts can delay clock shutdown. The optional gclk path logs a warning with a potentially stale `err` value when a non-defer `devm_clk_get("gclk")` fails.

## Test Signals
Useful signals include probe success and hardware version logging, `aplay`/`arecord` at 8 kHz through 192 kHz across S8/S16/S24/S32 formats, TDM slot validation, full-duplex mismatch rejection, runtime stop without ready timeouts, and DMA maxburst alignment across representative period sizes. Device-tree tests should cover both one-pair sam9x60 and FIFO-capable sama7g5 data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-i2s-mcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-pdmc.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-pdmc.c

## Purpose
Microchip Pulse Density Microphone Controller capture-only DAI. It converts PDM microphone streams into PCM capture, configures PDM channel mapping from device tree, manages SINC/audio-filter parameters, exposes channel-map ALSA controls, and registers dmaengine PCM with a post-processing hook.

## Important APIs, Types, And Functions
- `struct mchp_pdmc` stores microphone mapping, regmap, pclk/gclk, DMA address data, enabled-channel mask, suspended IRQ mask, startup delay, mic count, SINC order, audio filter state, and `busy_stream`.
- ALSA controls: `"Audio Filter"`, `"SINC Filter Order"`, and `"Capture Channel Map"` through `mchp_pdmc_*_get/put` handlers.
- DAI ops: `mchp_pdmc_set_fmt`, `mchp_pdmc_startup`, `mchp_pdmc_hw_params`, `mchp_pdmc_trigger`, `mchp_pdmc_pcm_new`, and `mchp_pdmc_dai_probe`.
- `mchp_pdmc_dt_init()` parses `microchip,mic-pos` and optional `microchip,startup-delay-us`, rejecting invalid DS/edge combinations and duplicate microphones.
- `mchp_pdmc_process()` clears the channel index bits in DMA samples.
- Runtime PM handlers cache-only the regmap and enable/disable pclk/gclk.

## Control Flow
Probe parses microphone topology, maps registers, installs IRQ, initializes default audio filter and SINC order, enables runtime PM, registers dmaengine PCM and the capture DAI. Startup resets the IP and constrains channel count to the declared mic count. `hw_params` checks channel count, marks the stream busy, chooses the closest gclk OSR from the allowed set, programs MR/CFGR with filter, SINC order, DMA chunk, and mic edge/data selections, and sets DMA maxburst. Trigger start enables the selected PDM channels, waits the microphone startup delay, drains RHR and clears interrupts, then enables overrun/underrun interrupts. Stop/suspend disables interrupts and clears PDMCEN.

## State And Persistence
Control values are kept in `struct mchp_pdmc`; `busy_stream` prevents changing audio filter and SINC order while capture is configured. Channel-map state is stored in the `mchp_pdmc_std_chmaps` entries and reflected into CFGR. Regcache preserves register programming across runtime suspend/resume, but no state is persisted beyond the device lifetime.

## Dependencies And Integration Points
Uses `dt-bindings/sound/microchip,pdmc.h`, ASoC controls, dmaengine PCM, regmap, clk, runtime PM, and OF. The DAI accepts only PDM format and requires the CPU DAI to be bit-clock provider. DMA integration uses `snd_dmaengine_pcm_config.process` to scrub metadata bits.

## Risks
The control path writes CFGR in channel-map `get`, so status reads can change hardware. `busy_stream` is set in `hw_params` but is only cleared on remove in this file, so filter controls may remain busy after normal stream teardown unless higher-level component lifecycle resets them elsewhere. Gclk retuning temporarily disables the clock, making runtime-PM sequencing important. Startup delay defaults to 150 ms and directly affects capture latency. Incorrect `microchip,mic-pos` ordering will produce swapped channel maps even when capture works.

## Test Signals
Validate DT parsing failures for odd/duplicate/out-of-range `microchip,mic-pos`, capture at supported rates with 1 to 4 mics, channel-map ALSA control round trips, overrun/underrun IRQ warnings, suspend/resume with regcache sync, and DMA output with channel index byte cleared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-pdmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdifrx.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdifrx.c

## Purpose
Microchip S/PDIF receiver CPU DAI. It provides stereo capture from the S/PDIF RX holding register, exports IEC958 channel status, subcode, lock, signal, bad-format, and calculated-rate controls, and uses runtime PM plus regcache around the pclk/gclk-backed hardware block.

## Important APIs, Types, And Functions
- `struct mchp_spdifrx_ch_stat` and `struct mchp_spdifrx_user_data` store 192-bit blocks plus completions.
- `struct mchp_spdifrx_dev` persists DMA data, controls, mutex, regmap, clocks, and `trigger_enabled`.
- Regmap callbacks mark status/RHR as precious or volatile and constrain readable/writeable registers.
- IRQ handler `mchp_spdif_interrupt()` completes channel-status/user-data acquisitions and reports overruns.
- DAI ops are `mchp_spdifrx_dai_probe`, `mchp_spdifrx_dai_remove`, `mchp_spdifrx_trigger`, and `mchp_spdifrx_hw_params`.
- IEC958 controls use `mchp_spdifrx_cs_get`, `mchp_spdifrx_subcode_ch_get`, `mchp_spdifrx_ulock_get`, `mchp_spdifrx_badf_get`, `mchp_spdifrx_signal_get`, and `mchp_spdifrx_rate_get`.

## Control Flow
Probe maps MMIO, initializes regmap and IRQ, gets pclk/gclk, sets a default gclk minimum rate for signal queries before `hw_params`, enables runtime PM, sets capture DMA address/maxburst, and registers PCM/DAI. DAI probe resets the IP, writes default MR behavior, initializes completions, and installs controls. `hw_params` rejects playback and non-stereo capture, maps endian/data width, retunes the gclk minimum to rate times the hardware ratio, and writes MR while holding `mlock` and while not running. Trigger start enables overrun IRQ and RX; stop disables them.

## State And Persistence
Control caches hold last channel status and subcode data, updated either synchronously from registers or through IRQ completions while running. `trigger_enabled` is used to avoid misleading hardware status when clocks are on but receiver is disabled. Regcache preserves configuration through runtime suspend/resume; no user data is persisted across driver reload.

## Dependencies And Integration Points
Depends on ASoC, dmaengine PCM, regmap MMIO, runtime PM, clk, IRQ, and IEC958 ALSA control definitions. Device-tree compatible is `microchip,sama7g5-spdifrx`. Integration with user space is through PCM capture and volatile IEC958 PCM controls.

## Risks
The source contains `GENAMSK` in the validity-bit mask macro, which is a compile-time risk if not hidden by preprocessing context. Control reads can wait up to 100 ms for completions; absent or unstable S/PDIF input returns timeout. Gclk minimum rate must be valid before signal/rate controls are queried. The signal control briefly enables RX when not streaming, so it can perturb hardware state if called frequently.

## Test Signals
Build coverage should catch register-mask typos. Runtime testing should cover control reads with and without an incoming signal, capture format validation, gclk retuning per sample rate, overrun IRQ warnings, and runtime suspend/resume with controls after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdifrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdiftx.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdiftx.c

## Purpose
Microchip S/PDIF transmitter CPU DAI. It provides mono/stereo playback, programs S/PDIF channel status and user data, sets the generated clock to sample-rate times the TX ratio, and registers dmaengine PCM against the common data register.

## Important APIs, Types, And Functions
- `struct mchp_spdiftx_mixer_control` stores 192-bit channel status and user-data arrays protected by a spinlock.
- `struct mchp_spdiftx_dev` stores control state, DMA playback data, regmap, pclk/gclk, DAI format, and suspended IRQ mask.
- `mchp_spdiftx_channel_status_write()` and `mchp_spdiftx_user_data_write()` serialize software arrays into hardware registers.
- IRQ handler writes deferred status/user data at `CSRDY`/`UDRDY` and disables handled error/status interrupts.
- DAI ops: startup reset/FIFO clear, shutdown interrupt disable, trigger TX enable/disable, `hw_params`, and `hw_free`.
- IEC958 controls expose playback default/mask status and subcode read/write.

## Control Flow
Probe maps registers, requests IRQ, gets pclk/gclk, initializes the control lock and default channel status, enables runtime PM, sets DMA address/width, and registers PCM/DAI. Startup resets the IP and clears FIFO. `hw_params` rejects capture and active TX, chooses mono/dual mode, maxburst, byte width, endian, valid bits, AES3 sample frequency code, retunes gclk, writes channel status, and writes MR. Trigger start restores saved IRQ mask and enables underrun/overrun interrupts before enabling TX; stop/suspend saves and disables interrupts and disables TX. IEC958 control writes either update registers immediately or enable ready IRQs if TX is running.

## State And Persistence
Channel-status/user-data arrays persist in driver memory and are pushed to registers during control updates or ready interrupts. Runtime PM uses regcache and clocks; suspend stores the current interrupt mask. No state is persisted outside kernel memory.

## Dependencies And Integration Points
Uses ASoC, dmaengine PCM, regmap MMIO, runtime PM, clk, IRQ, and `sound/asoundef.h` IEC958 definitions. OF compatible is `microchip,sama7g5-spdiftx`.

## Risks
The file contains likely compile-sensitive defects: `GENAMSK` in the multichannel mask macro and a malformed `.access` initializer for the IEC958 playback mask control. Runtime retunes gclk by disabling and re-enabling it, so failures can leave the clock state changed. Deferred control writes depend on hardware ready IRQs while playback is running. Sample-rate mapping accepts some rates as "not indicated" and rejects others.

## Test Signals
Build tests are important for macro and initializer issues. Runtime tests should cover playback at all accepted rates/formats, IEC958 status/subcode writes while stopped and running, underrun/overflow IRQs, runtime suspend/resume, and mono versus stereo DMA burst behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mchp-spdiftx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mikroe-proto.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/mikroe-proto.c

## Purpose
Device-tree machine driver for the MikroElektronika PROTO AudioCODEC board using a WM8731 codec. It creates a single DAI link between a DT-specified I2S controller and codec, sets WM8731 sysclk to the fixed 12.288 MHz crystal, and declares basic headphone/microphone DAPM routing.

## Important APIs, Types, And Functions
- `snd_proto_init()` calls `snd_soc_dai_set_sysclk()` for `WM8731_SYSCLK_XTAL`.
- Static `snd_soc_card snd_proto` carries widgets/routes and receives a dynamic DAI link at probe.
- `snd_proto_probe()` parses `model`, `audio-codec`, `i2s-controller`, audio format, and clock-provider information.

## Control Flow
Probe requires an OF node, allocates one DAI link plus three components, binds codec/cpu/platform OF nodes, enforces the same bit-clock and frame-clock master phandle, computes `dai_fmt`, registers the card with devm cleanup, and releases OF references on all paths.

## State And Persistence
The global card object is populated at probe with a dynamically allocated single link. There is no persistent state beyond the card registration.

## Dependencies And Integration Points
Integrates WM8731 codec DAI `wm8731-hifi`, an arbitrary DT I2S controller, ASoC card parsing helpers, and DAPM. Compatible string is `mikroe,mikroe-proto`.

## Risks
Because `snd_proto` is static, multiple device instances would share card fields. Clock-provider parsing rejects split bit/frame masters. Missing DT phandles fail probe. The sysclk is fixed to board hardware and not negotiable.

## Test Signals
DT probe with valid and missing phandles, clock-provider mode variants, card name parsing, and `aplay`/`arecord` through WM8731 with expected DAPM pins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/mikroe-proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/sam9g20_wm8731.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/sam9g20_wm8731.c

## Purpose
Legacy AT91SAM9G20-EK machine driver for a WM8731 codec on SSC0. It wires a fixed I2S DAI link, sets codec MCLK to 12 MHz, optionally disables microphone capture, and reserves/releases the SSC audio function.

## Important APIs, Types, And Functions
- `at91sam9g20ek_wm8731_init()` sets `WM8731_SYSCLK_MCLK` and disables `"Int Mic"` unless `ENABLE_MIC_INPUT` is defined.
- `SND_SOC_DAILINK_DEFS(pcm)` binds default CPU/platform `at91rm9200_ssc.0` and codec `wm8731.0-001b`.
- `at91sam9g20ek_audio_probe()` parses `atmel,model`, `atmel,audio-routing`, `atmel,audio-codec`, and `atmel,ssc-controller`, then registers the card.

## Control Flow
Probe requires OF, calls `atmel_ssc_set_audio(0)`, updates static link components with OF nodes, registers the static card, and unwinds SSC reservation on error. Remove unregisters the card and calls `atmel_ssc_put_audio(0)`.

## State And Persistence
State is a static card/link modified during probe. SSC reservation is a platform-level side effect held until remove. No persistent storage is used.

## Dependencies And Integration Points
Depends on AT91 SSC support, `atmel-pcm`, `atmel_ssc_dai`, WM8731 codec, and DT bindings named with `atmel,*` properties. Compatible string is `atmel,at91sam9g20ek-wm8731-audio`.

## Risks
Hardcoded SSC index 0 and static card/link limit flexibility. Capture is compile-time disabled by default despite DAPM mic routes existing. Probe must correctly release OF references and SSC reservations on all failures.

## Test Signals
Probe/unprobe on DT systems, SSC reservation conflicts, playback-only exposure when mic input is disabled, WM8731 sysclk setting, and audio-routing parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/sam9g20_wm8731.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/sam9x5_wm8731.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/sam9x5_wm8731.c

## Purpose
AT91SAM9x5 WM8731 machine driver. It dynamically allocates an ASoC card and single DAI link, sets the codec XTAL sysclk to 12.288 MHz, uses DSP_A framing with codec clock provider, and reserves the SSC identified by the DT alias.

## Important APIs, Types, And Functions
- `struct sam9x5_drvdata` stores the selected SSC id.
- `sam9x5_wm8731_init()` sets `WM8731_SYSCLK_XTAL`.
- `sam9x5_wm8731_driver_probe()` allocates card/link/components, parses card name/routing and codec/SSC phandles, calls `atmel_ssc_set_audio`, and registers with devm cleanup.
- Remove releases the reserved SSC via `atmel_ssc_put_audio`.

## Control Flow
Probe validates OF, allocates all structures with devm, installs DAPM widgets, constructs the DAI link, parses phandles, derives `ssc_id` from `of_alias_get_id(cpu_np, "ssc")`, reserves the SSC, registers the card, then releases node references. Failure after SSC reservation unwinds it.

## State And Persistence
Card and DAI state are device-managed allocations; the only persistent side effect is SSC audio reservation until remove.

## Dependencies And Integration Points
Integrates WM8731 codec, Atmel SSC DAI, ASoC DT parsing, and OF aliasing. Compatible string is `atmel,sam9x5-wm8731-audio`.

## Risks
If the SSC alias is missing, `ssc_id` may be negative and is passed to `atmel_ssc_set_audio`. The driver assumes one codec and one SSC link. Error logging for failed SSC reservation prints arguments in a confusing order.

## Test Signals
DT aliases for SSC, card/routing parsing, probe failure cleanup, playback/capture through DSP_A, sysclk setting, and remove releasing the SSC id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/sam9x5_wm8731.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/tse850-pcm5142.c -->
# sources/distributed-fs/ceph-client/sound/soc/atmel/tse850-pcm5142.c

## Purpose
Machine driver for the Axentia TSE-850 board with a PCM5142 codec. It models board-level analog routing using DAPM widgets and GPIO-controlled relay/mixer controls, exposes analog output voltage selection through a regulator-backed DAPM enum, and creates one I2S playback link.

## Important APIs, Types, And Functions
- `struct tse850_priv` stores GPIO descriptors for `add`, `loop1`, `loop2`, the analog regulator, and cached control values.
- Control handlers `tse850_get/put_mux1`, `tse850_get/put_mux2`, `tse850_get/put_mix`, and `tse850_get/put_ana` bridge ALSA controls to GPIO/regulator state.
- `tse850_dt_init()` parses `axentia,cpu-dai` and `axentia,audio-codec`.
- `tse850_probe()` acquires GPIOs/regulator, enables regulator, and registers the static card.

## Control Flow
Probe allocates private state, attaches it to the card, resolves CPU/platform and codec OF nodes, initializes all GPIOs high with matching caches, enables the analog regulator, and registers the card. DAPM control changes immediately toggle relays/add path or set regulator voltage, then call the relevant DAPM update helpers. Remove unregisters the card and disables the analog regulator.

## State And Persistence
Relay and mixer states are cached in memory and initialized to high/loop/add enabled at probe. Regulator voltage is queried from hardware for reads. No persistent ALSA-control restore is implemented beyond standard user-space mixer restore.

## Dependencies And Integration Points
Depends on GPIO consumer API, regulator API, OF, ASoC DAPM, and the PCM512x codec DAI `pcm512x-hifi`. Compatible string is `axentia,tse850-pcm5142`.

## Risks
DAPM routes are explicitly noted as an imperfect model of physical relay routing. GPIO toggles happen outside deeper DAPM mixer power sequencing in `tse850_put_mix`. The analog regulator maps enum `"Low"` to 2 V for board-noise reasons, which may surprise generic control users. Static card/link objects are not multi-instance safe.

## Test Signals
Probe with missing GPIOs/regulator/phandles, mixer and mux ALSA controls changing actual GPIO levels, regulator voltage enum round trips, card unregister disabling regulator, and playback path through PCM5142.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/atmel/tse850-pcm5142.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/Kconfig

## Purpose
Kconfig menu for Alchemy Au1x ASoC support. It separates newer PSC/DBDMA-based Au12xx/Au13xx/Au1550 support, older Au1000/Au1500/Au1100 AC97C/I2SC plus DMA support, and DB1000/DB1200-family board machine drivers.

## Important APIs, Types, And Functions
This is configuration data, not C code. Key symbols are `SND_SOC_AU1XPSC`, `SND_SOC_AU1XPSC_I2S`, `SND_SOC_AU1XPSC_AC97`, `SND_SOC_AU1XAUDIO`, `SND_SOC_AU1XAC97C`, `SND_SOC_AU1XI2SC`, `SND_SOC_DB1000`, and `SND_SOC_DB1200`.

## Control Flow
Menu selection controls which objects are built. Board symbols depend on the relevant core family and select CPU DAI, codec, and codec-bus helpers. Hidden tristate DAI symbols are selected by boards or parent options rather than exposed directly.

## State And Persistence
Build-time state only through kernel `.config`.

## Dependencies And Integration Points
Depends on `MIPS_ALCHEMY` for both core driver families. AC97 variants select `AC97_BUS`, `SND_AC97_CODEC`, and `SND_SOC_AC97_BUS`; board symbols select codecs such as generic AC97, WM9712, and WM8731 I2C.

## Risks
Hidden symbols mean direct platform enablement relies on board selections or manual config fragments. `SND_SOC_DB1200` selects both AC97 and I2S paths, so unused drivers/codecs can be pulled into a build. These options are architecture-specific and mostly untested outside MIPS Alchemy.

## Test Signals
Kconfig dependency resolution for `allyesconfig`, module builds for selected board symbols, and ensuring selected codec/helper symbols match the Makefile object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/Makefile

## Purpose
Build rules for Au1x ASoC CPU DAI, DMA, and board drivers. It maps Kconfig symbols to module object names and their single C source files.

## Important APIs, Types, And Functions
Important object mappings include `snd-soc-au1xpsc-dbdma-y := dbdma2.o`, `snd-soc-au1xpsc-i2s-y := psc-i2s.o`, `snd-soc-au1xpsc-ac97-y := psc-ac97.o`, `snd-soc-au1x-dma-y := dma.o`, `snd-soc-au1x-ac97c-y := ac97c.o`, `snd-soc-au1x-i2sc-y := i2sc.o`, `snd-soc-db1000-y := db1000.o`, and `snd-soc-db1200-y := db1200.o`.

## Control Flow
The kernel build includes each module when its `CONFIG_*` variable is enabled. Board objects are separate from controller/DMA objects.

## State And Persistence
Build-time only; no runtime state.

## Dependencies And Integration Points
Integrates with `sound/soc/au1x/Kconfig` symbols and the top-level sound/soc build.

## Risks
Any Kconfig rename must be mirrored here. Board drivers may build without all runtime platform devices present, so load order is determined by platform registration rather than Makefile ordering.

## Test Signals
Module build for each symbol and `modinfo`/object naming consistency with platform-driver names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/ac97c.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/ac97c.c

## Purpose
ASoC CPU DAI driver for the older Au1000/Au1500/Au1100 integrated AC97C controller. It implements AC97 bus read/write/reset operations, exposes a stereo playback/capture DAI, and passes legacy DMA request IDs to the Au1x PCM DMA component.

## Important APIs, Types, And Functions
- Uses `struct au1xpsc_audio_data` from `psc.h` for MMIO, config, mutex, and DMA IDs.
- `au1xac97c_ac97_read/write/warm_reset/cold_reset` implement `snd_ac97_bus_ops`.
- `alchemy_ac97c_startup()` attaches DMA IDs to substreams.
- `au1xac97c_drvprobe()` maps resources, reads DMA resources, powers the AC97C, registers AC97 ops and DAI component.
- PM handlers disable/restore the controller.

## Control Flow
Probe allocates context, maps MEM resource manually, stores playback/capture DMA resource IDs, enables the AC97 clock, configures front L/R slots, registers bus ops and the DAI. AC97 reads/writes poll command-pending bits with retries under a mutex. Cold reset toggles reset and waits for codec-ready. Startup associates DMA IDs; DAI probe depends on the global workdata pointer.

## State And Persistence
Global `ac97c_workdata` means only one controller instance is supported. `ctx->cfg` persists slot configuration across reset/resume. Runtime state is MMIO register state plus driver memory.

## Dependencies And Integration Points
Depends on MIPS Alchemy headers, ASoC AC97 bus support, the separate `alchemy-pcm-dma` component, and platform MEM/DMA resources. Platform driver name is `alchemy-ac97c`.

## Risks
Global singleton state is not multi-device safe. Manual MMIO request/ioremap paths are older than devm_platform helpers. Polling loops and errata timing are sensitive to hardware behavior. AC97 read failure returns `0xffff`, which can be confused with real register data.

## Test Signals
AC97 codec reset/read/write under load, DMA ID propagation to `dma.c`, suspend/resume restoring `ctx->cfg`, module unload clearing global workdata, and timeout/debug logs on missing codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/ac97c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/db1000.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/db1000.c

## Purpose
Simple machine driver for DB1000/DB1500/DB1100 AC97 audio. It binds the `alchemy-ac97c` CPU DAI, generic AC97 codec, and `alchemy-pcm-dma.0` platform into one ASoC card.

## Important APIs, Types, And Functions
- `SND_SOC_DAILINK_DEFS(hifi)` defines CPU, codec, and platform components.
- `db1000_ac97_dai` and `db1000_ac97` define the static link/card.
- `db1000_audio_probe()` sets the card device and registers it with devm.

## Control Flow
Platform probe registers the static card. There is no custom remove because devm handles card cleanup.

## State And Persistence
Only static card/link definitions and ASoC registration state.

## Dependencies And Integration Points
Requires `alchemy-ac97c`, `ac97-codec`, and `alchemy-pcm-dma.0` platform devices/components. Platform driver name is `db1000-audio`.

## Risks
Hardcoded component names make the driver dependent on legacy platform-device numbering. No DT parsing or runtime routing is present.

## Test Signals
Card registration when all named components exist, probe deferral if components are absent, and AC97 playback/capture on DB1000-family boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/db1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/db1200.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/db1200.c

## Purpose
Machine driver bundle for DB1200/DB1300/DB1550 evaluation boards in AC97 and I2S modes. It selects one of six static cards based on the platform device id and binds PSC CPU DAIs, codecs, and PSC PCM DMA instances.

## Important APIs, Types, And Functions
- `db1200_pids` maps platform names to `driver_data` indices.
- Static cards/links cover DB1200 AC97, DB1300 AC97, DB1550 AC97, and three WM8731 I2S variants.
- `db1200_i2s_startup()` sets WM8731 XTAL sysclk to 12 MHz.
- `db1200_audio_probe()` chooses a card from `db1200_cards`.

## Control Flow
Probe obtains the platform id, indexes `db1200_cards`, sets `card->dev`, and registers the selected card with devm. I2S stream startup configures the codec sysclk before playback/capture.

## State And Persistence
All card/link data is static. There is no dynamic routing state beyond ASoC registration.

## Dependencies And Integration Points
Requires PSC AC97/I2S CPU DAIs (`au1xpsc_ac97.N`, `au1xpsc_i2s.N`), matching PSC PCM platforms (`au1xpsc-pcm.N`), generic AC97 or WM9712 codecs for AC97, and WM8731 I2C for I2S.

## Risks
Platform ids and hardcoded component instance numbers must match board setup exactly. Driver `.name` is `db1200-ac97` even though the id table includes all variants. DB1550 AC97 reuses the DB1200 AC97 link. No DT fallback exists.

## Test Signals
Probe each platform id, verify chosen card name and component names, run AC97 and I2S audio, and check WM8731 sysclk setup for I2S cards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/db1200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/dbdma2.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/dbdma2.c

## Purpose
ASoC PCM platform component for Au12x0/Au1550 PSC audio using Alchemy descriptor-based DMA. It manages DMA channel allocation, descriptor queueing, period callbacks, PCM pointer reporting, and managed DMA buffers.

## Important APIs, Types, And Functions
- `struct au1xpsc_audio_dmadata` stores DDMA id/channel, substream, ring position, DMA buffer addresses, period geometry, and current bit width.
- `au1x_pcm_dbdma_realloc()` allocates or reallocates a two-descriptor ring when sample bit width changes.
- `au1x_pcm_queue_tx/rx()` queue the next period as source or destination.
- Component ops are open, close, hw_params, prepare, trigger, pointer, and pcm_new.

## Control Flow
Open retrieves DMA IDs from the CPU DAI and installs hardware constraints. `hw_params` reallocates the DDMA channel if needed and initializes period state. Prepare resets the DMA channel and prequeues two periods. Trigger starts or stops DDMA. DMA callbacks advance period counters, notify ALSA with `snd_pcm_period_elapsed`, and queue the next period. Close frees the DDMA channel.

## State And Persistence
Per-stream runtime state is allocated as two `au1xpsc_audio_dmadata` entries on probe. It is reset per `hw_params`/close. No persistent state beyond DMA channel allocation.

## Dependencies And Integration Points
Depends on Alchemy DBDMA APIs, ASoC component PCM ops, and CPU DAIs that provide playback/capture DBDMA IDs. Platform driver name is `au1xpsc-pcm`.

## Risks
The code assumes a two-descriptor ring and queues exactly two periods before start. Bit width changes force channel reallocation because the DBDMA API cannot adjust existing descriptor width. Pointer state is callback-driven and can drift if callbacks are missed. Buffer minimum is large to reduce skips.

## Test Signals
Playback/capture with different sample widths, period elapsed cadence, pointer monotonicity/wrap, close freeing DDMA, and underrun behavior with small period sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/dbdma2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/dma.c

## Purpose
ASoC PCM component for older Au1000/Au1500/Au1100 audio using the legacy Alchemy DMA controller. It builds a circular software list of PCM periods, programs double-buffered DMA registers, handles DMA interrupts, and reports ALSA PCM position.

## Important APIs, Types, And Functions
- `struct pcm_period` describes a period start and end offset in a circular list.
- `struct audio_stream` stores substream, DMA channel, period list, and geometry.
- `au1000_setup_dma_link()` creates the circular period list from runtime DMA area.
- `au1000_dma_start/stop()` program and control DMA buffers.
- `au1000_dma_interrupt()` handles done flags, advances the list, reloads buffer addresses, and notifies ALSA.
- Component ops are `alchemy_pcm_open/close/hw_params/hw_free/trigger/pointer/pcm_new`.

## Control Flow
Open obtains DMA IDs from the CPU DAI, requests the Alchemy DMA channel, disables noncoherent mode, stores the substream, and sets hardware constraints. `hw_params` builds the circular period list. Trigger start initializes and starts double-buffered DMA; stop disables DMA. IRQ moves to the next period, reloads the completed DMA buffer, and calls `snd_pcm_period_elapsed`. Close frees the DMA channel.

## State And Persistence
Per-stream state lives in `struct alchemy_pcm_ctx` allocated at probe. Period nodes are heap-allocated on `hw_params` and freed on `hw_free`; DMA channel state is held while stream is open.

## Dependencies And Integration Points
Depends on legacy `au1000_dma.h` APIs, CPU DAIs that supply DMA request IDs, and continuous managed PCM buffers.

## Risks
Uses `virt_to_phys(runtime->dma_area)` rather than DMA mapping helpers, matching old contiguous-buffer assumptions. Pointer math depends on current period and DMA residue. The `case (~DMA_D0 & ~DMA_D1)` expression is suspicious as an empty-IRQ case and may not express intended flag matching. Memory allocation per period can fail for high period counts.

## Test Signals
Open/close DMA allocation, playback/capture period interrupts, pointer wrap, missed-interrupt branch, hw_params reconfiguration, and DMA residue correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/i2sc.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/i2sc.c

## Purpose
ASoC CPU DAI for the older Au1000/Au1500/Au1100 I2S controller. It configures the controller format, clock inversion, sample width, and direction-specific FIFO enable bits, and passes legacy DMA IDs to the PCM DMA component.

## Important APIs, Types, And Functions
- Uses `struct au1xpsc_audio_data` for MMIO/config/DMA IDs.
- `au1xi2s_set_fmt()` maps ASoC I2S/MSB/LSB and inversion flags into controller CFG bits; it only accepts CPU bit/frame-clock provider mode.
- `au1xi2s_hw_params()` maps sample bit widths 8/16/18/20/24 through `msbits_to_reg`.
- `au1xi2s_trigger()` powers the block on/off and toggles TX/RX FIFO enables.
- Probe maps MEM, reads DMA resources, and registers DAI/component.

## Control Flow
Probe maps controller registers and records DMA IDs. Startup attaches DMA data. `set_fmt` updates the cached config. `hw_params` updates sample-size bits. Trigger start enables clock/controller and writes the cached config with the relevant FIFO enabled; stop clears that FIFO and disables the block.

## State And Persistence
Format and sample size are cached in `ctx->cfg`. There is no hardware configuration until trigger start. Suspend/remove disables the controller.

## Dependencies And Integration Points
Integrates with `alchemy-pcm-dma` and older Alchemy platform MEM/DMA resources. Platform driver name is `alchemy-i2sc`.

## Risks
Requires the I2S controller to provide clocks and an external clock at 256x sample rate. Powering off on any stop may affect simultaneous opposite-direction streams. Format naming maps MSB to right-justified and LSB to left-justified per hardware bits, which is easy to misread.

## Test Signals
Format/inversion rejection tests, sample-width programming, DMA ID handoff, playback/capture trigger sequencing, suspend disabling clock, and full-duplex stop behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/i2sc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/psc-ac97.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/psc-ac97.c

## Purpose
ASoC CPU DAI for Au12x0/Au1550 PSC in AC97 mode. It implements PSC-specific AC97 codec read/write/reset, configures sample width and AC97 slots, starts/stops direction FIFOs, and registers a DAI instance named after the platform device.

## Important APIs, Types, And Functions
- Global `au1xpsc_ac97_workdata` backs AC97 bus ops.
- `au1xpsc_ac97_read/write/warm_reset/cold_reset` implement `snd_ac97_bus_ops` using PSC AC97 CDC/EVNT/RST registers.
- `au1xpsc_ac97_hw_params()` programs length and front L/R AC97 slots, rejecting mismatches while TX/RX are busy.
- `au1xpsc_ac97_trigger()` clears FIFO and starts/stops TX or RX.
- Probe selects PSC AC97 mode, records DMA IDs, clones the DAI template, and registers AC97 ops/component.

## Control Flow
Probe maps PSC registers, reads DMA resources, sets FIFO thresholds and device enable bits in `cfg`, preserves platform clock selection, switches PSC into AC97 mode, registers bus ops and DAI. Cold reset disables the PSC, asserts reset, enables PSC, waits for ready bits, and enables AC97. `hw_params` either validates an active configuration or disables/re-enables AC97 to apply new width/slot settings. Trigger start/stop manipulates PSC PCR and waits for busy clear on stop.

## State And Persistence
Configuration, rate, PM save registers, mutex, and DMA IDs live in `au1xpsc_audio_data`. The global workdata restricts practical use to one active AC97 PSC. Suspend saves `PSC_SEL` and disables PSC; resume restores selection and expects AC97 core reset to reinitialize.

## Dependencies And Integration Points
Depends on Alchemy PSC register definitions, ASoC AC97 bus, PSC DBDMA PCM, and platform DMA resources. Platform driver name is `au1xpsc_ac97`.

## Risks
Global AC97 bus context is not multi-instance safe despite DAI naming by device instance. Polling waits use busy loops and msleeps and can stall on broken hardware. Only front L/R slots are enabled. Resume relies on later AC97 reset rather than fully restoring hardware.

## Test Signals
Codec read/write retries, cold/warm reset on real PSC hardware, active-stream `hw_params` rejection, suspend/resume with codec rediscovery, and playback/capture FIFO stop wait.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/psc-ac97.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/psc-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/psc-i2s.c

## Purpose
ASoC CPU DAI for Au12x0/Au1550 PSC in I2S mode. It supports I2S, left-justified, and right/LSB-justified framing, provider/consumer clock modes, sample-width/rate validation, late hardware configuration when external clocks are present, and PSC DBDMA integration.

## Important APIs, Types, And Functions
- `au1xpsc_i2s_set_fmt()` converts ASoC format/inversion/provider flags to PSC I2S config bits.
- `au1xpsc_i2s_hw_params()` validates active configuration or caches sample length and rate.
- `au1xpsc_i2s_configure()` enables PSC, waits for ready, writes I2S config, and waits for device-ready.
- `au1xpsc_i2s_start/stop()` start or stop per-direction FIFOs and suspend PSC when both directions are idle.
- Probe maps resources, records DMA IDs, selects PSC I2S mode, clones the DAI template, and registers the component.

## Control Flow
Probe preserves clock selection, disables PSC, selects I2S mode, clears I2S config, and caches FIFO thresholds. Startup attaches DMA IDs. `hw_params` only programs cached fields unless the hardware is active, where mismatched width/rate is rejected. Trigger start configures the PSC if no stream is busy, clears FIFO, starts the requested direction, and waits for busy confirmation. Trigger stop stops one direction and powers down PSC if both directions are idle.

## State And Persistence
`cfg`, `rate`, PM save registers, and DMA IDs persist in driver memory. Hardware is deliberately configured late because codec-provided clocks may be absent until stream start.

## Dependencies And Integration Points
Depends on Alchemy PSC registers and the `au1xpsc-pcm` DBDMA platform. Platform driver name is `au1xpsc_i2s`.

## Risks
Comments say only PSC slave mode was originally supported, while code accepts both provider and consumer modes; board-clock realities need testing. Late configuration can time out if external clocks are missing. Only S16_LE and S24_LE are advertised. Full-duplex streams must use the same rate and sample width.

## Test Signals
Codec-master and PSC-master startup, timeout path when clocks are absent, rate/width mismatch rejection with one active stream, suspend/resume preserving PSC selection, and FIFO busy transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/psc-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/psc.h -->
# sources/distributed-fs/ceph-client/sound/soc/au1x/psc.h

## Purpose
Shared private header for Alchemy Au1x ASoC PSC/legacy audio drivers. It defines the common per-device state container and convenience macros for PSC/I2S/AC97 register offsets.

## Important APIs, Types, And Functions
- `struct au1xpsc_audio_data` holds MMIO base, cached config/rate, cloned DAI driver, PM save slots, mutex, and two DMA IDs.
- Macros such as `PSC_CTRL`, `PSC_SEL`, `I2S_STAT`, `I2S_CFG`, `I2S_PCR`, `AC97_CFG`, `AC97_CDC`, `AC97_EVNT`, `AC97_PCR`, `AC97_RST`, and `AC97_STAT` compute register addresses from `mmio`.

## Control Flow
No executable control flow; it is included by Au1x AC97/I2S/DMA/machine support files.

## State And Persistence
Defines the shared state shape. Actual state lifetime is controlled by each platform driver.

## Dependencies And Integration Points
Assumes Alchemy PSC offset macros are visible from architecture headers included by C files. It also requires ASoC DAI and mutex types through including translation units.

## Risks
The generic name `_AU1X_PCM_H` and shared struct are private conventions. Any field layout change affects multiple drivers. Register macros perform raw pointer arithmetic and rely on valid MMIO mapping.

## Test Signals
Build coverage of all Au1x files after header changes and runtime register access through AC97/I2S drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/au1x/psc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/Kconfig

## Purpose
Kconfig menu for Broadcom ASoC platform drivers. It exposes BCM2835 I2S, Cygnus audio, and BCM63XX Whistler I2S support.

## Important APIs, Types, And Functions
Configuration symbols are `SND_BCM2835_SOC_I2S`, `SND_SOC_CYGNUS`, and `SND_BCM63XX_I2S_WHISTLER`.

## Control Flow
Selecting a symbol controls which Makefile object bundle is built. BCM2835 depends on `ARCH_BCM2835 || COMPILE_TEST` and selects generic dmaengine PCM and regmap MMIO. Cygnus depends on `ARCH_BCM_CYGNUS || COMPILE_TEST`. BCM63XX selects regmap MMIO.

## State And Persistence
Build-time `.config` only.

## Dependencies And Integration Points
Integrates with the BCM Makefile and platform-specific DT/device drivers. BCM63XX does not declare an architecture dependency here, so platform code must provide the matching runtime pieces.

## Risks
Missing `COMPILE_TEST` or architecture dependencies on BCM63XX can expose build/runtime mismatches depending on the rest of the tree. Kconfig selects must match helper APIs used by the C files.

## Test Signals
Kconfig allmodconfig coverage, architecture-specific builds, and ensuring selected helper dependencies are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/Makefile

## Purpose
Build rules for Broadcom ASoC platform modules.

## Important APIs, Types, And Functions
Maps `SND_BCM2835_SOC_I2S` to `snd-soc-bcm2835-i2s.o`, `SND_SOC_CYGNUS` to `snd-soc-cygnus.o` from `cygnus-pcm.o cygnus-ssp.o`, and `SND_BCM63XX_I2S_WHISTLER` to `snd-soc-63xx.o` from `bcm63xx-i2s-whistler.o bcm63xx-pcm-whistler.o`.

## Control Flow
Kernel build includes each object bundle according to its `CONFIG_*` symbol.

## State And Persistence
Build-time only.

## Dependencies And Integration Points
Tightly matches `sound/soc/bcm/Kconfig` and expects the BCM63XX PCM companion file to provide symbols declared in `bcm63xx-i2s.h`.

## Risks
Object bundle membership is the link-time contract between BCM63XX I2S and PCM code; removing one side breaks unresolved symbols. Any config rename must be updated here.

## Test Signals
Module build/link for each Broadcom symbol and unresolved-symbol checks for `snd-soc-63xx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm2835-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/bcm2835-i2s.c

## Purpose
Broadcom BCM2835 I2S CPU DAI driver. It supports stereo playback/capture, standard and TDM slot configuration, clock-provider/consumer modes, FIFO/DMA setup, and dmaengine PCM registration for Raspberry Pi-style I2S hardware.

## Important APIs, Types, And Functions
- `struct bcm2835_i2s_dev` stores device, playback/capture DMA data, DAI format, TDM masks/slot width/frame length, regmap, clock state, and cached clock rate.
- Clock helpers `bcm2835_i2s_start_clock` and `bcm2835_i2s_stop_clock`.
- `bcm2835_i2s_clear_fifos()` stops directions, toggles FIFO clear bits, waits on SYNC, and restores state.
- DAI ops include set_fmt, set_bclk_ratio, set_tdm_slot, hw_params, prepare, trigger, startup, shutdown, and DAI probe.
- Regmap marks FIFO as precious and status/FIFO/interrupt/GRAY as volatile.

## Control Flow
Probe gets the clock, maps MMIO, initializes regmap, derives DMA bus address from DT `reg`, fills playback/capture DMA data with FIFO address, 32-bit bus width, burst 2, and PACK flags, then registers DAI and dmaengine PCM. Startup enables the PCM block and clears standby. `hw_params` returns early if TX or RX is already on; otherwise it derives slot/frame geometry, validates provider mode and data length, programs clock rate when CPU provides BCLK, computes RX/TX channel positions, writes RXC/TXC/MODE/DREQ/CS registers, and clears FIFOs. Trigger starts/stops the relevant direction and conditionally starts/stops the clock. Shutdown disables the module when both streams are inactive.

## State And Persistence
Driver memory holds chosen DAI/TDM format and clock state. Hardware registers hold the active frame/channel configuration and DMA thresholds. No persistent storage is used.

## Dependencies And Integration Points
Depends on ASoC, dmaengine PCM, regmap MMIO, clk, OF address parsing, and DT compatible `brcm,bcm2835-i2s`. Machine drivers use standard DAI format/TDM callbacks.

## Risks
FIFO clearing waits on SYNC and has a FIXME for slave mode, so slave-clock configurations may log sync errors. The driver is limited to two active channels even when TDM slots are configured. Early return from `hw_params` while a stream is active assumes the existing register setup is compatible. Manual DMA base parsing from DT may be wrong on address-translated buses. There are trailing-space style issues near register writes but no behavioral effect.

## Test Signals
Stereo playback/capture in master and slave modes, TDM slot masks with exactly two bits, FIFO clear after overrun/underrun, continuous-clock mode shutdown, clock-rate changes across sample rates, and DT DMA address correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm2835-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s-whistler.c -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s-whistler.c

## Purpose
Broadcom BCM63XX Whistler I2S CPU DAI. It configures separate TX/RX I2S blocks, coordinates which side generates the shared bus clock, sets sample clock rate, and delegates PCM/DMA registration to the companion BCM63XX PCM implementation.

## Important APIs, Types, And Functions
- Regmap callbacks `brcm_i2s_wr_reg`, `brcm_i2s_rd_reg`, and `brcm_i2s_volatile_reg` constrain register access.
- `bcm63xx_i2s_hw_params()` sets `i2sclk` to the requested sample rate.
- `bcm63xx_i2s_startup()` enables TX or RX data/clock bits, initializes IRQ thresholds, and chooses master/slave mode based on the opposite block.
- `bcm63xx_i2s_shutdown()` disables direction bits, restores IRQ thresholds, and hands master mode back to the other active block if needed.
- Probe maps registers, initializes regmap, disables pad loopback, registers the DAI, stores private state, and calls `bcm63xx_soc_platform_probe`.

## Control Flow
Probe allocates `bcm_i2s_priv`, gets `i2sclk`, maps MMIO, sets up regmap, disables pad loop loopback, registers the DAI, stores state, and registers the PCM platform. Startup is direction-specific: playback enables TX output/data/clock and chooses TX master only if RX is currently slave; capture mirrors the logic for RX. Shutdown disables the direction and may promote the other still-enabled direction to master before putting the stopped side back to slave.

## State And Persistence
State is in `bcm_i2s_priv` plus hardware registers. The header also reserves fields for substreams and DMA descriptors used by the companion PCM file. No persistence beyond device lifetime.

## Dependencies And Integration Points
Depends on regmap, clk, ASoC, `bcm63xx-i2s.h`, and companion functions `bcm63xx_soc_platform_probe/remove` linked from the BCM63XX PCM object. Compatible string is `brcm,bcm63xx-i2s`.

## Risks
`hw_params` sets the clock to the sample rate rather than an obvious bit-clock multiple; this may rely on clock-provider internals and should be checked on hardware. Master/slave arbitration is register-state based and sensitive to simultaneous stream startup/shutdown races. Only S32_LE stereo is advertised. Regmap write ranges include descriptor registers that the PCM side may also manipulate.

## Test Signals
Playback-only, capture-only, and full-duplex stream start/stop ordering; clock rate programming; master/slave handoff when one direction stops; pad loopback disable; and integration with companion PCM descriptor handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s-whistler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s.h

## Purpose
Shared private header for BCM63XX Whistler I2S and PCM support. It defines TX/RX register offsets, bit masks, descriptor FIFO constants, private device state, and prototypes for the companion PCM platform hooks.

## Important APIs, Types, And Functions
- Register macros cover `I2S_MISC_CFG`, TX/RX config, IRQ, descriptor FIFO, and config-2 master/slave registers.
- `struct bcm_i2s_priv` stores device, regmap, clock, playback/capture substreams, and DMA descriptor pointers.
- Externs `bcm63xx_soc_platform_probe()` and `bcm63xx_soc_platform_remove()` connect the I2S DAI driver to the PCM implementation.

## Control Flow
No executable code. It is the compile/link contract between `bcm63xx-i2s-whistler.c` and the companion PCM source.

## State And Persistence
Defines the in-memory device state used by the BCM63XX module; lifetime is owned by platform probe/remove.

## Dependencies And Integration Points
Requires ASoC/platform-device types from including C files and an `i2s_dma_desc` type supplied by the companion PCM code or other included definitions.

## Risks
Header changes can break both I2S and PCM sides. Descriptor pointer fields are opaque here, making ownership and allocation rules dependent on the companion implementation. Hardcoded register offsets must match the target BCM63XX IP block.

## Test Signals
Build/link of `snd-soc-63xx`, register access tests for TX/RX offsets, and runtime DMA descriptor allocation/free through the companion PCM driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/bcm/bcm63xx-i2s.h -->
