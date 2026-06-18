# subset-b-006555 Tegra and TI ASoC driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.c

## Purpose

This file is the Tegra30/Tegra124 I2S CPU DAI driver. It registers one stereo playback/capture DAI, programs the I2S MMIO block through regmap, routes the port through the Tegra30 AHUB FIFO fabric, and binds the DAI to Tegra's dmaengine PCM platform.

## Important APIs, types, and functions

The main DAI callbacks are `tegra30_i2s_set_fmt`, `tegra30_i2s_hw_params`, `tegra30_i2s_trigger`, `tegra30_i2s_set_tdm`, and `tegra30_i2s_probe`. Platform lifecycle is handled by `tegra30_i2s_platform_probe` and `tegra30_i2s_platform_remove`. Runtime PM is implemented by `tegra30_i2s_runtime_suspend` and `tegra30_i2s_runtime_resume`. SoC-specific CIF programming is selected through `tegra30_i2s_config` versus `tegra124_i2s_config`.

## Control flow

Probe allocates `struct tegra30_i2s`, reads `nvidia,ahub-cif-ids`, gets the I2S clock, maps registers, creates a cached regmap, enables runtime PM, allocates AHUB TX/RX FIFOs, routes playback and capture CIFs, registers the ASoC component/DAI, then registers Tegra PCM with explicit DMA channel names. `hw_params` accepts only stereo `S16_LE`, computes the required I2S clock and channel bit count, sets the clock rate, writes timing/offset registers, and programs RX or TX Audio CIF based on stream direction. `trigger` enables or disables AHUB FIFO paths and I2S transfer bits.

## State and persistence behavior

Persistent state is the driver data object, FIFO CIF IDs, DMA channel names and addresses, regmap cache, selected SoC CIF callback, and runtime PM clock state. Suspend marks the regmap cache-only and disables the clock; resume enables the clock, marks the cache dirty, and syncs cached register state back to hardware.

## Dependencies and integration points

It depends on ASoC DAI/component APIs, dmaengine PCM, Tegra AHUB helpers, runtime PM, regmap, clocks, and device tree. Machine drivers reference this DAI through `nvidia,i2s-controller`; AHUB FIFO allocation and CIF routing connect it to the larger Tegra audio fabric.

## Risks and test signals

Risks include unsupported non-stereo or non-16-bit formats, bad DT CIF IDs, mismatched AHUB route cleanup on probe failure, clock-rate rounding that changes bit timing, and regcache sync failures after runtime resume. Useful test signals are boot/probe logs, `aplay`/`arecord` at 8-96 kHz, TDM slot programming checks, runtime suspend/resume playback continuity, and DMA channel-name validation in device tree.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.h

## Purpose

This header defines the Tegra30 I2S register map, bitfields, and private driver data structures used by `tegra30_i2s.c`.

## Important APIs, types, and functions

It declares register offsets from `TEGRA30_I2S_CTRL` through `TEGRA30_I2S_LCOEF_2_4_2`, masks for control, timing, offset, channel, slot, flow-control, flow-status, and coefficient registers, `struct tegra30_i2s_soc_data`, and `struct tegra30_i2s`.

## Control flow

There is no executable control flow beyond structure layout. The constants drive regmap readable/writeable/volatile checks, DAI format programming, `hw_params` clock/timing calculations, TDM slot setup, and runtime transfer enable/disable in the C file.

## State and persistence behavior

`struct tegra30_i2s` persists the SoC-specific CIF writer, mutable DAI template copy, I2S clock, AHUB playback/capture CIF endpoints, DMA channel names/data, regmap, and dmaengine PCM configuration. These fields bridge platform probe, DAI callbacks, runtime PM, and remove cleanup.

## Dependencies and integration points

The header includes `tegra_pcm.h` for dmaengine PCM types and refers to Tegra30 AHUB CIF enums and `struct tegra30_ahub_cif_conf` through the C file include order. Its register constants must match the Tegra30/Tegra124 hardware manual and the AHUB CIF helpers.

## Risks and test signals

The main risks are incorrect bit shifts/masks, stale register offsets, the typo-preserved `EGDE` field names being misused, and structure changes that desynchronize cleanup or DMA setup. Compile coverage, regmap access tests, DT-driven probe, and oscilloscope/logic-analyzer checks of LRCK/BCLK/data timing are strong signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra30_i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.c

## Purpose

This is the shared and universal Tegra ASoC machine-driver implementation for many older Tegra boards and codecs. It centralizes jack GPIO handling, common DAPM widgets and controls, audio clock programming, DT phandle binding, and a table of codec-specific card descriptors.

## Important APIs, types, and functions

The exported helpers are `tegra_asoc_machine_init` and `tegra_asoc_machine_probe`. The common PCM operation is `tegra_machine_hw_params`, which programs PLLA/PLLA_OUT0/MCLK and calls `snd_soc_dai_set_sysclk` on the codec. Board policy is described by static `struct tegra_asoc_data` instances for WM8753, WM9712, MAX98090/98088/98089, SGTL5000, TLV320AIC23 TrimSlice, RT5677/RT5640/RT5632/RT5631, and CPCAP.

## Control flow

Probe obtains GPIOs, parses model and routing, binds either AC97 or I2S/controller and codec phandles into the card's DAI link, optionally installs common controls/widgets/ops, gets PLLA clocks, applies legacy clock-parent fallback, handles fixed AC97 clocking, enables the MCLK, and registers the card. Runtime init creates headphone, headset, and microphone jacks according to flags and GPIO availability. `hw_params` selects a base PLL rate for 44.1 kHz or 48 kHz rate families, updates clocks only when cached values differ, then tells the codec its MCLK.

## State and persistence behavior

State is stored in `struct tegra_machine`: clocks, last programmed baseclock/MCLK, optional GPIO descriptors, and pointers to shared jack state. Several jack objects are file-static singletons, so the driver assumes one active card instance for those paths. GPIO output state follows DAPM widget power events and jack GPIO state follows `snd_soc_jack_add_gpios`.

## Dependencies and integration points

It integrates with Linux ASoC card/DAI/DAPM/jack APIs, gpiod, clocks, OF phandles, codec drivers, and the per-codec wrapper drivers that reuse `tegra_asoc_machine_probe`. Device tree properties include `nvidia,model`, `nvidia,audio-routing`, codec/controller phandles, optional jack/mute GPIOs, and legacy clock-parent behavior.

## Risks and test signals

Risks include global jack objects preventing safe multi-card use, legacy clock fallback hiding DT errors, clock rates that do not match codec constraints, and DAPM widget-name coupling for GPIO events. Tests should cover each compatible string, jack insertion/removal, DAPM speaker/mic/headphone GPIO toggles, AC97 versus I2S probe, suspend/resume with MCLK left enabled, and sample-rate family transitions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.h

## Purpose

This header defines the private data contracts shared by Tegra codec-specific machine drivers and the common Tegra machine implementation.

## Important APIs, types, and functions

`struct tegra_asoc_data` carries board/codec policy: MCLK callback, optional codec platform-device name, HP jack name, card pointer, MCLK ID, jack/control/widget flags, AC97 mode, and legacy HP GPIO polarity handling. `struct tegra_machine` stores runtime card state: clocks, cached clock rates, the selected policy, GPIO descriptors, and shared jack pointers. It declares `tegra_asoc_machine_probe` and `tegra_asoc_machine_init`.

## Control flow

The header has no executable logic. Codec machine files instantiate `tegra_asoc_data`, then the common probe consumes the flags to configure phandles, widgets, controls, jacks, clocks, and card registration.

## State and persistence behavior

`tegra_machine` is per-card state attached with `snd_soc_card_set_drvdata`. It persists GPIO descriptors and last programmed clock values across DAI callbacks. The booleans in `tegra_asoc_data` are immutable policy state matched from OF compatibles.

## Dependencies and integration points

The header forward-declares Linux clock, GPIO, ASoC, jack, and platform-device types, allowing small codec machine files to depend on the shared probe/init ABI without pulling in the full implementation.

## Risks and test signals

Risks are ABI drift between codec wrappers and common probe, missing initialization when new `tegra_asoc_data` flags are added, and stale fields such as `gpiod_ear_sel` that are not used by current code. Build coverage of all Tegra machine files and runtime probe for each compatible are the main signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_asoc_machine.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_audio_graph_card.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_audio_graph_card.c

## Purpose

This file implements a Tegra audio-graph-card machine driver for newer Tegra APE systems. It extends the generic audio graph/simple-card utility with Tegra PLLA and PLLA_OUT0 clock programming.

## Important APIs, types, and functions

Key types are `enum srate_type`, `struct tegra_audio_priv`, and `struct tegra_audio_cdata`. Important functions are `need_clk_update`, `tegra_audio_graph_update_pll`, `tegra_audio_graph_hw_params`, `tegra_audio_graph_card_probe`, and `tegra_audio_graph_probe`. SoC clock tables exist for Tegra210, Tegra186, Tegra238, and Tegra264 compatibles.

## Control flow

Platform probe allocates private data, creates a simple-card, enables component chaining and forced DPCM, installs custom ops, and calls `audio_graph_parse_of`. Card probe gets `pll_a` and `plla_out0` clocks before delegating to `graph_util_card_probe`. At `hw_params`, the driver updates clocks only for CPU DAIs whose driver names contain I2S, DMIC, or DSPK, chooses 44.1 kHz-family or 48 kHz-family PLL rates, halves PLLA_OUT0 when the implied BCLK divider would exceed 128, then calls `simple_util_hw_params`.

## State and persistence behavior

Persistent state is the embedded `simple_util_priv` plus PLL clock handles. The driver does not cache programmed rates; each relevant `hw_params` call may reprogram PLLA and PLLA_OUT0. Card and DAI topology are parsed from DT graph endpoints.

## Dependencies and integration points

It depends on `sound/graph_card.h`, simple-card utilities, ASoC DAI helpers, Linux clocks, OF match data, and Tegra clock topology. It is selected by `nvidia,tegra*-audio-graph-card` compatibles and integrates with CPU DAIs named as Tegra I2S/DMIC/DSPK.

## Risks and test signals

Risks include fragile string matching in `need_clk_update`, unsupported sample rates, clock-rate conflicts when multiple links request different families, and divider assumptions for low BCLK configurations. Tests should cover audio graph parsing, low-rate I2S playback, 44.1/48/176.4/192 kHz families, simultaneous DPCM links, and clock tree inspection before and after stream start.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_audio_graph_card.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_cif.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_cif.h

## Purpose

This header provides inline helpers for programming Tegra Audio CIF control registers, including the altered bit layout used by Tegra264.

## Important APIs, types, and functions

`struct tegra_cif_conf` carries FIFO threshold, audio/client channel counts, audio/client sample widths, expansion, stereo conversion, replication, truncation, and mono conversion fields. `tegra_set_cif` and `tegra264_set_cif` pack that structure into a register update using `TEGRA_ACIF_UPDATE_MASK`.

## Control flow

Both helpers construct a single register value from the configuration, subtract one from channel counts for hardware encoding, shift each field into place, then call `regmap_update_bits`. Tegra264 uses different shifts for audio bits, client channels, and audio channels while reusing the remaining field layout.

## State and persistence behavior

There is no local state. The persistent effect is the hardware CIF register value written through regmap. The helpers assume callers provide valid channel counts and enum-encoded bit widths.

## Dependencies and integration points

It depends only on `linux/regmap.h`. It is a shared low-level contract for Tegra audio clients that need to connect CPU/audio fabric sample formats and channel layouts to hardware FIFOs.

## Risks and test signals

Risks include invalid zero channel counts underflowing the `- 1` encoding, wrong Tegra264 shifts, and `TEGRA_ACIF_UPDATE_MASK` accidentally preserving stale bits outside the mask. Test signals are register dumps after each CIF setup, playback/capture with mono/stereo/multichannel formats, and SoC-specific validation on Tegra264 versus earlier chips.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_cif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.c

## Purpose

This file implements interconnect bandwidth voting for Tegra ADMAIF audio streams. It tracks per-PCM-device bandwidth and uses Linux interconnect APIs to request aggregate write bandwidth.

## Important APIs, types, and functions

The public functions are `tegra_isomgr_adma_register`, `tegra_isomgr_adma_unregister`, and `tegra_isomgr_adma_setbw`. The implementation uses `struct tegra_admaif` from `tegra210_admaif.h` and `struct tegra_adma_isomgr` from the paired header.

## Control flow

Registration allocates isomgr state, gets the `"write"` ICC path, derives maximum PCM devices and maximum bandwidth from ADMAIF SoC data, allocates two per-device arrays for playback and capture, initializes the mutex, and attaches the object to ADMAIF. `setbw` validates runtime/PCM pointers and device index, skips no-op state transitions, computes bandwidth for running streams from channels, rate in kHz, and sample bytes, clamps the aggregate to `max_bw`, updates aggregate and per-device accounting under a mutex, then calls `icc_set_bw`.

## State and persistence behavior

State persists in `admaif->adma_isomgr`: ICC path, mutex, current aggregate bandwidth, maximums, and `bw_per_dev[stream][pcm_device]`. Unregister destroys the mutex but relies on devm allocation for memory lifetime.

## Dependencies and integration points

It integrates with the Tegra ADMAIF DAI driver, ALSA runtime format/rate/channel state, and Linux interconnect providers. It is intended to be called when ADMA streams start and stop.

## Risks and test signals

Risks include integer unit confusion (`KBps` versus ICC units), subtracting stale bandwidth after partial failures, calling `icc_set_bw` outside the mutex after aggregate state changes, unsupported formats yielding negative widths, and missing ICC path silently disabling behavior. Tests should start/stop multiple ADMAIF streams, verify ICC votes with tracing, cover invalid PCM indices, and exercise open/close failure paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.h

## Purpose

This header defines the Tegra ADMA isomgr bandwidth state and the small public API used by ADMAIF.

## Important APIs, types, and functions

`STREAM_TYPE` is fixed at two for playback and capture. `struct tegra_adma_isomgr` stores the mutex, ICC path handle, per-stream/per-device bandwidth arrays, current aggregate bandwidth, maximum PCM device count, and maximum bandwidth. It declares register, unregister, and set-bandwidth functions.

## Control flow

No code executes in this header. The C file populates the structure during ADMAIF registration and updates it on stream state transitions.

## State and persistence behavior

The structure is owned by ADMAIF and persists for the device lifetime. Its mutex protects aggregate bandwidth accounting, while `bw_per_dev` records each PCM device's last active vote.

## Dependencies and integration points

It references `struct mutex`, `struct icc_path`, `u32`, `struct device`, `struct snd_pcm_substream`, and `struct snd_soc_dai`, so it is tightly coupled to Linux kernel, interconnect, and ASoC interfaces.

## Risks and test signals

Risks include callers using stream indexes outside `0..STREAM_TYPE-1`, lifecycle mismatches with devm-allocated arrays, and future ADMAIF changes that add more stream classes. Compile coverage with ADMAIF and runtime stream start/stop tests are the key signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_isomgr_bw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.c

## Purpose

This file is Tegra's dmaengine-backed PCM platform helper. It provides a common PCM hardware definition, registration helpers, and legacy component callbacks for opening, configuring, closing, pointer reporting, and buffer allocation.

## Important APIs, types, and functions

Exports include `tegra_pcm_platform_register`, `devm_tegra_pcm_platform_register`, `tegra_pcm_platform_register_with_chan_names`, `tegra_pcm_platform_unregister`, `tegra_pcm_open`, `tegra_pcm_close`, `tegra_pcm_hw_params`, `tegra_pcm_pointer`, and `tegra_pcm_new`. `tegra_pcm_hardware` defines mmap/interleaved capability, period bounds, eight-page buffer size, and FIFO size.

## Control flow

Registration passes a `snd_dmaengine_pcm_config` to dmaengine PCM, optionally adding channel names and parent DMA device. `open` skips DPCM no-pcm links, installs hardware constraints, requires period bytes to step by 8, requests the named DMA channel from the CPU DAI device, and opens dmaengine PCM with a default 500 ms wait time. `hw_params` builds a DMA slave config from ALSA params, fills source or destination address/width/burst from DAI DMA data, and calls `dmaengine_slave_config`. `new` allocates a fixed write-combine DMA buffer and preserves compatibility with older top-level `sound` nodes carrying `iommus`.

## State and persistence behavior

The module has no mutable global state. Per-stream state lives in ALSA runtime and dmaengine channel ownership. Buffer allocation persists in the PCM object for the card lifetime.

## Dependencies and integration points

It integrates with dmaengine PCM, ALSA PCM hardware constraints, CPU DAI DMA data, OF `iommus`, and Tegra DAI drivers such as I2S. The named-channel registration path is used by drivers that allocate AHUB FIFOs and expose synthetic DMA channel names.

## Risks and test signals

Risks include missing `dmap` in `open`, channel-name mismatch, fixed burst sizes not matching a controller, 32-bit DMA mask limits, and older-DT IOMMU fallback selecting the wrong device. Tests should cover playback/capture open/close, DMA channel release on errors, mmap buffer allocation, no-pcm DPCM links, and period-size constraint enforcement.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.h

## Purpose

This header exposes Tegra PCM helper callbacks and registration functions to Tegra CPU DAI/component drivers.

## Important APIs, types, and functions

It declares PCM component callbacks (`tegra_pcm_new`, `tegra_pcm_open`, `tegra_pcm_close`, `tegra_pcm_hw_params`, `tegra_pcm_pointer`) and platform registration helpers, including a channel-name variant that accepts a mutable `snd_dmaengine_pcm_config`.

## Control flow

There is no executable logic. Driver components wire these callbacks into ASoC component drivers, while platform DAI drivers call the registration helpers from probe.

## State and persistence behavior

The header defines no state. State is supplied by callers through ASoC component/runtime/substream objects and through DMA config/channel-name storage owned by the DAI driver.

## Dependencies and integration points

It includes `sound/dmaengine_pcm.h` and `sound/asound.h`, making the ABI depend on ALSA and dmaengine PCM definitions. It is the shared contract between Tegra audio controllers and the PCM helper implementation.

## Risks and test signals

Risks are signature drift against ASoC callbacks and caller-provided DMA config lifetime issues. Compile tests across all Tegra DAI users and playback/capture smoke tests verify the contract.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8903.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8903.c

## Purpose

This is a codec-specific Tegra machine wrapper for boards using the WM8903 codec. It supplies WM8903 DAI/card descriptors and codec-specific jack/MICBIAS handling while delegating generic board setup to `tegra_asoc_machine_probe`.

## Important APIs, types, and functions

Key functions are `tegra_wm8903_mclk_rate`, `tegra_wm8903_init`, and `tegra_wm8903_remove`. The driver defines `tegra_wm8903_dai`, `snd_soc_tegra_wm8903`, legacy and non-legacy `tegra_asoc_data`, and a compatible table for multiple historical boards.

## Control flow

Probe is the shared Tegra machine probe. DAI init optionally compensates for old DT headphone-detect polarity, calls common machine init to create jacks, creates a WM8903 codec-driven mic jack when no external mic GPIO exists, invokes `wm8903_mic_detect`, and force-enables `MICBIAS`. Remove disables codec mic detect. The MCLK callback uses 128x for high sample rates and 256x otherwise, then doubles until at least 6 MHz.

## State and persistence behavior

State lives in the common `tegra_machine`, the static card/DAI descriptors, and WM8903 mic-detect registration. Legacy polarity behavior mutates the shared `hp_jack_gpio` inversion field during init.

## Dependencies and integration points

It depends on the WM8903 codec driver's `wm8903_mic_detect`, ASoC jack/DAPM, gpiod polarity, OF compatibles, and `tegra_asoc_machine` common helpers. Device tree supplies codec/controller phandles and board-specific compatible selection.

## Risks and test signals

Risks include legacy polarity quirks applied to the wrong board, mic detection conflicts between GPIO and codec IRQ paths, forced MICBIAS power cost, and global card descriptor reuse. Tests should cover all legacy compatibles, headphone/mic insertion, headset short detection through `nvidia,headset`, suspend/resume, and sample-rate clock setup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8903.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8962.c -->
# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8962.c

## Purpose

This is the Tegra machine wrapper for WM8962 codec boards. It mirrors the WM8903 pattern with WM8962-specific MCLK selection and mic-detect integration.

## Important APIs, types, and functions

The main functions are `tegra_wm8962_mclk_rate`, `tegra_wm8962_init`, and `tegra_wm8962_remove`. Static descriptors include `tegra_wm8962_dai`, `snd_soc_tegra_wm8962`, `tegra_wm8962_data`, and the OF match table for `nvidia,tegra-audio-wm8962`.

## Control flow

Shared Tegra machine probe performs card binding. DAI init calls `tegra_asoc_machine_init`, then if there is no external mic-detect GPIO and mic jack support is enabled it creates a `Mic Jack` and passes it to `wm8962_mic_detect`. It force-enables `MICBIAS`. Remove disables WM8962 mic detection by passing `NULL`. The MCLK callback returns 12.288 MHz for 48 kHz-family rates, 11.2896 MHz for 44.1 kHz-family rates, and 12 MHz otherwise.

## State and persistence behavior

State is shared between static card/DAI descriptors, common Tegra machine state, and WM8962 codec mic-detect registration. There is no separate mutable driver-private structure in this file.

## Dependencies and integration points

It depends on `wm8962_mic_detect`, ASoC jack/DAPM APIs, the common Tegra machine helper, OF-compatible matching, and DT-provided codec/I2S phandles and optional GPIOs.

## Risks and test signals

Risks include unsupported sample-rate families falling back to 12 MHz, jack creation failure leaving codec detection unregistered, MICBIAS always forced on, and static card reuse assumptions. Tests should validate probe, clock rates at common sample rates, codec-based mic detection, GPIO-based jack fallback, and card remove cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/tegra/tegra_wm8962.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/ti/Kconfig

## Purpose

This Kconfig file defines Texas Instruments ASoC platform, CPU DAI, and machine-driver configuration symbols and their dependency/select relationships.

## Important APIs, types, and functions

Important symbols include `SND_SOC_TI_EDMA_PCM`, `SND_SOC_TI_SDMA_PCM`, `SND_SOC_TI_UDMA_PCM`, `SND_SOC_DAVINCI_ASP`, `SND_SOC_DAVINCI_MCASP`, OMAP DAI symbols, multiple OMAP/Nokia/Pandora/TWL board symbols, `SND_SOC_OMAP_AMS_DELTA`, `SND_SOC_DAVINCI_EVM`, and `SND_SOC_J721E_EVM`.

## Control flow

Kconfig evaluation gates the menu on TI DMA provider availability or `COMPILE_TEST`. DAI symbols select the correct generic DMAengine PCM provider wrappers. Machine symbols depend on SoC, I2C, GPIO, MFD, or clock prerequisites and select the codec/DAI drivers they need.

## State and persistence behavior

Configuration state persists in the kernel `.config`. This file does not manage runtime state, but it determines which objects are built and therefore which probe paths can exist.

## Dependencies and integration points

It integrates with the kernel build system, SoC architecture symbols, DMA controller options, codec Kconfig symbols, and the Makefile in the same directory. The comments and help text document supported boards and required userspace setup for AMS Delta.

## Risks and test signals

Risks include missing selects causing link errors, overly narrow dependencies hiding compile coverage, and board symbols selecting the wrong DAI/codec. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and targeted configs for Davinci ASP, McASP, AMS Delta, DaVinci EVM, and J721E EVM.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/ti/Makefile

## Purpose

This Makefile maps TI ASoC Kconfig symbols to kernel object names for PCM providers, CPU DAIs, and machine drivers.

## Important APIs, types, and functions

It defines aggregate object lists such as `snd-soc-ti-edma-y`, `snd-soc-davinci-asp-y`, `snd-soc-davinci-mcasp-y`, OMAP DAI objects, and board objects like `snd-soc-davinci-evm-y` and `snd-soc-ams-delta-y`. `obj-$(CONFIG_...)` lines attach those aggregates to config symbols.

## Control flow

There is no runtime control flow. During kernel build, Kbuild expands selected config symbols into built-in or module objects and compiles the listed source files.

## State and persistence behavior

Build state is controlled by `.config` and Kbuild output directories. This file has no persistent runtime state.

## Dependencies and integration points

It must stay aligned with `Kconfig`, source filenames, and module names expected by userspace/autoloading. It also references related TI files outside this work item, such as `sdma-pcm.o`, `udma-pcm.o`, OMAP DAI files, and J721E machine support.

## Risks and test signals

Risks include stale object names after file renames, missing object aggregation for newly selected symbols, and module-name changes that break autoload assumptions. Full build coverage with representative TI configs and `modules.order` inspection are useful signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/ams-delta.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/ams-delta.c

## Purpose

This machine driver supports the Amstrad E3/Delta videophone audio path. It connects OMAP McBSP to a CX20442 voice codec, controls handset/handsfree GPIO mutes, exposes an `Audio Mode` control, and optionally integrates a modem TTY line discipline for codec control.

## Important APIs, types, and functions

Important functions include DAPM GPIO events `ams_delta_event_handset` and `ams_delta_event_handsfree`, ALSA control handlers `ams_delta_get_audio_mode` and `ams_delta_set_audio_mode`, line discipline callbacks `cx81801_open`, `cx81801_close`, `cx81801_receive`, mute control `ams_delta_mute`, card init `ams_delta_cx20442_init`, and platform probe/remove.

## Control flow

Probe gets handset and handsfree mute GPIOs and registers the card. Card init saves the codec component for TTY callbacks, creates a hook-switch jack, gets the modem/codec mux GPIO, installs a fallback codec DAI mute operation or startup/shutdown hooks, registers line discipline `N_V253`, and initializes DAPM pins. The TTY receive path forwards modem data to `v253_ops`, detects carriage-return responses, pulses the mux GPIO through a timer, and later reconnects the codec unless audio is muted. The `Audio Mode` control maps enum selections into DAPM pin enable/disable state.

## State and persistence behavior

State is mostly file-static: mute GPIOs, codec pointer, hook switch, AGC flag, timer, pending-command flag, digital mute flag, spinlock, and modem mux GPIO. DAPM pin state persists in the card. The line discipline lifecycle resets pins on close and unregisters on remove.

## Dependencies and integration points

It depends on OMAP McBSP platform naming, the CX20442 codec and `v253_ops`, GPIO descriptors, TTY line disciplines, ASoC jack/DAPM/control APIs, and platform data. Kconfig help documents the required userspace `ldattach 19 /dev/ttyS3` setup.

## Risks and test signals

Risks include static state that assumes one card, races between timer, mute, and TTY receive paths, line discipline registration/unregistration ordering, codec DAI ops mutation, and functionality depending on userspace attaching the ldisc. Test signals include card probe without ldisc, ldisc open/close/hangup, hook-switch GPIO events, all `Audio Mode` transitions, playback mute behavior, and timer/mux GPIO tracing.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/ams-delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-evm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-evm.c

## Purpose

This machine driver supports TI DaVinci EVM boards using a TLV320AIC3X codec and a McASP controller. It wires DT phandles into an ASoC card, manages an optional MCLK, and sets codec/CPU sysclk during stream setup.

## Important APIs, types, and functions

`struct snd_soc_card_drvdata_davinci` stores `mclk` and `sysclk`. Important functions are `evm_startup`, `evm_shutdown`, `evm_hw_params`, `evm_aic3x_init`, and `davinci_evm_probe`. Static descriptors include `evm_dai_tlv320aic3x`, `davinci_evm_dt_ids`, and `evm_soc_card`.

## Control flow

Probe matches the DAI link, parses codec and McASP phandles, assigns CPU/platform/codec endpoints, parses `ti,model`, obtains optional `mclk`, derives `sysclk` from `ti,codec-clock-rate` or the clock rate, stores drvdata, and registers the card. Startup enables MCLK; shutdown disables it. `hw_params` sets sysclk on the codec and then the CPU DAI, allowing `-ENOTSUPP` from the CPU side. Codec init adds DAPM widgets, parses `ti,audio-routing` or installs legacy routes, and disables unconnected codec pins.

## State and persistence behavior

The static card and DAI link are mutated with DT phandles during probe. Drvdata persists MCLK and sysclk for stream callbacks. Error paths manually drop OF node references and clear DAI link nodes.

## Dependencies and integration points

It depends on OF platform matching, ASoC card/DAI/DAPM APIs, clocks, TLV320AIC3X codec naming, and McASP CPU DAI. Device tree properties include `ti,audio-codec`, `ti,mcasp-controller`, `ti,model`, optional `ti,audio-routing`, and optional `ti,codec-clock-rate`.

## Risks and test signals

Risks include static card mutation with multiple instances, OF node reference leaks on devm card unregister, clock-rate mismatch after `clk_set_rate`, and route differences between DT and legacy map. Tests should probe with valid/invalid phandles, verify MCLK enable/disable around streams, test sysclk programming, and run playback through the AIC3X routes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-evm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.c

## Purpose

This is the DaVinci ASP/McBSP-compatible I2S CPU DAI driver. Despite the McBSP naming, it drives the older DaVinci Audio Serial Port block and connects it to EDMA PCM.

## Important APIs, types, and functions

The private state is `struct davinci_mcbsp_dev`. DAI callbacks include `davinci_i2s_set_dai_fmt`, `davinci_i2s_dai_set_clkdiv`, `davinci_i2s_set_tdm_slot`, `davinci_i2s_hw_params`, `davinci_i2s_prepare`, `davinci_i2s_trigger`, `davinci_i2s_shutdown`, and `davinci_i2s_dai_probe`. Platform lifecycle is `davinci_i2s_probe` and `davinci_i2s_remove`.

## Control flow

Probe maps the `mpu` register resource, allocates state, reads optional T1 framing booleans, fills TX/RX DMA addresses and filter data from resources or DT names, gets functional and optional external clocks, enables clocks, registers the ASoC component, and registers EDMA PCM. Format setup programs PCR, SPCR, and SRGR for master/slave clocking, DSP/I2S emulation, inversion, free-running mode, and TDM restrictions. `hw_params` validates format, computes word length, sample-rate generator settings, receive/transmit control fields, optional channel-combine behavior, and writes XCR or RCR. `prepare` resets and primes the controller; `trigger` starts or stops TX/RX.

## State and persistence behavior

State includes register base, DMA data/request IDs, current PCR/mode/fmt/clock divider/TDM settings, clock handles, and T1 framing flags. Hardware state is direct MMIO with no regcache or runtime PM. Clocks are enabled at probe and disabled at remove.

## Dependencies and integration points

It depends on ASoC, dmaengine PCM through `edma-pcm.h`, Linux clocks, DT or legacy resources, and DaVinci board machine drivers. DMA addresses point to DXR/DRR registers and channel names default to `"tx"`/`"rx"` under DT.

## Risks and test signals

Risks include confusing ASP/McBSP terminology, unsupported true I2S in some codec-master modes, TDM masks requiring all slots, clock-divider rounding errors, direct raw MMIO without PM save/restore, and channel-combine left/right swaps. Tests should cover each DAI format and clock-provider mode, S16/S24/S32 playback/capture, TDM slot setup, suspend behavior, and DMA resource versus DT channel-name paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.h

## Purpose

This header exposes the divider ID used by the DaVinci ASP/I2S DAI `set_clkdiv` callback.

## Important APIs, types, and functions

It defines `enum davinci_mcbsp_div` with `DAVINCI_MCBSP_CLKGDV`, representing the sample-rate generator divider.

## Control flow

No executable code exists. Machine drivers may pass this enum to `snd_soc_dai_set_clkdiv`, which reaches `davinci_i2s_dai_set_clkdiv`.

## State and persistence behavior

No state is defined. The selected divider value is stored in `struct davinci_mcbsp_dev` in the C file.

## Dependencies and integration points

It is a small ABI between machine drivers and `davinci-i2s.c`. Its guard name and enum must stay stable for existing users.

## Risks and test signals

The main risk is adding or renaming divider IDs without updating the DAI callback. Build tests of any machine driver using `DAVINCI_MCBSP_CLKGDV` and runtime clock-divider validation are sufficient signals.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-i2s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.c

## Purpose

This file is the main TI DaVinci/Sitara/OMAP/DRA/K3 McASP CPU DAI driver. It supports multichannel IIS/TDM and DIT S/PDIF modes, EDMA/SDMA/UDMA PCM backends, optional GPIO use of McASP pins, IRQ-driven xrun detection, clock/divider programming, channel constraints, and runtime PM context save/restore.

## Important APIs, types, and functions

The core state is `struct davinci_mcasp`, backed by `struct davinci_mcasp_context` under PM and `struct davinci_mcasp_ruledata` for ALSA constraints. Important DAI callbacks are `davinci_mcasp_set_dai_fmt`, `davinci_mcasp_set_clkdiv`, `davinci_mcasp_set_sysclk`, `davinci_mcasp_set_tdm_slot`, `davinci_mcasp_startup`, `davinci_mcasp_shutdown`, `davinci_mcasp_hw_params`, `davinci_mcasp_trigger`, `davinci_mcasp_delay`, and `davinci_mcasp_dai_probe`. Probe helpers parse DT/platform config, choose DMA type, calculate DMA offsets, register optional GPIO chip, and request IRQs.

## Control flow

Probe validates DT/platform data, maps registers, enables runtime PM, parses op mode, TDM slots, async mode, serializer directions, FIFO event depths, auxclk/fs ratios, and dismod, initializes pins to McASP function, requests common/rx/tx IRQs, prepares DMA addresses from `mpu` or `dat` resources, allocates channel constraint lists, possibly reparents legacy `fck`, detects the DMA controller by temporarily requesting the TX channel, registers the appropriate PCM provider, registers the DAI component for IIS or DIT mode, then optionally registers a GPIO chip. Runtime DAI setup programs frame format, clock provider roles, inversion, sysclk source, dividers, TDM masks, serializer direction, FIFO thresholds, format width/rotation, S/PDIF channel status, and channel/rate/format constraints. Trigger starts/stops RX or TX by sequencing global-control bits, serializer release, FIFO enable, IRQ masks, and pin direction updates.

## State and persistence behavior

Persistent state includes DMA data, platform data, MMIO base/fifo base, active substreams, DAI format, IEC958 status, TDM masks/slots/widths, op mode, serializers, clock frequencies/dividers, async mode, pdir bitfield, FIFO event depths, data-port mode, active channel/format constraints, IRQ masks, optional GPIO chip, and PM context. Runtime suspend saves key config/FIFO/serializer registers; resume restores them. Stream counters coordinate synchronous TX/RX clock lifetime.

## Dependencies and integration points

It depends on ASoC, ALSA hw constraints, dmaengine PCM providers (`edma-pcm`, `sdma-pcm`, `udma-pcm`), Linux clocks, runtime PM, OF/property APIs, GPIO library, platform data `davinci_asp.h`, and McASP register definitions. Device tree supplies compatibles, `op-mode`, `tdm-slots`, `serial-dir`, FIFO event counts, DMA names, optional `dat` resource, GPIO-controller flag, and clock metadata.

## Risks and test signals

Risks are high because this driver spans many SoC versions. Specific risks include async/sync TX/RX clock interactions, serializer count versus channels, FIFO `numevt` divisibility, implicit BCLK divider accuracy, DIT-only TX behavior, DMA-controller detection side effects, GPIO/audio pin conflicts, PM restore omissions, and static-compatible pdata defaults. Tests should cover IIS playback/capture/full-duplex, async TX/RX with different slots, DIT S/PDIF rates and IEC958 controls, EDMA/SDMA/UDMA probes, xrun IRQ handling, GPIO-only mode with missing audio params, runtime suspend/resume, and DT validation failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.h

## Purpose

This header defines McASP register offsets, bit masks, serializer controls, FIFO controls, and public clock/divider IDs used by `davinci-mcasp.c` and machine drivers.

## Important APIs, types, and functions

It covers register groups for global control, TX/RX formatting, frame control, clocks, TDM slots, status, DMA event control, DIT channel status/user data, serializer control, data buffers, and AFIFO. Public IDs include `MCASP_CLK_HCLK_*` clock-source constants and `MCASP_CLKDIV_*` divider constants.

## Control flow

There is no executable code. Macros are expanded by register programming helpers in the C file and by external machine drivers calling DAI sysclk/clkdiv APIs.

## State and persistence behavior

No state is stored. The persistent effect of these definitions is the hardware register state programmed by the driver.

## Dependencies and integration points

The header assumes Linux `BIT()` is available through including code. It must match McASP hardware manuals and platform data constants such as serializer modes and op modes from `davinci_asp.h`.

## Risks and test signals

Risks include incorrect offsets for SoC variants, macro precedence issues in shift expressions, public clock/divider IDs drifting from machine-driver expectations, and FIFO base differences between hardware versions. Test signals are register trace review, full-duplex and DIT operation, clock-divider API use by machine drivers, and build coverage on all McASP compatibles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/davinci-mcasp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.c

## Purpose

This file provides the TI EDMA dmaengine PCM registration helper used by DaVinci ASP/McASP and related TI ASoC drivers.

## Important APIs, types, and functions

It defines `edma_pcm_hardware`, `edma_dmaengine_pcm_config`, and exports `edma_pcm_platform_register`. The hardware capabilities include mmap, pause/resume, no-period-wakeup, interleaved streams, 128 KiB buffers, 32-byte minimum periods, 64 KiB maximum periods, and up to 19 periods.

## Control flow

`edma_pcm_platform_register` directly registers the static dmaengine config for DT devices. For non-DT devices it allocates a config copy, adds legacy channel names `"tx"` and `"rx"`, and registers it with devm dmaengine PCM.

## State and persistence behavior

The file has immutable static PCM configuration. Non-DT registration allocates a per-device config that persists through devm lifetime. Runtime DMA state is managed by the generic dmaengine PCM layer.

## Dependencies and integration points

It depends on ASoC, ALSA PCM, dmaengine PCM, and TI DAI drivers that call `edma_pcm_platform_register`. It is selected by `SND_SOC_TI_EDMA_PCM`.

## Risks and test signals

Risks include hardware capability bounds that do not fit all EDMA users, legacy channel-name mismatches, and period-count limits tied to the EDMA dmaengine implementation. Test signals include DT and non-DT probe paths, playback/capture with boundary period sizes, pause/resume, and no-period-wakeup behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.h

## Purpose

This header exposes the EDMA PCM registration helper while allowing callers to build when the EDMA PCM provider is disabled.

## Important APIs, types, and functions

When `CONFIG_SND_SOC_TI_EDMA_PCM` is enabled, it declares `edma_pcm_platform_register`. Otherwise it provides a static inline stub returning 0.

## Control flow

The enabled path calls the real implementation in `edma-pcm.c`; the disabled path compiles out EDMA PCM registration and makes caller probe continue.

## State and persistence behavior

No state is defined. The stub path means no EDMA PCM platform component is registered by that call.

## Dependencies and integration points

The header is used by DaVinci ASP and McASP drivers. It relies on Kconfig selecting the provider when a driver truly needs EDMA PCM, while still making multi-backend code buildable.

## Risks and test signals

Risks include a disabled provider producing a successful no-op when the caller expected real PCM registration, and Kconfig select mistakes masking that at compile time. Test signals are build matrices with the provider enabled/disabled and runtime probe confirming a PCM device appears when EDMA is selected.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/ti/edma-pcm.h -->
