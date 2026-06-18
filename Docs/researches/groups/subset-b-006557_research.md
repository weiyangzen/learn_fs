<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-dma.c

## Purpose
ASoC platform/PCM DMA support for Socionext UniPhier AIO. It exposes the memory-ring side of the AIO engine to ALSA PCM and compressed-audio streams, maps the AIO register resource, requests the shared DMA interrupt, and registers a component with PCM and compress callbacks.

## Important APIs, Types, and Functions
The exported entry point is `uniphier_aiodma_soc_register_platform()`. Runtime callbacks are `uniphier_aiodma_open()`, `uniphier_aiodma_prepare()`, `uniphier_aiodma_trigger()`, `uniphier_aiodma_pointer()`, `uniphier_aiodma_mmap()`, and `uniphier_aiodma_new()`. IRQ flow is handled by `aiodma_irq()`, `aiodma_pcm_irq()`, and `aiodma_compr_irq()`. The component uses the `uniphier_aio_sub` state and helper APIs declared in `aio.h`, especially `aiodma_ch_set_param()`, `aiodma_rb_set_buffer()`, `aiodma_rb_sync()`, `aiodma_rb_set_threshold()`, and interrupt clear/test helpers.

## Control Flow, State, and Persistence
Registration maps the AIO DMA register block through a 32-bit MMIO regmap, obtains IRQ 0, registers a shared interrupt handler, and then registers the ASoC component. `open()` installs static hardware limits and a 256-byte buffer-step constraint. `prepare()` programs channel parameters and ring-buffer bounds under the substream lock. `trigger(START)` syncs ring pointers, enables the DMA channel, and marks `sub->running`; `STOP` clears `running` before disabling the channel. IRQ scanning walks every `chip->aios[i].sub[j]`, checks `running` plus hardware IRQ status, advances the threshold by one ALSA period/fragment, syncs read/write offsets, clears the IRQ, and notifies ALSA with `snd_pcm_period_elapsed()` or `snd_compr_fragment_elapsed()`. State persists in `sub->threshold`, `rd_offs`, `wr_offs`, PCM/compress stream pointers, and the hardware ring registers until stop/prepare rewrites them.

## Dependencies and Integration Points
Depends on ALSA SoC component APIs, ALSA compressed ops from `uniphier_aio_compress_ops`, Linux DMA mask/buffer APIs, platform resources, IRQs, and UniPhier AIO helper routines implemented in sibling files. DAI drivers in `aio-ld11.c` and `aio-pxs2.c` use the CPU DAI identity to reach the matching `uniphier_aio` instance via `uniphier_priv()`.

## Risks and Test Signals
Risks include threshold drift if `aiodma_rb_set_threshold()` fails repeatedly, shared IRQ scans across inactive substreams, hard-coded 33-bit DMA addressing, mmap write-combine assumptions, and pointer correctness depending on `aiodma_rb_sync()` maintaining coherent offsets. Test signals are PCM playback/capture period interrupts, compressed S/PDIF fragment interrupts, pointer monotonicity/wrap behavior, mmap playback, prepare/start/stop cycles without stale IRQs, and DMA mask success on target UniPhier systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-ld11.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-ld11.c

## Purpose
SoC description and platform driver binding for UniPhier LD11/LD20 AIO audio. It describes available ports, virtual-to-real hardware mappings, PLL availability, DAI capabilities, and OF compatibles for the shared UniPhier AIO core.

## Important APIs, Types, and Functions
The main data are `uniphier_aio_ld11[]`, `uniphier_aio_pll_ld11[]`, `uniphier_aio_dai_ld11[]`, `uniphier_aio_ld11_spec`, and `uniphier_aio_ld20_spec`. The platform driver calls common `uniphier_aio_probe()` and `uniphier_aio_remove()`. DAI ops are referenced from the shared AIO implementation: `uniphier_aio_i2s_ld11_ops`, `uniphier_aio_spdif_ld11_ops`, and `uniphier_aio_spdif_ld11_ops2`.

## Control Flow, State, and Persistence
Probe is delegated entirely to the common core with `of_device_id.data` selecting either LD11 or LD20 chip spec. The spec arrays persist as read-only topology: HDMI, SIF, line/EVEA, S/PDIF input, speaker, HDMI PCM, line/headphone output, SRC outputs, S/PDIF PCM, and compressed S/PDIF. LD20 reuses LD11 topology but sets `addr_ext = 1`, a DMA access workaround flag consumed by shared code.

## Dependencies and Integration Points
Depends on the common UniPhier AIO core, ALSA DAI descriptors, OF platform matching, and the AIO register/routing helpers behind the `uniphier_aio_*_ops`. It integrates with EVEA for line/headphone analog paths and with the AIO DMA component for ring-buffer transport.

## Risks and Test Signals
Risks are mostly declarative: wrong map/hardware IDs route audio through the wrong AIO block, DAI stream names must match the spec names used by the common core, and LD20 behavior depends on the single `addr_ext` difference. Test signals include OF match for `socionext,uniphier-ld11-aio` and `socionext,uniphier-ld20-aio`, DAI registration count, playback/capture on each exposed stream, SRC operation on `aio-epcmout2/3`, and compressed S/PDIF open on `aio-hieccompout1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-ld11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-pxs2.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-pxs2.c

## Purpose
SoC description and platform driver binding for UniPhier PXs2 AIO audio. It provides static routing, DAI, PLL, and compatible-table data for the shared AIO driver.

## Important APIs, Types, and Functions
The core declarations are `uniphier_aio_pxs2[]`, `uniphier_aio_pll_pxs2[]`, `uniphier_aio_dai_pxs2[]`, and `uniphier_aio_pxs2_spec`. The platform driver binds `socionext,uniphier-pxs2-aio` and delegates probe/remove to `uniphier_aio_probe()` and `uniphier_aio_remove()`. Referenced DAI ops are `uniphier_aio_i2s_pxs2_ops`, `uniphier_aio_spdif_pxs2_ops`, and `uniphier_aio_spdif_pxs2_ops2`.

## Control Flow, State, and Persistence
All behavior is data-driven. The common probe consumes the PXs2 spec to allocate AIO instances and DAIs for HDMI, line, auxiliary, S/PDIF, and compressed S/PDIF streams. The SW maps persist the ring-buffer, DMA channel, output/input interface, and real port selectors needed by runtime helper code.

## Dependencies and Integration Points
Depends on ALSA SoC DAI registration, OF matching, and common UniPhier AIO helpers. PXs2 differs from LD11 by exposing line/aux I2S paths and two S/PDIF output groups while omitting LD11 EVE/SRC entries.

## Risks and Test Signals
Risks include static route mismatches, duplicated S/PDIF hardware mappings between PCM and compress DAIs, and supported-rate declarations being narrower than hardware variants. Test signals are registration of seven DAIs, correct stream names, 48 kHz I2S playback/capture, HDMI S/PDIF PCM output, compressed output on both S/PDIF ports, and no regression in common AIO probe with `addr_ext = 0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-pxs2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-reg.h

## Purpose
Register-map contract for the UniPhier AIO block. It defines MMIO offsets and bitfields for system glue, AIO virtual maps, PLL/control registers, input/output ports, S/PDIF framing, volume/fade, sample-rate conversion, DMA channels, and DMA ring buffers.

## Important APIs, Types, and Functions
This header exports macro APIs rather than functions. Important families include `A2*MAPCTR*` virtual mapping registers, `A2APLLCTR*` PLL control, `IPORTMX*` input port configuration, `OPORTMX*` output/SRC/S/PDIF/volume registers, `PBINMX*` and `PBOUTMX*` memory format controls, `CDA2D_*` DMA channel and ring-buffer registers, and bitfield helpers such as `SBF_()`.

## Control Flow, State, and Persistence
The file has no runtime flow, but it defines persistent hardware state touched by the common UniPhier AIO implementation. Port setup uses format, rate, clock, master/slave, mute, slot, reset, and mask fields. DMA code uses ring begin/end/read/write pointers, IRQ enable/status bits, and channel address mode fields. These registers persist in hardware until reset, suspend, or explicit helper reconfiguration.

## Dependencies and Integration Points
It depends on Linux `BIT()`/`GENMASK()` definitions and on IEC61937 constants from `aio.h`. It is included by common AIO code and underpins the SoC data in `aio-ld11.c` and `aio-pxs2.c`.

## Risks and Test Signals
Risks include incorrect bit masks for high packed fields, confusing active-low power/reset naming, macro dependence on SoC-specific map selectors, and S/PDIF repetition constants needing exact IEC61937 framing. Test signals are register-write traces during I2S/S/PDIF/SRC setup, successful reset/unmask/fade operations, IRQ status/clear correctness, and bitfield validation against UniPhier hardware manuals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio.h -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/aio.h

## Purpose
Private interface for the UniPhier AIO sound driver. It centralizes stream names, hardware IDs, clock/PLL IDs, IEC61937 constants, data structures, and helper prototypes shared by UniPhier AIO DMA, DAI, port, SRC, and compressed-audio code.

## Important APIs, Types, and Functions
Key types are `enum ID_PORT_TYPE`, `enum ID_PORT_DIR`, `enum IEC61937_PC`, `struct uniphier_aio_selector`, `struct uniphier_aio_swmap`, `struct uniphier_aio_spec`, `struct uniphier_aio_pll`, `struct uniphier_aio_chip_spec`, `struct uniphier_aio_sub`, `struct uniphier_aio`, and `struct uniphier_aio_chip`. Helper prototypes include ring accounting, PLL/chip initialization, port/interface/SRC setup, DMA channel/ring setup, and `uniphier_aiodma_soc_register_platform()`.

## Control Flow, State, and Persistence
The header defines the state persisted across probe and stream runtime. `uniphier_aio_chip` owns platform resources, regmaps, reset/clock handles, active count, AIO instances, and PLL state. `uniphier_aio` stores per-DAI clock/PLL selections and two direction-specific `uniphier_aio_sub` objects. Each substream tracks PCM/compress pointers, parameters, mmap mode, running/setting flags, threshold, and 64-bit read/write origin/total counters protected by a spinlock.

## Dependencies and Integration Points
Depends on ALSA PCM/SoC/DAI declarations, Linux spinlocks/types, platform devices, and `aio-reg.h` users. It is the integration boundary among `aio-dma.c`, SoC descriptor files, common AIO DAI/control implementation, and the EVEA codec path.

## Risks and Test Signals
Risks include shared mutable substream fields touched from IRQ and PCM/compress callbacks, 64-bit offset wrap handling, aliasing compressed and PCM state in the same `uniphier_aio_sub`, and virtual mapping tables requiring exact SoC data. Test signals are build coverage across all UniPhier AIO objects, lockdep/IRQ testing around ring offsets, simultaneous playback/capture, compressed IEC61937 passthrough, and suspend/resume preserving chip and PLL state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/aio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/evea.c -->
# sources/distributed-fs/ceph-client/sound/soc/uniphier/evea.c

## Purpose
ASoC codec driver for the Socionext UniPhier EVEA ADC/DAC block. It provides line input, line output, headphone output, controls, DAPM widgets/routes, clock/reset sequencing, and MMIO regmap access.

## Important APIs, Types, and Functions
The driver-private state is `struct evea_priv`. Important helpers are `evea_set_power_state_on()`, `evea_set_power_state_off()`, `evea_update_switch_lin()`, `evea_update_switch_lo()`, `evea_update_switch_hp()`, `evea_update_switch_all()`, codec callbacks `evea_codec_probe()`, `evea_codec_suspend()`, `evea_codec_resume()`, and platform callbacks `evea_probe()`/`evea_remove()`. It defines DAPM widgets/routes, three switch controls, `soc_codec_evea`, and three DAIs: line1, hp1, and lo2.

## Control Flow, State, and Persistence
Probe allocates private state, gets `evea` and `exiv` clocks, gets shared resets, maps MMIO, creates a 32-bit regmap, enables clocks, deasserts resets in the required order, obtains/deasserts `adamv`, and registers the codec component. Component probe defaults line, line-out, and headphone switches to enabled and programs analog power/mute state. Suspend powers outputs down, asserts resets in reverse, and disables clocks; resume restores clocks/resets, powers the codec on, and reapplies switch state. Switch values persist in `evea_priv` and are replayed after resume.

## Dependencies and Integration Points
Depends on Linux clock/reset/regmap/platform APIs and ALSA SoC component, DAPM, and control APIs. It integrates with UniPhier AIO line/headphone DAIs through stream names such as `Line In 1`, `Line Out 1`, `Headphone 1`, and `Line Out 2`.

## Risks and Test Signals
Risks include register naming where power-down bits are set for active state, no regcache across suspend, ignored `regmap_update_bits()` return values, strict reset ordering because ADAMV hangs if EXIV reset is asserted, and switch controls bypassing richer DAPM event sequencing. Test signals are probe/resume reset order, switch get/put behavior, DAPM route visibility, 48 kHz S32_LE line capture/playback, headphone mute/unmute transitions, and suspend/resume audio recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/uniphier/evea.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/Kconfig

## Purpose
Kconfig menu for ST-Ericsson Ux500 ASoC support. It controls the base Ux500 audio option, MSP I2S platform support, DMA platform registration, and the MOP500 machine driver for Ux500 plus AB8500.

## Important APIs, Types, and Functions
Defines `SND_SOC_UX500`, `SND_SOC_UX500_PLAT_MSP_I2S`, `SND_SOC_UX500_PLAT_DMA`, and `SND_SOC_UX500_MACH_MOP500`. Selection relationships pull in generic DMAengine PCM, AB8500 codec support, MSP I2S, and Ux500 platform DMA for the MOP500 machine.

## Control Flow, State, and Persistence
There is no runtime state. Build-time selection gates which objects from the Ux500 Makefile are compiled and which dependencies must exist, notably `MFD_DB8500_PRCMU`, `AB8500_CORE`, and `AB8500_GPADC`.

## Dependencies and Integration Points
Integrates Ux500 audio with ALSA SoC, DB8500 PRCMU, AB8500 MFD/codec, and the generic DMAengine PCM framework.

## Risks and Test Signals
Risks include hidden `SND_SOC_UX500_PLAT_MSP_I2S` being selected only by machine drivers, platform DMA requiring generic DMAengine support, and legacy platform dependencies limiting compile coverage. Test signals are Kconfig dependency resolution, module build for each selected symbol, and successful auto-selection when enabling `SND_SOC_UX500_MACH_MOP500`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/Makefile

## Purpose
Build manifest for Ux500 ASoC objects. It groups the MSP DAI/I2S low-level driver, DMA PCM platform, and MOP500 machine driver into config-controlled modules.

## Important APIs, Types, and Functions
Defines composite objects `snd-soc-ux500-plat-msp-i2s-y`, `snd-soc-ux500-plat-dma-y`, and `snd-soc-ux500-mach-mop500-y`, then wires them to `CONFIG_SND_SOC_UX500_PLAT_MSP_I2S`, `CONFIG_SND_SOC_UX500_PLAT_DMA`, and `CONFIG_SND_SOC_UX500_MACH_MOP500`.

## Control Flow, State, and Persistence
No runtime behavior. Build composition determines link boundaries: `ux500_msp_dai.o` and `ux500_msp_i2s.o` share one module, `ux500_pcm.o` is the DMA platform module, and `mop500.o` plus `mop500_ab8500.o` form the machine module.

## Dependencies and Integration Points
Integrates with Kbuild and the Kconfig symbols in the same directory. The object grouping matters because the DAI file calls low-level MSP functions and the machine file calls AB8500 board helpers.

## Risks and Test Signals
Risks are missing object linkage if config symbols are changed or helper exports are removed. Test signals are `make M=sound/soc/ux500`, module alias generation, and no unresolved references among MOP500, MSP, and PCM objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/mop500.c -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/mop500.c

## Purpose
ASoC machine driver for MOP500 boards using Ux500 MSP I2S controllers and the AB8500 codec. It creates the sound card and two DAI links, then resolves device-tree phandles for CPU DAIs and codec.

## Important APIs, Types, and Functions
Defines DAI links `mop500_dai_links[]`, the `mop500_card`, `mop500_of_probe()`, `mop500_probe()`, `mop500_remove()`, and `mop500_of_node_put()`. It uses `mop500_ab8500_machine_init()` and `mop500_ab8500_ops` from the AB8500 machine helper.

## Control Flow, State, and Persistence
Platform probe stores the card device, resolves two `stericsson,cpu-dai` phandles and one `stericsson,audio-codec` phandle, rewrites DAI link component names to OF nodes, optionally parses `stericsson,card-name`, and registers the card. Remove unregisters the card, calls AB8500 cleanup, and drops OF node references. Card/link state persists in static structures updated during OF probe.

## Dependencies and Integration Points
Depends on ALSA SoC card registration, OF phandles, Ux500 MSP DAI names, AB8500 codec DAI names, and `mop500_ab8500.c` for hardware params, controls, and clock setup.

## Risks and Test Signals
Risks include static DAI link mutation making multiple instances unsafe, shared codec phandle refcount assumptions, no non-OF fallback despite static component names, and cleanup depending on successful earlier probe. Test signals are DT probe with both CPU DAI phandles, card registration, two PCM devices, AB8500 init on link 0, and clean remove without OF ref leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/mop500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/mop500_ab8500.c -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/mop500_ab8500.c

## Purpose
Machine-specific AB8500 glue for MOP500. It manages master-clock selection, board DAPM controls, stream startup/shutdown, TDM slot masks, codec/CPU DAI formatting, and shared rate/channel consistency across active DAIs.

## Important APIs, Types, and Functions
Exports `mop500_ab8500_ops[]`, `mop500_ab8500_machine_init()`, and `mop500_ab8500_remove()`. Key internals include `struct mop500_ab8500_drvdata`, `mop500_ab8500_set_mclk()`, ALSA enum get/put callbacks for `Master Clock Select`, `mop500_ab8500_startup()`, `mop500_ab8500_shutdown()`, `mop500_ab8500_hw_params()`, and `mop500_ab8500_hw_free()`.

## Control Flow, State, and Persistence
Machine init allocates card private data, obtains `sysclk`, `ulpclk`, and `intclk`, defaults `intclk` parent to ULPCLK, adds card controls, and disables most DAPM endpoint pins by default. Startup applies the selected MCLK parent. `hw_params()` locks global consistency state: if another DAI is active, rate and channel count must match, otherwise it records the first active stream's values and marks the CPU DAI ID in `mop500_ab8500_usage`. It selects normal mode for 1/2 channels and codec-only gated mode for 8 channels, sets DSP_A format, programs TX/RX slot masks, and calls `snd_soc_dai_set_tdm_slot()` on both CPU and codec DAIs. `hw_free()` clears the active bit; shutdown resets global TX/RX slot masks to defaults.

## Dependencies and Integration Points
Depends on ALSA SoC DAI/card/control/DAPM APIs, Linux clock framework, Ux500 MSP DAI support, Ux500 PCM, and AB8500 codec DAI behavior. Slot masks are tailored to AB8500 DSP_A TDM conventions and must match `ux500_msp_dai.c` slot handling.

## Risks and Test Signals
Risks include file-global `tx_slots`, `rx_slots`, usage/rate/channel state across cards, clock handles acquired with non-devm `clk_get()`, `mop500_ab8500_remove()` setting drvdata back to the same pointer after `clk_put()`, and early returns in `hw_params()` leaving usage bits set after a later DAI call failure. Test signals are MCLK control behavior, simultaneous link rate/channel rejection with `-EBUSY`, mono/stereo/8-channel TDM setup, DAPM pin switches, and clock parent transitions on stream startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/mop500_ab8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/mop500_ab8500.h -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/mop500_ab8500.h

## Purpose
Small internal interface between the MOP500 machine driver and its AB8500-specific helper implementation.

## Important APIs, Types, and Functions
Declares `extern const struct snd_soc_ops mop500_ab8500_ops[]`, `mop500_ab8500_machine_init(struct snd_soc_pcm_runtime *rtd)`, and `mop500_ab8500_remove(struct snd_soc_card *card)`.

## Control Flow, State, and Persistence
The header has no runtime state. It defines the compile-time contract that `mop500.c` uses to attach stream ops and initialize/cleanup AB8500 board controls and clocks.

## Dependencies and Integration Points
Depends on ALSA SoC types being visible through including C files. It links `mop500.c` to `mop500_ab8500.c`.

## Risks and Test Signals
Risks are limited to signature drift or missing type includes if included from a different context. Build coverage of `snd-soc-ux500-mach-mop500` is the primary test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/mop500_ab8500.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.c

## Purpose
ASoC CPU DAI driver for Ux500 MSP I2S/PCM controllers. It translates ASoC DAI format, TDM, sysclk, hw_params, startup, prepare, trigger, and shutdown operations into low-level MSP configuration and generic DMAengine PCM registration.

## Important APIs, Types, and Functions
Important helpers include `setup_pcm_multichan()`, `setup_frameper()`, `setup_pcm_framing()`, `setup_clocking()`, `setup_pcm_protdesc()`, `setup_i2s_protdesc()`, `setup_msp_config()`, and DAI callbacks `ux500_msp_dai_startup()`, `ux500_msp_dai_shutdown()`, `ux500_msp_dai_prepare()`, `ux500_msp_dai_hw_params()`, `ux500_msp_dai_set_dai_fmt()`, `ux500_msp_dai_set_tdm_slot()`, `ux500_msp_dai_set_dai_sysclk()`, `ux500_msp_dai_trigger()`, and `ux500_msp_dai_of_probe()`. Platform callbacks are `ux500_msp_drv_probe()` and `ux500_msp_drv_remove()`.

## Control Flow, State, and Persistence
Probe allocates `ux500_msp_i2s_drvdata`, initializes default format/slots/masks/master clock, gets `v-ape`, PRCMU QoS, clocks, low-level MSP MMIO state, registers one CPU DAI, then registers the DMAengine PCM platform. Startup enables the regulator and clocks. `hw_params()` constrains channels according to I2S versus DSP/TDM slot masks. `prepare()` builds `ux500_msp_config`, opens/programs the MSP, and raises APE OPP if generated bit clock exceeds 19.2 MHz. Trigger delegates start/stop to low-level MSP enable/disable. Shutdown closes the direction, lowers QoS, disables clocks, and disables the regulator.

## Dependencies and Integration Points
Depends on ALSA SoC DAI and DMAengine helpers, Linux regulators/clocks/platform/OF, DB8500 PRCMU QoS, low-level `ux500_msp_i2s.c`, and `ux500_pcm.c`. MOP500 calls its DAI ops through standard ASoC runtime operations.

## Risks and Test Signals
Risks include `setup_msp_config()` return ignored in `prepare()`, format/inversion acceptance mismatches between set_fmt and setup_clocking, only 16-bit TDM slots supported, PRCMU QoS name inconsistency (`ux500_msp_i2s` vs `ux500-msp-i2s`), and global low-level state allowing only one TX and one RX direction. Test signals are regulator/clock balance, I2S and DSP_A/B format setup, 1/2/8/16-slot TDM masks, DMA address initialization, channel constraints from masks, high-bitclock OPP changes, and repeated prepare/trigger/shutdown cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.h -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.h

## Purpose
Private DAI-level definitions for the Ux500 MSP ASoC driver. It defines supported rates/formats, frame-period constants, channel bounds, clock IDs, and the DAI driver-private state.

## Important APIs, Types, and Functions
Important constants are `UX500_I2S_RATES`, `UX500_I2S_FORMATS`, `FRAME_PER_*`, `UX500_MSP_MIN_CHANNELS`, `UX500_MSP_MAX_CHANNELS`, and `UX500_MSP_MASTER_CLOCK`. `struct ux500_msp_i2s_drvdata` stores low-level MSP pointer, regulator, DAI format, TDM masks/slots/slot width, master clock, clocks, and OPP constraint state. It also declares `ux500_msp_dai_set_data_delay()`.

## Control Flow, State, and Persistence
No runtime flow is implemented here. The struct fields persist from platform probe through stream setup and are mutated by DAI callbacks: format, slot masks, slot count/width, master clock, and OPP constraint status.

## Dependencies and Integration Points
Includes Linux types/spinlocks and `ux500_msp_i2s.h`. It is shared by MOP500 board code and the MSP DAI implementation.

## Risks and Test Signals
Risks include declarations without implementation (`ux500_msp_dai_set_data_delay()` is not defined in the researched file set), S16-only advertised formats despite some machine code accepting S32, and fixed frame-period constants needing hardware validation. Test signals are compile/link checks, hw_params constraints, and DAI format/rate negotiation on MOP500.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_dai.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.c

## Purpose
Low-level register driver for the Ux500 MSP I2S/PCM hardware. It programs protocol descriptors, bit clocks, multichannel masks, DMA enable bits, FIFOs, trigger state, and MMIO resource mapping for the higher-level ASoC DAI.

## Important APIs, Types, and Functions
External APIs are `ux500_msp_i2s_init_msp()`, `ux500_msp_i2s_cleanup_msp()`, `ux500_msp_i2s_open()`, `ux500_msp_i2s_close()`, and `ux500_msp_i2s_trigger()`. Internal helpers include `set_prot_desc_tx()`, `set_prot_desc_rx()`, `configure_protocol()`, `setup_bitclk()`, `configure_multichannel()`, `enable_msp()`, `flush_fifo_rx()`, `flush_fifo_tx()`, `disable_msp_rx()`, `disable_msp_tx()`, and `disable_msp()`.

## Control Flow, State, and Persistence
Initialization maps MMIO and records `tx_rx_addr` for DMA. `open()` rejects interrupt context, checks direction availability through `msp->dir_busy`, writes selected clock/sync/FIFO bits into `MSP_GCR`, calls `enable_msp()`, optionally marks loopback, flushes FIFOs, and sets `MSP_STATE_CONFIGURED`. `enable_msp()` programs TX/RX protocol registers, SRG divider/period, multichannel registers, DMA enable bits, I/O delay, and frame generation. Trigger start sets TX or RX enable; stop disables the matching side. Close disables the requested direction and, when no directions remain busy, clears the main MSP registers and returns to idle.

## Dependencies and Integration Points
Depends on Linux platform/MMIO/delay APIs, ALSA trigger constants, and register definitions from `ux500_msp_i2s.h`. It is called exclusively by `ux500_msp_dai.c`, which supplies protocol and clock configuration derived from ASoC.

## Risks and Test Signals
Risks include no locking around `dir_busy` and register state, `configure_protocol()` return ignored inside `enable_msp()`, division by zero or invalid divider if frame parameters are wrong, shared TX/RX close logic bug where `disable_rx = dir & MSP_DIR_TX`, and direct `writel()` sequencing requiring hardware timing. Test signals are TX/RX busy rejection, FIFO flush behavior, generated bit clock accuracy, multichannel TDM mask writes, stop/close clearing registers for TX-only and RX-only cases, and underrun/overrun-free DMA streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.h

## Purpose
Register, bitfield, enum, and structure contract for the Ux500 MSP I2S/PCM controller. It describes the hardware register layout and the in-memory configuration consumed by `ux500_msp_i2s.c`.

## Important APIs, Types, and Functions
Defines register offsets such as `MSP_DR`, `MSP_GCR`, `MSP_TCF`, `MSP_RCF`, `MSP_SRG`, `MSP_DMACR`, interrupt/multichannel registers, bit masks for global config, protocol config, FIFO flags, DMA and interrupt bits, plus enums for protocol, phase, frame/element length, delay, edge, companding, direction, data size, state, and RX comparison mode. Important structs are `msp_multichannel_config`, `msp_protdesc`, `ux500_msp_config`, and `ux500_msp`.

## Control Flow, State, and Persistence
The header implements no flow, but `ux500_msp_config` is the transient setup object for each `open()`, while `ux500_msp` is persistent low-level state storing MMIO base, DMA data register address, MSP state, direction busy mask, loopback flag, and computed bit clock.

## Dependencies and Integration Points
Depends on Linux platform-device declarations. It is included by both the DAI layer and low-level register programming layer, and indirectly shapes MOP500 TDM behavior.

## Risks and Test Signals
Risks include dense bitfield macros where shift/mask mistakes are hard to diagnose, duplicated direction enums (`msp_direction` and `i2s_direction_t`) with different names, legacy spelling/semantic quirks, and fixed FIFO/register assumptions. Test signals are compile coverage, register dump comparison after known configurations, bitclock/frame-period validation, and TX/RX/multichannel interrupt behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_msp_i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.c

## Purpose
Generic DMAengine PCM platform glue for Ux500 MSP DAIs. It registers an ASoC DMAengine PCM device and adapts ALSA hw_params into DMA slave configuration for MSP transmit/receive.

## Important APIs, Types, and Functions
Exports `ux500_pcm_register_platform()` and `ux500_pcm_unregister_platform()`. The main callback is `ux500_pcm_prepare_slave_config()`, installed in `ux500_dmaengine_of_pcm_config`.

## Control Flow, State, and Persistence
Register calls `snd_dmaengine_pcm_register()` with a prepare callback. During hw_params, the prepare callback retrieves CPU DAI DMA data, translates hw_params with `snd_hwparams_to_dma_slave_config()`, forces 4-burst and 2-byte bus widths, and sets either destination or source address to the MSP data register. Unregister removes the DMAengine PCM platform.

## Dependencies and Integration Points
Depends on ALSA SoC, PCM params, DMAengine PCM helpers, and DMA data initialized by `ux500_msp_dai_of_probe()`. It is registered from `ux500_msp_drv_probe()`.

## Risks and Test Signals
Risks include fixed 2-byte bus width despite stream format negotiation, hard-coded maxburst of 4, no custom channel filter, and reliance on CPU DAI DMA data existing. Test signals are DMA slave config for playback/capture, working cyclic DMA through MSP data register, buffer/period limits from generic DMAengine, and clean register/unregister on platform probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.h

## Purpose
Internal header for Ux500 PCM platform registration.

## Important APIs, Types, and Functions
Declares `ux500_pcm_register_platform(struct platform_device *pdev)` and `ux500_pcm_unregister_platform(struct platform_device *pdev)`.

## Control Flow, State, and Persistence
No runtime behavior. It provides the contract for the MSP DAI platform driver to register and unregister the DMAengine PCM platform.

## Dependencies and Integration Points
Includes page and workqueue headers and relies on `struct platform_device` being visible to includers. Used by `ux500_msp_dai.c`, `mop500.c`, and `mop500_ab8500.c`.

## Risks and Test Signals
Risks are minimal, mainly include hygiene and signature drift. Build coverage of Ux500 MSP and MOP500 modules is the test signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ux500/ux500_pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/xilinx/Kconfig

## Purpose
Kconfig menu for Xilinx ASoC soft-IP audio drivers: I2S, audio formatter PCM, and S/PDIF.

## Important APIs, Types, and Functions
Defines `SND_SOC_XILINX_I2S`, `SND_SOC_XILINX_AUDIO_FORMATTER`, and `SND_SOC_XILINX_SPDIF`, each tristate with user-facing help text.

## Control Flow, State, and Persistence
No runtime behavior. Build-time selections decide which Xilinx platform/component drivers are compiled.

## Dependencies and Integration Points
The options live under an ASoC architecture menu and integrate with Kbuild entries in the sibling Makefile. They do not select common dependencies explicitly, so source files rely on broader ASoC and platform support.

## Risks and Test Signals
Risks include missing dependency/select clauses for clocks, OF, or regmap expectations and help text that describes IP directions ambiguously. Test signals are allmodconfig/allyesconfig builds and module loading for each selected driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/xilinx/Makefile

## Purpose
Kbuild manifest for Xilinx ASoC driver modules.

## Important APIs, Types, and Functions
Maps `xlnx_i2s.o`, `xlnx_formatter_pcm.o`, and `xlnx_spdif.o` into `snd-soc-xlnx-i2s.o`, `snd-soc-xlnx-formatter-pcm.o`, and `snd-soc-xlnx-spdif.o`, controlled by their Kconfig symbols.

## Control Flow, State, and Persistence
No runtime state. It establishes one source file per module.

## Dependencies and Integration Points
Integrates Xilinx audio files with Linux Kbuild and the Kconfig options in the same directory.

## Risks and Test Signals
Risks are limited to object-name drift or config rename mismatches. Test signals are module builds for all three Xilinx drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_formatter_pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_formatter_pcm.c

## Purpose
ASoC PCM platform driver for Xilinx audio formatter IP. It controls MM2S playback and S2MM capture formatter engines, manages PCM buffers, period interrupts, AES channel-status parsing, and formatter-specific hw_params.

## Important APIs, Types, and Functions
Key structs are `xlnx_pcm_drv_data` and `xlnx_pcm_stream_param`. Important functions include `xlnx_parse_aes_params()`, `xlnx_formatter_pcm_reset()`, `xlnx_formatter_disable_irqs()`, IRQ handlers `xlnx_mm2s_irq_handler()` and `xlnx_s2mm_irq_handler()`, component callbacks `xlnx_formatter_set_sysclk()`, `xlnx_formatter_pcm_open()`, `xlnx_formatter_pcm_close()`, `xlnx_formatter_pcm_pointer()`, `xlnx_formatter_pcm_hw_params()`, `xlnx_formatter_pcm_trigger()`, `xlnx_formatter_pcm_new()`, and platform probe/remove.

## Control Flow, State, and Persistence
Probe enables `s_axi_lite_aclk`, maps the formatter registers, reads core configuration to detect MM2S/S2MM engines, resets present engines, disables interrupts, requests named IRQs, stores driver data, and registers the ASoC component. Open validates engine presence, allocates per-stream private data, reads format/channel/xfer-mode limits, installs PCM constraints, enables IOC IRQs, and stores active substream pointers for IRQ callbacks. Hw_params validates channels, programs playback MCLK multiplier if sysclk is known, optionally logs AES RX parameters, writes DMA buffer address, sample width, active channels, period configuration, and bytes-per-channel. Trigger toggles DMA enable; pointer reads transfer count. Close resets the stream engine, disables IRQs, and frees stream state.

## Dependencies and Integration Points
Depends on ALSA SoC component PCM APIs, managed PCM buffers, Linux MMIO/platform IRQ/clock APIs, and IEC958 channel-status definitions. It pairs with Xilinx I2S/SPDIF DAIs in machine graphs as the PCM platform component.

## Risks and Test Signals
Risks include memory leak on `open()` constraint failure after allocating `stream_data`, not clearing old data-width/active-channel bits before ORing new values, close returning success even if reset failed, active substream pointers not cleared on close, fixed two-channel PCM hardware despite reading channel limits, and reliance on named IRQs. Test signals are MM2S/S2MM detection, reset timeout handling, period IRQs, pointer wrap behavior, sysclk/rate divisibility, 64-byte period/buffer alignment, AES_TO_PCM logging, and playback/capture start/stop cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_formatter_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_i2s.c

## Purpose
ASoC DAI driver for Xilinx I2S transmitter and receiver soft IP. It programs serial clock divisors, channel enable registers, core enable state, and fixed playback/capture DAI capabilities from device-tree properties.

## Important APIs, Types, and Functions
Driver state is `struct xlnx_i2s_drv_data`. DAI operations are `xlnx_i2s_set_sclkout_div()`, `xlnx_i2s_set_sysclk()`, `xlnx_i2s_startup()`, `xlnx_i2s_hw_params()`, and `xlnx_i2s_trigger()`. Platform probe is `xlnx_i2s_probe()`.

## Control Flow, State, and Persistence
Probe maps registers, reads `xlnx,num-channels` and `xlnx,dwidth`, determines 16- or 24-bit formats, chooses playback or capture DAI based on compatible string, reads whether LRCLK is 32-bit, stores private data, and registers one DAI. `set_sysclk()` stores the source clock and builds a rational rate constraint. Startup applies that constraint if present. Hw_params computes and writes SCLK divider when sysclk is known, then writes per-stereo-pair channel registers. Trigger enables or disables the core control bit.

## Dependencies and Integration Points
Depends on Linux OF/platform/MMIO APIs and ALSA SoC DAI constraint helpers. It integrates with Xilinx formatter PCM or other platform components through machine-card links.

## Risks and Test Signals
Risks include only supporting fixed channel count from DT, using `channels *= 2` semantics that must match IP documentation, possible stale control bits when writing only enable on trigger, no remove/reset path, and rate constraints depending on previously configured data width/channel state. Test signals are DT property validation, transmitter and receiver compatible matching, divisor calculation for 32-bit LRCLK and data-width LRCLK modes, channel register programming for multichannel IP, and trigger start/stop producing clean I2S clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_spdif.c

## Purpose
ASoC DAI driver for Xilinx S/PDIF soft IP. It supports either transmit or receive mode, configures clock division, enables/disables the core, handles RX channel-status interrupts, and waits for stream detection before capture starts.

## Important APIs, Types, and Functions
Driver state is `struct spdif_dev_data`. Key functions are `xlnx_spdifrx_irq_handler()`, `xlnx_spdif_startup()`, `xlnx_spdif_shutdown()`, `xlnx_spdif_hw_params()`, `rx_stream_detect()`, `xlnx_spdif_trigger()`, and `xlnx_spdif_probe()`. It defines separate DAI drivers `xlnx_spdif_tx_dai` and `xlnx_spdif_rx_dai`.

## Control Flow, State, and Persistence
Probe enables `s_axi_aclk`, maps registers, reads `xlnx,spdif-mode`, selects TX DAI if nonzero or RX DAI plus IRQ/waitqueue if zero, reads `xlnx,aud_clk_i`, registers the component, and soft-resets the core. Startup flushes the FIFO and enables channel-status/global IRQs for capture. Hw_params derives a clock config code from `aud_clk_i / (2 channels * 32 AES bits * rate)` and writes it into control. Trigger start enables the core and, for capture, waits up to 40 ms for channel-status IRQ; stop clears enable. Shutdown soft-resets the core.

## Dependencies and Integration Points
Depends on ALSA SoC DAI APIs, Linux clock/MMIO/OF/platform IRQ/waitqueue APIs, and a machine graph that pairs the DAI with a PCM platform such as Xilinx formatter.

## Risks and Test Signals
Risks include RX stream detection blocking trigger and returning `-EINVAL` for absent status, limited accepted clock divisors, no explicit global IRQ disable on shutdown, boolean interpretation of `xlnx,spdif-mode`, and control writes depending on reset defaults. Test signals are TX and RX probe modes, allowed rates from 32 kHz to 192 kHz, clock divisor validation, RX channel-status IRQ wakeup, FIFO flush, and start/stop/reset cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xilinx/xlnx_spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xtensa/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/xtensa/Kconfig

## Purpose
Kconfig menu for Xtensa XTFPGA ASoC I2S controller support.

## Important APIs, Types, and Functions
Defines `SND_SOC_XTFPGA_I2S`, a tristate option that selects `REGMAP_MMIO` and enables the XTFPGA I2S master driver.

## Control Flow, State, and Persistence
No runtime behavior. Build-time selection controls whether `xtfpga-i2s.c` is compiled.

## Dependencies and Integration Points
Integrates Xtensa FPGA audio support with ASoC and regmap MMIO infrastructure. Users must also select suitable codec and machine-card pieces outside this file.

## Risks and Test Signals
Risks are sparse dependency declaration and relying on users to enable the rest of the audio subsystem. Test signals are Kconfig resolution and module build with `REGMAP_MMIO` selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xtensa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xtensa/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/xtensa/Makefile

## Purpose
Kbuild manifest for the Xtensa XTFPGA I2S ASoC module.

## Important APIs, Types, and Functions
Builds `snd-soc-xtfpga-i2s.o` from `xtfpga-i2s.o` under `CONFIG_SND_SOC_XTFPGA_I2S`.

## Control Flow, State, and Persistence
No runtime behavior. It provides a single-module build mapping.

## Dependencies and Integration Points
Integrates the Xtensa I2S source with Kbuild and the local Kconfig symbol.

## Risks and Test Signals
Risks are limited to config/object rename drift. Test signal is successful module build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xtensa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xtensa/xtfpga-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/xtensa/xtfpga-i2s.c

## Purpose
ASoC I2S master and PIO PCM driver for Cadence/Xtensa XTFPGA I2S hardware. It provides playback-only FIFO feeding, interrupt-driven period notification, runtime PM clock control, and DAI format/hw_params setup.

## Important APIs, Types, and Functions
Driver state is `struct xtfpga_i2s`. Generated FIFO writers are `xtfpga_pcm_tx_1x16()`, `xtfpga_pcm_tx_2x16()`, `xtfpga_pcm_tx_1x32()`, and `xtfpga_pcm_tx_2x32()`. Key helpers/callbacks include `xtfpga_pcm_push_tx()`, `xtfpga_pcm_refill_fifo()`, `xtfpga_i2s_threaded_irq_handler()`, DAI callbacks `xtfpga_i2s_startup()`, `xtfpga_i2s_hw_params()`, `xtfpga_i2s_set_fmt()`, PCM callbacks `xtfpga_pcm_open()`, `xtfpga_pcm_close()`, `xtfpga_pcm_hw_params()`, `xtfpga_pcm_trigger()`, `xtfpga_pcm_pointer()`, `xtfpga_pcm_new()`, runtime PM callbacks, and platform probe/remove.

## Control Flow, State, and Persistence
Probe maps registers, creates a regmap, gets the clock, initializes config/status/mask registers, requests a threaded shared IRQ, registers component/DAI, and enables runtime PM. DAI hw_params sets sample resolution, programs MCLK to 256 * rate, computes I2S clock ratio, and chooses FIFO interrupt watermarks based on period size. PCM hw_params selects the PIO writer for channel count and format. Trigger start resets `tx_ptr`, publishes the substream with RCU, and refills the FIFO; stop clears the RCU pointer. IRQ handling validates enabled status, estimates FIFO level from level/underrun bits, calls `snd_pcm_period_elapsed()`, refills FIFO, adjusts interrupt masks, and toggles TX/IRQ enable. Close uses `synchronize_rcu()` before userspace can free stream state.

## Dependencies and Integration Points
Depends on ALSA SoC DAI/component/PCM APIs, Linux regmap MMIO, clocks, IRQs, runtime PM, and OF platform matching. It uses managed PCM buffers but transfers samples by programmed I/O rather than DMA.

## Risks and Test Signals
Risks include PIO throughput limits, approximate FIFO level accounting, interrupt masking complexity around underrun recovery, no capture support, RCU pointer correctness, and ratio math relying on supported 16/32-bit mono/stereo formats. Test signals are runtime PM clock balance, 8-96 kHz playback, mono/stereo 16/32-bit FIFO writes, underrun recovery, period elapsed cadence, pointer wrap behavior, and remove clearing config/interrupt registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/xtensa/xtfpga-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sound_core.c -->
# sources/distributed-fs/ceph-client/sound/sound_core.c

## Purpose
Core sound class registration plus optional legacy OSS sound core. The common part creates the `sound` device class used by ALSA and OSS devices. The OSS part allocates legacy `SOUND_MAJOR` minors, creates `/dev/sound/*` devices, and dispatches opens to registered subdriver file operations or module autoload aliases.

## Important APIs, Types, and Functions
Exports `sound_class`. With `CONFIG_SOUND_OSS_CORE`, exports `register_sound_special_device()`, `register_sound_special()`, `register_sound_mixer()`, `register_sound_dsp()`, `unregister_sound_special()`, `unregister_sound_mixer()`, and `unregister_sound_dsp()`. Important internals are `struct sound_unit`, `sound_insert_unit()`, `sound_remove_unit()`, `__sound_insert_unit()`, `__sound_remove_unit()`, `__look_for_unit()`, and `soundcore_open()`.

## Control Flow, State, and Persistence
`init_soundcore()` initializes optional OSS core then registers `sound_class`; cleanup reverses that. OSS mode optionally preclaims all SOUND_MAJOR minors via `register_chrdev()` depending on `preclaim_oss`. Registered units are stored in ordered linked lists by minor-chain modulo 16 under `sound_loader_lock`. Device registration chooses a minor, optionally registers a one-minor char device when not preclaiming, and creates a class device. Open maps audio/dsp16 minors back to the DSP chain, looks up the registered unit, optionally requests legacy `sound-slot-*`, `sound-service-*`, and standard char-major modules, replaces file ops with the subdriver ops, and calls the subdriver open.

## Dependencies and Integration Points
Depends on Linux device class, chrdev, module autoloading, spinlocks, SOUND_MAJOR, and file-operation replacement APIs. It is the compatibility boundary used by OSS drivers and ALSA OSS emulation while sharing the common `sound` class with modern sound devices.

## Risks and Test Signals
Risks include legacy preclaim behavior blocking alternate OSS implementations, list/chrdev races handled by retry only in non-preclaim mode, device-create return ignored, minor-chain aliasing for dsp/audio/dspW, and reliance on subdriver module lifetime. Test signals are class registration at subsys init, `/dev/snd/*` devnode naming for non-SOUND_MAJOR devices, OSS mixer/DSP/special register/unregister, preclaim and non-preclaim open autoload behavior, and open dispatch to replacement fops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sound_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/Kconfig -->
# sources/distributed-fs/ceph-client/sound/sparc/Kconfig

## Purpose
Kconfig menu for Sun SPARC-specific ALSA sound devices.

## Important APIs, Types, and Functions
Defines `SND_SPARC`, `SND_SUN_AMD7930`, `SND_SUN_CS4231`, and `SND_SUN_DBRI`. Device options select ALSA PCM and, for CS4231, ALSA timer support.

## Control Flow, State, and Persistence
No runtime flow. Build-time selection gates SPARC-only sound drivers, with `SND_SPARC` defaulting to yes on SPARC.

## Dependencies and Integration Points
Depends on `SPARC`; AMD7930 and DBRI additionally depend on `SBUS`. It integrates with the local SPARC sound Makefile.

## Risks and Test Signals
Risks include old SBUS-only dependencies limiting coverage and default-y exposure on SPARC. Test signals are SPARC allmodconfig builds and expected module names `snd-sun-amd7930`, `snd-sun-cs4231`, and `snd-sun-dbri`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/Makefile -->
# sources/distributed-fs/ceph-client/sound/sparc/Makefile

## Purpose
Kbuild manifest for SPARC ALSA sound drivers.

## Important APIs, Types, and Functions
Builds `snd-sun-amd7930.o`, `snd-sun-cs4231.o`, and `snd-sun-dbri.o` from `amd7930.o`, `cs4231.o`, and `dbri.o` under their Kconfig symbols.

## Control Flow, State, and Persistence
No runtime behavior. The file maps config symbols to module objects.

## Dependencies and Integration Points
Integrates the SPARC sound source files with Kbuild and the Kconfig menu in the same directory.

## Risks and Test Signals
Risks are object/config drift. Test signal is successful SPARC sound module build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/amd7930.c -->
# sources/distributed-fs/ceph-client/sound/sparc/amd7930.c

## Purpose
ALSA low-level driver for AMD7930/Am79C30 audio hardware found on older Sun SPARC systems. The chip provides mono 8 kHz A-law or mu-law audio over an ISDN-oriented B-channel interface, so the driver implements pseudo-DMA byte transfer in the interrupt handler plus simple mixer controls.

## Important APIs, Types, and Functions
Driver state is `struct snd_amd7930`; hardware indirect state is `struct amd7930_map`. Important helpers are `amd7930_idle()`, `amd7930_enable_ints()`, `amd7930_disable_ints()`, `__amd7930_write_map()`, `__amd7930_update_map()`, `snd_amd7930_interrupt()`, PCM trigger/prepare/pointer/open/close callbacks, `snd_amd7930_pcm()`, mixer callbacks `snd_amd7930_get_volume()`/`snd_amd7930_put_volume()`, `snd_amd7930_mixer()`, `snd_amd7930_free()`, `snd_amd7930_create()`, `amd7930_sbus_probe()`, module init, and module exit.

## Control Flow, State, and Persistence
Module init registers a platform driver matching OF nodes named `audio`. Probe allocates an ALSA card, maps SBUS registers, idles the chip, requests a shared IRQ, enables interrupts, initializes gain state and MAP registers, configures the mux to route audio channel Ba to Bb, creates PCM and mixer devices, registers the card, and links it into a module-global list for exit cleanup. Playback/capture prepare sets pseudo-DMA pointers over the ALSA buffer, sets the active flag, and updates A-law/mu-law mode. Trigger start/stop toggles per-direction flags and B-channel interrupts. Each BBUF interrupt either writes the next playback byte to `BBTB` or reads a capture byte from `BBRB`; when the buffer byte count reaches zero it reports period elapsed. Mixer controls update `rgain`, `pgain`, and `mgain` and rewrite hardware gain coefficients under the spinlock.

## Dependencies and Integration Points
Depends on ALSA core/PCM/control APIs, SPARC SBUS MMIO helpers, OF/platform resources, interrupts, and legacy module parameters for card index/id/enable. It is built only for SPARC SBUS systems through the local Kconfig.

## Risks and Test Signals
Risks include half-duplex hardware represented by independent playback/capture flags, interrupt handler calling `snd_pcm_period_elapsed()` for capture when no playback elapsed due to `else` logic, period handling based on whole buffer byte exhaustion rather than ALSA period size, no platform-driver remove callback, global `amd7930_list` cleanup at module exit, and legacy 8-bit companded-only constraints. Test signals are probe on SBUS audio nodes, IRQ byte transfer at 8 kHz, A-law/mu-law mode switching, playback/capture pointer movement, mixer coefficient updates, module unload freeing cards, and no underrun/capture overrun during small-buffer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/amd7930.c -->
