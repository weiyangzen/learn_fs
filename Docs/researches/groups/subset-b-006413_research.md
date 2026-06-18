# subset-b-006413 Research

Grouped code research for the Ceph client copy of Linux ALSA PowerMac, SuperH, ADI ASoC, and AMD ACP audio files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/tumbler.c -->
# sources/distributed-fs/ceph-client/sound/ppc/tumbler.c

## Purpose
`tumbler.c` implements the low-level PowerMac Tumbler/Snapper mixer and codec support for TAS3001C/TAS3004 based machines. It programs codec registers over the Keywest I2C adapter, exposes ALSA mixer controls, manages audio GPIOs for reset/mute/jack detect, handles automatic mute and optional automatic DRC changes, and restores codec/GPIO state across suspend and resume.

## Important APIs, Types, And Functions
The key private state is `struct pmac_tumbler`, which stores `pmac_keywest` I2C state, GPIO descriptors, IRQ numbers, master volumes/switches, TAS mono/mix volumes, DRC range, capture source, reset style, and Snapper analog control state. `snd_pmac_tumbler_init()` is the exported entry point used by the PowerMac core. Important helpers include `send_init_client()`, `tumbler_init_client()`, `snapper_init_client()`, `tumbler_set_master_volume()`, `tumbler_set_drc()`, `snapper_set_drc()`, `tumbler_set_mono_volume()`, `snapper_set_mix_vol()`, `snapper_set_capture_source()`, `tumbler_find_device()`, `tumbler_reset_audio()`, `tumbler_suspend()`, and `tumbler_resume()`.

## Control Flow
Initialization allocates `pmac_tumbler`, records the cleanup hook, discovers Open Firmware audio GPIOs and jack IRQs, resets the codec through either the normal reset GPIO or the anded-reset mute GPIO sequence, locates the TAS codec node and I2C address, initializes Keywest I2C, registers model-specific mixer controls, initializes DRC defaults, installs PM callbacks, initializes the device-change work item, and optionally requests jack-detect IRQs. Mixer `put` callbacks validate ALSA values, update shadow state, and write TAS registers. Jack IRQs schedule `device_change_handler()`, which reads headphone/line-out GPIOs and writes mute GPIOs before reapplying master volume and optional DRC.

## State And Persistence
Runtime state is persisted in `chip->mixer_data`, ALSA control objects, static `device_change`/`device_change_chip`, IRQ registrations, and the TAS codec/GPIO hardware. The driver keeps shadow copies of volumes, switches, DRC, Snapper mixer values, and `acs` so resume can reinitialize the codec and replay every user-visible control. Suspend saves master volume/switches, mutes output, optionally powers down Snapper analog control, disables jack IRQs, and asserts reset/mute GPIOs.

## Dependencies And Integration Points
This file integrates with the PowerMac ALSA core (`struct snd_pmac`), Keywest I2C helpers, Open Firmware GPIO and IRQ discovery, `pmac_call_feature()` GPIO access, ALSA control APIs, optional `PMAC_SUPPORT_AUTOMUTE`, optional `CONFIG_SND_POWERMAC_AUTO_DRC`, and volume tables from `tumbler_volume.h`. It depends on machine quirks such as `PowerMac3,4`, `has-anded-reset`, `layout-id`, and Open Firmware `platform-do-*` GPIO scripts.

## Risks And Edge Cases
GPIO polarity discovery relies on firmware properties and script heuristics, so wrong polarity can invert mute or jack detection. Several init error paths return after partially allocated controls or I2C state, relying on higher-level card cleanup. The global device-change work pointer assumes a single active PowerMac mixer. I2C register writes are retried only during codec init, while control writes surface as `-EINVAL`. Auto-mute suppresses manual mute control changes when enabled, and anded-reset machines need extra sleeps to avoid audible or electrical glitches.

## Test Signals
Useful tests include boot/probe on TAS3001C and TAS3004 machines, ALSA mixer get/put validation for master, bass, treble, PCM, Snapper mix, DRC, capture source, and mute controls; jack insertion/removal with notification checks; suspend/resume replay of all controls; I2C failure injection; Open Firmware GPIO polarity variants; and regression testing on anded-reset and line-out-equipped systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/tumbler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/tumbler_volume.h -->
# sources/distributed-fs/ceph-client/sound/ppc/tumbler_volume.h

## Purpose
`tumbler_volume.h` provides static codec-specific volume conversion tables used by the PowerMac Tumbler/Snapper mixer driver. The arrays map ALSA integer control indices to TAS3001C/TAS3004 register values for master volume, bass, treble, PCM/mixer gains, and Snapper tone controls.

## Important APIs, Types, And Functions
The file has no functions or types. It exports file-local `static const unsigned int` arrays: `master_volume_table`, `treble_volume_table`, `bass_volume_table`, `mixer_volume_table`, `snapper_treble_volume_table`, and `snapper_bass_volume_table`. `tumbler.c` uses `ARRAY_SIZE()` on these tables to define ALSA control limits and then indexes them to build one-, three-, six-, or nine-byte TAS register writes.

## Control Flow
There is no executable flow in this header. Control flow is indirect: ALSA mixer callbacks in `tumbler.c` validate user indices against these array sizes, clamp internal values before hardware writes, translate indices to packed TAS gain/tone values, and send the corresponding bytes over I2C.

## State And Persistence
The arrays are immutable kernel text/rodata. User-visible state is not stored here; persisted mixer state is kept by `struct pmac_tumbler` and translated through the tables each time hardware must be updated or restored after resume.

## Dependencies And Integration Points
This header is included only by `tumbler.c`. The table width and value encoding are tied to TAS3001C/TAS3004 register formats: master and mixer tables are 24-bit values, while tone tables are byte-sized values consumed by the driver according to the target register.

## Risks And Edge Cases
Because ALSA control ranges derive directly from `ARRAY_SIZE()`, changing table length changes the user ABI range for those controls. Incorrect table ordering or values would produce wrong attenuation or tone curves even though control validation still passes. The tables have no self-description, so maintainers must preserve the implicit contract between array index, perceived volume curve, register width, and codec model.

## Test Signals
Tests should check that ALSA control max values match table sizes, boundary indices write valid TAS bytes, mute uses zero rather than table lookup, and suspend/resume or jack automute replays the same register values for selected volume/tone indices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/ppc/tumbler_volume.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/Kconfig -->
# sources/distributed-fs/ceph-client/sound/sh/Kconfig

## Purpose
`sound/sh/Kconfig` declares the non-ASoC SuperH ALSA driver menu and enables the legacy Dreamcast AICA and on-chip SuperH DAC audio drivers.

## Important APIs, Types, And Functions
The main symbols are `SND_SUPERH`, `SND_AICA`, and `SND_SH_DAC_AUDIO`. `SND_SUPERH` is a boolean menu gated by `SUPERH`. `SND_AICA` depends on `SH_DREAMCAST` and `SH_DMA_API`, selects `SND_PCM` and `G2_DMA`, and builds the Dreamcast Yamaha AICA PCM driver. `SND_SH_DAC_AUDIO` depends on `SND`, `CPU_SH3`, and `HIGH_RES_TIMERS`, selects `SND_PCM`, and builds the simple DAC driver.

## Control Flow
The file has no runtime flow. Build-time flow is menu-based: enabling `SND_SUPERH` exposes both driver choices; selected tristate symbols then drive `sound/sh/Makefile` object inclusion.

## State And Persistence
Configuration state persists in the kernel `.config`. There is no runtime state in this file.

## Dependencies And Integration Points
This Kconfig file integrates with the top-level ALSA sound configuration and with `sound/sh/Makefile`. It separates architecture-specific legacy ALSA drivers from ASoC drivers, which are described under the ASoC menu.

## Risks And Edge Cases
The dependencies are hardware-specific. Enabling AICA requires both Dreamcast platform support and the SuperH DMA API; enabling the DAC driver requires high-resolution timers because sample output is timer-driven. Missing dependencies would otherwise lead to build failures or unusable runtime behavior.

## Test Signals
Build tests should cover `m`, `y`, and disabled combinations for `SND_AICA` and `SND_SH_DAC_AUDIO` on matching SuperH configs, plus negative config checks on non-Dreamcast or non-SH3 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/Makefile -->
# sources/distributed-fs/ceph-client/sound/sh/Makefile

## Purpose
`sound/sh/Makefile` maps SuperH ALSA Kconfig symbols to the corresponding kernel objects.

## Important APIs, Types, And Functions
The object composites are `snd-aica-y := aica.o` and `snd-sh_dac_audio-y := sh_dac_audio.o`. The final module inclusions are `obj-$(CONFIG_SND_AICA) += snd-aica.o` and `obj-$(CONFIG_SND_SH_DAC_AUDIO) += snd-sh_dac_audio.o`.

## Control Flow
There is no runtime flow. During kbuild, selected Kconfig tristates decide whether each composite is built-in, built as a module, or omitted.

## State And Persistence
Build state is determined by `.config` and kbuild outputs. The file stores no runtime state.

## Dependencies And Integration Points
It is consumed by the ALSA sound build and pairs directly with `sound/sh/Kconfig`. Module names are stable user-visible artifacts for loading and packaging.

## Risks And Edge Cases
Object naming must remain aligned with module aliases and Kconfig help. Renaming a composite would change module filenames, while adding source files to a composite would affect all configurations that select that driver.

## Test Signals
Signals are successful `allyesconfig`/targeted SuperH builds and expected module artifacts `snd-aica.ko` and `snd-sh_dac_audio.ko` when configured as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/aica.c -->
# sources/distributed-fs/ceph-client/sound/sh/aica.c

## Purpose
`aica.c` is the ALSA PCM driver for the Sega Dreamcast Yamaha AICA sound processor. It creates a simple platform device, loads `aica_firmware.bin` into SPU memory, manages the ARM7/SPU control area, feeds playback data through the SH DMA API, and exposes basic PCM playback controls.

## Important APIs, Types, And Functions
Important functions include `spu_write_wait()`, `spu_memset()`, `spu_memload()`, `spu_disable()`, `spu_enable()`, `spu_reset()`, `aica_chn_start()`, `aica_chn_halt()`, `aica_dma_transfer()`, `run_spu_dma()`, `aica_period_elapsed()`, `snd_aicapcm_pcm_open()`, `snd_aicapcm_pcm_prepare()`, `snd_aicapcm_pcm_trigger()`, `snd_aicapcm_pcm_pointer()`, `snd_aicapcmchip()`, `load_aica_firmware()`, `snd_aica_probe()`, `aica_init()`, and `aica_exit()`. State comes from `struct snd_card_aica` and `struct aica_channel` in `aica.h`.

## Control Flow
Module init registers a platform driver, creates a matching platform device with ARM control and sound RAM resources, resets the SPU, requests firmware, copies it into SPU memory, and enables the ARM7. Probe allocates the ALSA card, initializes work and timer, creates a playback-only PCM, adds mixer controls, and registers the card. PCM open allocates an AICA channel descriptor and enables the SPU. Start schedules DMA work and a timer. The first work run copies the full buffer, uploads channel control, starts playback, then later timer callbacks compare the SPU sample counter with `current_period`, schedule period DMA, call `snd_pcm_period_elapsed()`, and rearm while running.

## State And Persistence
Persistent runtime state includes the global platform device pointer, module parameters, firmware-loaded SPU memory, `snd_card_aica`, the active channel descriptor, `substream`, DMA click counters, period timer, work item, `master_volume`, and `dma_check`. Playback data is staged in ALSA continuous DMA memory then copied into AICA sound RAM per period.

## Dependencies And Integration Points
The driver depends on Dreamcast memory-mapped constants, `mach/sysasic.h`, SH DMA functions `dma_xfer()` and `dma_wait_for_completion()`, the firmware loader, ALSA PCM/control APIs, timers, workqueues, and module firmware packaging for `aica_firmware.bin`.

## Risks And Edge Cases
The code uses fixed physical addresses and local IRQ masking around SPU writes. FIFO waits have a timeout warning but continue. The timer/work path assumes `substream` remains valid while synchronized by `.sync_stop`; incorrect ordering can race close. Mixer volume cannot be used before channel allocation and returns `-ETXTBSY`. `aica_init()` returns firmware-load errors after registering the platform device, so init unwinding deserves attention.

## Test Signals
High-value signals include firmware missing/present boot paths, PCM open/prepare/start/stop/close, period elapsed cadence at supported rates/formats/channels, DMA error injection, `.sync_stop` race testing, volume control before and during playback, and module unload confirming playback halt and SPU reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/aica.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/aica.h -->
# sources/distributed-fs/ceph-client/sound/sh/aica.h

## Purpose
`aica.h` defines the Dreamcast AICA hardware addresses, command values, buffer layout, DMA constants, and driver-private state structures shared by `aica.c`.

## Important APIs, Types, And Functions
The header defines fixed addresses such as `G2_FIFO`, `SPU_MEMORY_BASE`, `ARM_RESET_REGISTER`, `SPU_REGISTER_BASE`, `AICA_CONTROL_POINT`, and `AICA_CONTROL_CHANNEL_SAMPLE_NUMBER`; commands `AICA_CMD_START`, `AICA_CMD_STOP`, and `AICA_CMD_VOL`; sample mode constants; buffer/period sizes; channel offsets; and DMA channel/mode constants. `struct aica_channel` is the command block copied to SPU memory. `struct snd_card_aica` holds ALSA card state, work/timer objects, the active channel, substream, period counters, volume, and DMA phase flag.

## Control Flow
No code executes here. `aica.c` fills `struct aica_channel` during PCM open/prepare, uploads it through `spu_memload()`, and uses the constants to address SPU memory and control registers during reset, start, stop, DMA, and pointer reporting.

## State And Persistence
The structures define the persistent runtime state allocated by `aica.c`. The constants encode hardware layout and therefore form a stable ABI with the Dreamcast SPU firmware loaded by the driver.

## Dependencies And Integration Points
This header is private to the AICA driver and depends on kernel integer types and work/timer/ALSA declarations already included by `aica.c`. It is tightly coupled to the firmware command block format.

## Risks And Edge Cases
Changing field order, command values, buffer sizes, or offsets can break firmware communication or DMA placement. Buffer and period constants are hard-coded into ALSA hardware constraints, DMA scheduling, and SPU memory layout.

## Test Signals
Tests should verify that channel control fields written by the driver match firmware expectations, pointer reads use the correct sample counter, and buffer/period constants remain consistent with ALSA hardware constraints and DMA transfer sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/aica.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/sh_dac_audio.c -->
# sources/distributed-fs/ceph-client/sound/sh/sh_dac_audio.c

## Purpose
`sh_dac_audio.c` is a simple ALSA playback driver for SuperH on-chip DAC audio. It supports mono unsigned 8-bit 8 kHz playback by copying user PCM data into a software buffer and emitting one byte per high-resolution timer tick through `sh_dac_output()`.

## Important APIs, Types, And Functions
The main private object is `struct snd_sh_dac`, containing the ALSA card/substream, hrtimer, sample interval, circular buffer pointers, processed-byte counter, platform data, and buffer size. Important functions include `dac_audio_start_timer()`, `dac_audio_stop_timer()`, `dac_audio_reset()`, `dac_audio_set_rate()`, PCM callbacks `snd_sh_dac_pcm_open()`, `close()`, `prepare()`, `trigger()`, `copy()`, `fill_silence()`, `pointer()`, the timer callback `sh_dac_audio_timer()`, `snd_sh_dac_create()`, `snd_sh_dac_pcm()`, and `snd_sh_dac_probe()`.

## Control Flow
Probe allocates an ALSA card and `snd_sh_dac`, initializes the hrtimer and 8 kHz interval, stores platform data, allocates a driver buffer, creates a playback PCM, and registers the card. Open initializes buffer pointers and calls the board-specific `pdata->start()`. Copy and silence fill regions in `data_buffer`, advance `buffer_end`, and start the timer if playback was empty. The hrtimer emits one sample through `sh_dac_output()`, advances the circular pointer, reports periods after enough bytes, marks the buffer empty when caught up, and rearms itself only while data remains.

## State And Persistence
State persists in the ALSA card private data, `data_buffer`, circular pointer fields, `empty`, `processed`, `buffer_size`, and platform data callbacks. Hardware state is owned by board platform data `start()`/`stop()` and the `sh_dac_output()` DAC function.

## Dependencies And Integration Points
The driver depends on `struct dac_audio_pdata` from `<sound/sh_dac_audio.h>`, SuperH DAC APIs from `<cpu/dac.h>`, HP6xx/HD64461 platform headers, hrtimers, and ALSA PCM managed buffers. It registers as platform driver `"dac_audio"`.

## Risks And Edge Cases
The timer callback assumes `chip->substream` and runtime remain valid while the timer is active, making stop/close ordering important. Buffer pointer and ALSA frame units are byte-oriented because the format is U8 mono; extending formats would need careful conversion. Timer-per-sample scheduling is CPU-sensitive. `buffer_begin == data_buffer + buffer_size - 1` wraps before the last byte, which should be checked against intended ring semantics.

## Test Signals
Test by probing with valid platform data, playing 8 kHz U8 mono streams, checking period notifications, pointer progression, underrun-to-empty behavior, copy/silence wakeups, trigger start/stop cycles, close-time timer cancellation, and board callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sh/sh_dac_audio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/Kconfig

## Purpose
`sound/soc/Kconfig` is the top-level configuration menu for ALSA System-on-Chip support. It enables the ASoC core, common helper features, KUnit test toggles, ACPI/USB integration, and sources all platform, codec, SOF, SoundWire utility, and generic machine-driver Kconfig files.

## Important APIs, Types, And Functions
Key symbols are `SND_SOC`, `SND_SOC_AC97_BUS`, `SND_SOC_GENERIC_DMAENGINE_PCM`, `SND_SOC_COMPRESS`, `SND_SOC_TOPOLOGY`, `SND_SOC_TOPOLOGY_BUILD`, `SND_SOC_TOPOLOGY_KUNIT_TEST`, `SND_SOC_CARD_KUNIT_TEST`, `SND_SOC_UTILS_KUNIT_TEST`, `SND_SOC_OPS_KUNIT_TEST`, `SND_SOC_ACPI`, and `SND_SOC_USB`. The file then sources vendor/platform Kconfig files including `sound/soc/adi/Kconfig` and `sound/soc/amd/Kconfig`.

## Control Flow
There is no runtime flow. Build-time flow starts with `menuconfig SND_SOC`; when enabled, helper symbols become selectable or selected by drivers, and sourced Kconfig files add SoC-specific options.

## State And Persistence
Configuration is persisted in `.config`. The selected symbols determine which ASoC core, test, platform, codec, and helper modules are built.

## Dependencies And Integration Points
This file integrates with `sound/soc/Makefile`, ALSA PCM, AC97, regmap I2C/SPI, jack support, compress offload, topology, ACPI matching, USB offload, SOF, codec, SoundWire utility, and all SoC vendor subdirectories.

## Risks And Edge Cases
Top-level select statements affect broad dependency closure. KUnit-only symbols intentionally build fake playback devices and should not be enabled accidentally in normal production configs. Adding a new vendor directory requires matching Kconfig source and Makefile object inclusion.

## Test Signals
Signals include `allmodconfig`, `allyesconfig`, tiny KUnit configs for topology/card/utils/ops tests, and platform-specific builds confirming sourced vendor Kconfigs expose expected symbols only when `SND_SOC` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/Makefile

## Purpose
`sound/soc/Makefile` builds the ASoC core, optional helper modules/tests, ACPI and USB support, and all enabled platform/codec/generic subdirectories.

## Important APIs, Types, And Functions
The central composite is `snd-soc-core-y`, made from core files such as `soc-core.o`, `soc-dapm.o`, `soc-jack.o`, `soc-pcm.o`, `soc-card.o`, and optional `soc-compress.o`, `soc-topology.o`, `soc-generic-dmaengine-pcm.o`, and `soc-ac97.o`. It also defines `snd-soc-acpi-y := soc-acpi.o`, KUnit test object inclusions, and recursive `obj-$(CONFIG_SND_SOC) += .../` entries for codecs, generic, ADI, AMD, SOF, and many other SoC vendors.

## Control Flow
There is no runtime flow. Kbuild expands composite objects and descends into subdirectories according to Kconfig symbols. Optional blocks use `ifneq ($(CONFIG_*),)` so built-in and module selections both include the relevant objects.

## State And Persistence
State is build output: built-in objects, modules, and subdirectory traversal. Runtime state belongs to the ASoC core and drivers built from these objects.

## Dependencies And Integration Points
This file pairs with `sound/soc/Kconfig` and every sourced platform Kconfig. It is the build integration point for ASoC core helper APIs consumed by the ADI AXI and AMD ACP files in this subset.

## Risks And Edge Cases
The recursive vendor list must stay synchronized with Kconfig sources. Optional helper object placement changes exported symbols available to drivers. KUnit object inclusion can create modules with fake devices and should remain tied to test symbols.

## Test Signals
Build signals include successful ASoC core module generation, ACPI/helper module generation when selected, KUnit test modules under KUnit configs, and vendor subdirectory traversal when `SND_SOC` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/adi/Kconfig

## Purpose
`sound/soc/adi/Kconfig` declares ASoC driver options for Analog Devices AXI softcore audio peripherals.

## Important APIs, Types, And Functions
The file defines `SND_SOC_ADI_AXI_I2S` for the AXI-I2S peripheral and `SND_SOC_ADI_AXI_SPDIF` for the AXI-SPDIF transmitter. Both are tristates and select `SND_SOC_GENERIC_DMAENGINE_PCM` and `REGMAP_MMIO`.

## Control Flow
There is no runtime flow. When either symbol is selected, kbuild includes the matching object from `sound/soc/adi/Makefile`, and the driver gets generic DMAengine PCM plus MMIO regmap support.

## State And Persistence
The persistent state is kernel configuration. Runtime state is held by the selected platform driver.

## Dependencies And Integration Points
This menu is sourced from the top-level ASoC Kconfig. Its symbols build `axi-i2s.c` and `axi-spdif.c`, which register OF platform drivers and ASoC components.

## Risks And Edge Cases
Both drivers depend on DMAengine and MMIO regmap helpers by selection rather than explicit user choice. Device-tree bindings must provide resources, clocks, and DMA names that match the corresponding driver expectations.

## Test Signals
Build tests should cover module and built-in combinations, and DT-based boot tests should confirm the selected drivers probe only when compatible nodes and required resources exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/adi/Makefile

## Purpose
`sound/soc/adi/Makefile` maps ADI ASoC Kconfig symbols to AXI softcore audio driver modules.

## Important APIs, Types, And Functions
It defines `snd-soc-adi-axi-i2s-y := axi-i2s.o` and `snd-soc-adi-axi-spdif-y := axi-spdif.o`, then includes those composites through `obj-$(CONFIG_SND_SOC_ADI_AXI_I2S)` and `obj-$(CONFIG_SND_SOC_ADI_AXI_SPDIF)`.

## Control Flow
There is no runtime flow. Kbuild uses the selected Kconfig symbols to produce built-in objects or modules.

## State And Persistence
Only build artifacts persist. Runtime state is in the platform drivers.

## Dependencies And Integration Points
This file is reached from `sound/soc/Makefile` when ASoC is enabled and pairs directly with `sound/soc/adi/Kconfig`.

## Risks And Edge Cases
Module naming is user-visible. Any source split or rename needs synchronized Kconfig, module alias, and packaging updates.

## Test Signals
Signals are successful builds of `snd-soc-adi-axi-i2s.ko` and `snd-soc-adi-axi-spdif.ko` under module configs, plus built-in link coverage under `y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/axi-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/adi/axi-i2s.c

## Purpose
`axi-i2s.c` is an ASoC CPU DAI driver for the Analog Devices AXI-I2S softcore. It registers playback and/or capture DAIs based on device-tree DMA names, programs frame clocking, controls TX/RX enables, and binds the generic DMAengine PCM backend to MMIO FIFO addresses.

## Important APIs, Types, And Functions
The main state is `struct axi_i2s`, containing regmap, AXI/ref clocks, capture/playback capability flags, DAI driver copy, DMA data, and rate constraints. Important functions include `axi_i2s_parse_of()`, `axi_i2s_probe()`, `axi_i2s_dev_remove()`, `axi_i2s_dai_probe()`, `axi_i2s_startup()`, `axi_i2s_shutdown()`, `axi_i2s_hw_params()`, and `axi_i2s_trigger()`.

## Control Flow
Probe allocates state, parses `dma-names` for `rx`/`tx`, maps registers, creates a 32-bit regmap, gets `axi` and `ref` clocks, enables the AXI clock, fills playback/capture DAI capabilities and DMA FIFO addresses for available directions, derives a rational rate constraint from the ref clock, globally resets the core, registers the ASoC component/DAI, and registers generic DMAengine PCM. PCM startup resets the selected FIFO, applies rate constraints, and enables the ref clock. `hw_params()` computes bit-clock rate for a fixed 64-bit frame and writes word size/divider. Trigger sets or clears TX/RX enable bits.

## State And Persistence
Persistent state lives in devm-managed `struct axi_i2s`, enabled clocks, regmap-visible core registers, DAI capabilities, and DMAengine configuration. PCM stream state is maintained by ASoC and DMAengine; this driver programs only core control and clocking.

## Dependencies And Integration Points
The driver integrates with OF compatible `adi,axi-i2s-1.00.a`, platform MMIO resources, named clocks `axi` and `ref`, `dma-names`, regmap MMIO, ASoC component/DAI registration, and generic DMAengine PCM.

## Risks And Edge Cases
`axi_i2s_dai` is a static template modified at probe time, which is risky if multiple instances with different capabilities probe. Divider calculation assumes a valid ref clock and can underflow if the requested rate exceeds feasible clocking. The frame size is fixed at 64 bits even though hardware is described as configurable. Remove disables only the AXI clock; stream shutdown handles ref clock balancing.

## Test Signals
Tests should cover playback-only, capture-only, and full-duplex DT nodes, missing clocks/resources, rate-constraint behavior, divider programming for supported rates, FIFO reset on startup, trigger enable/disable bits, DMA FIFO address correctness, and multiple-instance probing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/axi-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/axi-spdif.c -->
# sources/distributed-fs/ceph-client/sound/soc/adi/axi-spdif.c

## Purpose
`axi-spdif.c` is an ASoC CPU DAI driver for the Analog Devices AXI-SPDIF transmit softcore. It configures S/PDIF playback clock dividers/status rate bits, enables transmit data flow, and connects the TX FIFO to generic DMAengine PCM.

## Important APIs, Types, And Functions
The main state is `struct axi_spdif`, containing regmap, AXI/ref clocks, playback DMA data, and rate constraints. Important functions are `axi_spdif_probe()`, `axi_spdif_dev_remove()`, `axi_spdif_dai_probe()`, `axi_spdif_startup()`, `axi_spdif_shutdown()`, `axi_spdif_hw_params()`, and `axi_spdif_trigger()`.

## Control Flow
Probe allocates state, maps MMIO, initializes regmap, obtains `axi` and `ref` clocks, enables the AXI clock, sets TX FIFO DMA data, derives a rational rate constraint from `clk_ref / 128`, registers the component/DAI, and registers generic DMAengine PCM. Startup applies rate constraints, enables the ref clock, and sets the transmitter-enable bit. `hw_params()` writes S/PDIF status frequency bits for 32/44.1/48 kHz or NA, computes a clock divider from the ref clock and sample rate, and updates the control register. Trigger toggles TX data flow. Shutdown disables TX and the ref clock.

## State And Persistence
Runtime state is devm-managed driver data, enabled clocks, DMAengine PCM configuration, and the AXI-SPDIF control/status registers. ALSA stream state is held by ASoC and DMAengine.

## Dependencies And Integration Points
The driver binds OF compatible `adi,axi-spdif-tx-1.00.a`, platform MMIO, named clocks, regmap MMIO, ASoC DAI/component APIs, and generic DMAengine PCM. It exposes a stereo S16_LE playback-only DAI.

## Risks And Edge Cases
Clock divider calculation assumes feasible ref clock rates and does not explicitly mask overflow before `regmap_update_bits()`. Non-32/44.1/48 kHz rates are allowed by the rational constraint but mark S/PDIF frequency as not indicated. There is no capture path. Remove relies on devm cleanup and disables only the AXI clock.

## Test Signals
Tests should validate probe failure paths for missing clocks/resources, 32/44.1/48 kHz status bits, arbitrary constrained rates using `FREQ_NA`, trigger TXDATA toggling, startup/shutdown TXEN and ref-clock balancing, DMA FIFO address setup, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/adi/axi-spdif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/amd/Kconfig

## Purpose
`sound/soc/amd/Kconfig` declares AMD ASoC options for legacy ACP 2.x, ACP3x/Renoir/Vangogh/Yellow Carp/Pink Sardine families, machine drivers, shared ACP configuration selection, ACP common infrastructure, and SoundWire-capable newer platforms.

## Important APIs, Types, And Functions
Important symbols include `SND_SOC_AMD_ACP`, `SND_SOC_AMD_CZ_DA7219MX98357_MACH`, `SND_SOC_AMD_CZ_RT5645_MACH`, `SND_SOC_AMD_ST_ES8336_MACH`, `SND_SOC_AMD_ACP3x`, `SND_SOC_AMD_RENOIR`, `SND_SOC_AMD_ACP5x`, `SND_SOC_AMD_ACP6x`, `SND_AMD_ACP_CONFIG`, `SND_SOC_AMD_ACP63_TOPLEVEL`, `SND_SOC_AMD_SOUNDWIRE`, `SND_SOC_AMD_PS`, and `SND_SOC_AMD_PS_MACH`. It sources `sound/soc/amd/acp/Kconfig` for common ACP modules and machine drivers.

## Control Flow
There is no runtime flow. Config choices select codec drivers, ACPI matching, common ACP support, SOF/SoundWire helpers, and platform subdirectories. Many platform symbols select `SND_AMD_ACP_CONFIG`, which builds the machine configuration module used to choose legacy versus SOF paths.

## State And Persistence
Configuration state persists in `.config`; runtime state is held by the platform and machine drivers enabled by those symbols.

## Dependencies And Integration Points
The file integrates AMD ASoC with X86/PCI/ACPI, I2C/SPI/GPIO, codec drivers, SOF firmware matching, SoundWire, and the shared `amd/acp` common modules. It controls build inclusion in `sound/soc/amd/Makefile`.

## Risks And Edge Cases
Dependency and select chains are broad. Enabling a machine driver without required firmware, ACPI IDs, GPIOs, or codecs can build successfully but fail to probe. The legacy, SOF, and SoundWire paths overlap, so config and runtime machine selection must agree.

## Test Signals
Signals include build matrices for old ACP 2.x, ACP3x, Renoir, Vangogh, Yellow Carp, ACP6.3/7.x, SOF, and SoundWire configs; module dependency checks; and ACPI probe tests confirming the expected machine driver is selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/Makefile

## Purpose
`sound/soc/amd/Makefile` maps AMD ASoC Kconfig symbols to legacy ACP DMA/machine objects, platform-family subdirectories, and the newer common ACP implementation.

## Important APIs, Types, And Functions
Composite modules include `acp_audio_dma-y := acp-pcm-dma.o`, `snd-soc-acp-da7219mx98357-mach-y`, `snd-soc-acp-rt5645-mach-y`, `snd-soc-acp-es8336-mach-y`, `snd-soc-acp-rt5682-mach-y`, and `snd-acp-config-y := acp-config.o`. Object inclusion covers `acp_audio_dma.o`, legacy CZ/Stoney machine drivers, `raven/`, `renoir/`, `vangogh/`, `yc/`, `acp/`, `snd-acp-config.o`, and `ps/`.

## Control Flow
There is no runtime flow. Kbuild includes composites or descends into subdirectories based on AMD ASoC symbols.

## State And Persistence
Only build artifacts persist. Runtime state belongs to the built drivers.

## Dependencies And Integration Points
This Makefile pairs with `sound/soc/amd/Kconfig` and is reached from the top-level ASoC Makefile. It connects the files in this subset to their module names and platform directories.

## Risks And Edge Cases
Some symbols include both a subdirectory and a config module, e.g. `SND_AMD_ACP_CONFIG` builds `acp/` and `snd-acp-config.o`; mismatches can break machine selection. Module names are stable artifacts expected by userspace packaging and kernel auto-loading.

## Test Signals
Build tests should confirm each enabled symbol emits expected modules and subdirectory objects, especially combinations of legacy ACP DMA, `snd-acp-config`, and `amd/acp` common modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-config.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp-config.c

## Purpose
`acp-config.c` selects AMD ACP audio configuration paths and publishes ACPI machine tables for SOF-enabled AMD platforms. It decides whether a PCI ACP device should use SOF, legacy, or legacy-only-DMIC behavior using PCI revision, ACPI properties, and DMI quirks.

## Important APIs, Types, And Functions
The exported API is `snd_amd_acp_find_config()`. `snd_amd_acp_acpi_find_config()` reads `acp-audio-config-flag`. `config_table` maps selected DMI systems to `FLAG_AMD_SOF` or `FLAG_AMD_LEGACY`. `acp70_acpi_flag_override_table` suppresses ACPI flag use for a specific ASUS system. Exported machine arrays include `snd_soc_acpi_amd_sof_machines`, `snd_soc_acpi_amd_vangogh_sof_machines`, `snd_soc_acpi_amd_rmb_sof_machines`, `snd_soc_acpi_amd_acp63_sof_machines`, and `snd_soc_acpi_amd_acp70_sof_machines`.

## Control Flow
For revision zero, config selection returns 0. For ACP 7.0 or newer, the function returns 0 on the ASUS override or reads the ACPI integer flag, defaulting to legacy-only DMIC. For older revisions, it scans DMI entries matching the PCI device and returns the configured flags, updating global `acp_quirk_data`. SOF machine arrays then let ASoC/SOF matching pick driver names, codec-list quirks, firmware names, topology files, and platform data.

## State And Persistence
Persistent module state is `acp_quirk_data`, exported indirectly as `pdata` to matched machine drivers. The ACPI machine arrays are static exported tables consumed by platform/SOF probing.

## Dependencies And Integration Points
The file depends on ACPI, DMI, PCI, `../sof/amd/acp.h`, `mach-config.h`, and ASoC ACPI machine matching. It bridges low-level ACP PCI detection with machine-driver and SOF firmware/topology selection.

## Risks And Edge Cases
DMI matching is exact for many systems and broad for Google systems, so table order and specificity matter. ACP 7.x relies on BIOS ACPI flags except for overrides; incorrect firmware properties can route to the wrong stack. `acp_quirk_data` is global, so multi-device assumptions should be considered.

## Test Signals
Tests should cover revision zero, pre-7.0 DMI hits/misses, ACP7 ACPI property values, ASUS override behavior, SOF machine matching for listed codec IDs, firmware/topology filename selection, and multi-platform module load ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-da7219-max98357a.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp-da7219-max98357a.c

## Purpose
`acp-da7219-max98357a.c` is an AMD Carrizo/Stoney ASoC machine driver for boards using DA7219 or RT5682 headset codecs, MAX98357A speaker amplifier, and ADAU7002 DMICs. It defines DAI links, jack detection, clock handling, DAPM widgets/routes, and fixed regulator support for codec supplies.

## Important APIs, Types, And Functions
Key functions include `cz_da7219_init()`, `cz_rt5682_init()`, `da7219_clk_enable()`, `rt5682_clk_enable()`, startup callbacks for headset playback/capture, MAX playback, and two DMIC paths, `cz_da7219_shutdown()`, `cz_rt5682_shutdown()`, `acp_soc_is_rltk_max()`, and `cz_probe()`. Important data includes `cz_dai_7219_98357`, `cz_dai_5682_98357`, `cz_card`, `cz_rt5682_card`, `cz_jack`, DAPM widgets/routes, and `acp_da7219_desc`.

## Control Flow
ACPI matches either `"AMD7219"` or `"AMDI5682"` and passes the corresponding card. Probe optionally registers a fixed 1.8 V regulator for the DA7219 card, allocates `acp_platform_info`, attaches it to the card, registers the ASoC card, and updates `acp_bt_uart_enable` from the `bt-pad-enable` property. Codec init programs PLL/sysclk, obtains codec-generated DAI clocks, creates headset jack pins/buttons, and wires jack detection to the codec. Startup callbacks constrain streams to stereo 48 kHz, choose ACP I2S instance/capture channel in `acp_platform_info`, and enable the codec DAI clock.

## State And Persistence
State persists in global clock pointers, global `cz_jack`, static card/link tables, the per-card `acp_platform_info`, regulator registration, and global `acp_bt_uart_enable` used by the ACP DMA driver to select BT pad mode.

## Dependencies And Integration Points
The driver depends on ACPI IDs, DA7219/RT5682/MAX98357A/ADAU7002 codecs, codec clock providers, regulator framework, ASoC DAI link APIs, DAPM, jack/input key reporting, and `acp_audio_dma.0` plus DesignWare I2S CPU DAIs.

## Risks And Edge Cases
Clock globals assume one active card instance. Startup must pair with shutdown to avoid unbalanced codec clocks. The DA7219 fixed regulator is registered only for one card name. `acp_platform_info` is shared card state and is overwritten by each stream startup, so simultaneous streams rely on consistent values. `acp_bt_uart_enable` is global across ACP users.

## Test Signals
Test ACPI matching for both cards, card registration, regulator creation, jack and button events, 48 kHz/stereo constraints, each DAI link startup/shutdown, BT pad property behavior, playback/capture/DMIC routing, and suspend/resume through `snd_soc_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-da7219-max98357a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-es8336.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp-es8336.c

## Purpose
`acp-es8336.c` is an AMD Stoney/Jadeite ASoC machine driver for ES8336/ES8316 codec systems. It creates a single I2S codec link, constrains audio to stereo 48 kHz, manages headset jack detection, and controls an optional speaker amplifier GPIO through DAPM.

## Important APIs, Types, And Functions
Important functions include `sof_es8316_speaker_power_event()`, `st_es8336_init()`, `st_es8336_codec_startup()`, `st_es8336_late_probe()`, `st_es8336_quirk_cb()`, and `st_es8336_probe()`. Important data includes `st_jack`, `gpio_pa`, `st_dai_es8336`, `st_widgets`, `st_audio_route`, `st_mc_controls`, `acpi_es8336_gpios`, `st_card`, and `st_es8336_quirk_table`.

## Control Flow
Probe allocates `acp_platform_info`, checks DMI quirks to authorize supported systems, attaches the card and machine data, and registers the card. DAI init creates a headset jack with play/pause button support and calls `snd_soc_component_set_jack()`. Startup sets ES8336 sysclk to `48000 * 256`, enforces stereo 48 kHz constraints, and selects `I2S_MICSP_INSTANCE` for playback and capture with capture channel 0. Late probe finds the `ESSX8336` ACPI device, adds GPIO mappings, and obtains the `pa-enable` GPIO. DAPM speaker power events toggle that GPIO.

## State And Persistence
State persists in static card/link data, global jack and codec device/GPIO pointers, and per-card `acp_platform_info`. The speaker amplifier GPIO remains managed by DAPM event transitions.

## Dependencies And Integration Points
The driver depends on ACPI ID `"AMDI8336"`, DMI system matching, ES8316 codec DAI `"ES8316 HiFi"`, `designware-i2s.1`, `acp_audio_dma.0`, GPIO descriptor APIs, DAPM, jack/input APIs, and the ACP DMA platform data contract.

## Risks And Edge Cases
Unsupported DMI systems return `-ENODEV` even with matching ACPI ID. `gpio_pa` is global and can be NULL if GPIO mapping fails; DAPM event paths assume it is usable. Late probe holds a physical codec device reference and only releases it on one error path. The machine forces a single rate/channel configuration.

## Test Signals
Test DMI allowlist behavior, ACPI matching, codec sysclk programming, jack/button reporting, speaker GPIO on/off through DAPM, 48 kHz stereo constraints, playback/capture route setup, and error handling when the codec ACPI node or GPIO is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-es8336.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-pcm-dma.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp-pcm-dma.c

## Purpose
`acp-pcm-dma.c` implements the legacy AMD ACP 2.x ASoC PCM platform driver. It initializes ACP hardware, configures page tables and SRAM DMA descriptors, manages playback/capture DMA channels for I2S SP/BT/MICSP instances, handles period interrupts, exposes PCM callbacks to ASoC, and supports runtime/system resume.

## Important APIs, Types, And Functions
Private state is `struct audio_drv_data` for device-wide streams/MMIO/ASIC type and `struct audio_substream_data` for per-stream DMA configuration. Important helpers include `acp_reg_read()`, `config_acp_dma_channel()`, `config_dma_descriptor_in_sram()`, `acp_pte_config()`, `config_acp_dma()`, `acp_dma_start()`, `acp_dma_stop()`, `acp_set_sram_bank_state()`, `acp_init()`, `acp_deinit()`, `dma_irq_handler()`, PCM callbacks `acp_dma_open()`, `hw_params()`, `prepare()`, `trigger()`, `pointer()`, `delay()`, `close()`, and platform probe/remove/PM callbacks.

## Control Flow
Probe maps MMIO, requests the ACP IRQ, stores ASIC type from platform data, initializes ACP reset/clock/DAGB/PTE/descriptor state, registers the ASoC platform component, and enables runtime PM. Open allocates per-stream state, selects PCM hardware constraints, enables interrupts on the first stream, and powers SRAM banks. `hw_params()` reads `acp_platform_info` from the machine driver, selects channel numbers, SRAM banks, PTE offsets, descriptor indices, byte-count registers, and writes PTEs/descriptors. Trigger starts circular DMA chains for playback or capture, and stop resets channels. IRQ handling reports period elapsed for playback channels and advances capture SYSRAM descriptors.

## State And Persistence
State persists in ACP MMIO registers, SRAM descriptor/PTE tables, stream pointers in `audio_drv_data`, per-stream byte counters and DMA metadata, SRAM bank power state, runtime PM state, and exported `acp_bt_uart_enable`. Resume reinitializes ACP and reprograms active stream DMA state.

## Dependencies And Integration Points
The driver depends on `acp.h` register/channel constants, AMD ASIC IDs, platform data from ACP PCI/device creation, ASoC component PCM callbacks, machine-driver `acp_platform_info`, IRQ handling, PM runtime, and DesignWare I2S/codec machine links.

## Risks And Edge Cases
The driver has many fixed channel/descriptor mappings and ASIC-specific Stoney exceptions. Interrupt handlers dereference active stream pointers and rely on open/close ordering. DMA stop polls can time out. Capture pointer/delay accounting is descriptor-based and sensitive to byte counter wrap. Global `acp_bt_uart_enable` can affect pad selection across devices.

## Test Signals
Tests should cover each I2S instance and direction, Stoney versus Carrizo constraints, period interrupt cadence, capture descriptor alternation, pause/resume, runtime PM suspend/resume with active streams, SRAM bank power transitions, DMA timeout injection, and machine-driver platform-info combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-pcm-dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-rt5645.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp-rt5645.c

## Purpose
`acp-rt5645.c` is an AMD Carrizo ASoC machine driver for Realtek RT5645 codec systems. It defines playback and capture DAI links, codec PLL/sysclk programming, headset jack detection, DAPM endpoints, and card registration.

## Important APIs, Types, And Functions
Key functions are `cz_aif1_hw_params()`, `cz_init()`, and `cz_probe()`. Important data includes global `cz_jack`, `cz_jack_pins`, `cz_dai_rt5650`, `cz_widgets`, `cz_audio_route`, `cz_mc_controls`, `cz_card`, and the ACPI match table for `"AMDI1002"`.

## Control Flow
Probe binds `cz_card` to the platform device and registers it. DAI init creates a headset jack with headphone, microphone, and four button masks, then calls `rt5645_set_jack_detect()`. `hw_params()` configures codec PLL1 from 24 MHz MCLK to `rate * 512` and sets codec sysclk from PLL1. The two DAI links use `designware-i2s.1` for playback and `designware-i2s.2` for capture, both connected to `acp_audio_dma.0`.

## State And Persistence
State persists in static card/link definitions and the global jack object. Codec clocking is programmed per stream hardware-params call. No per-card `acp_platform_info` is used here, so the DMA driver defaults to its standard I2S instance behavior.

## Dependencies And Integration Points
The driver depends on ACPI, RT5645 codec APIs, ASoC DAPM/jack/card registration, DesignWare I2S CPU DAIs, and the legacy ACP DMA platform driver.

## Risks And Edge Cases
The driver assumes fixed ACPI codec name `i2c-10EC5650:00` and DAI name `rt5645-aif1`. There is no custom startup constraint path, so unsupported rates/channels must be rejected by lower layers or codec/CPU DAI constraints. Static global card state limits multiple-instance safety.

## Test Signals
Test ACPI probe, playback and capture stream setup, PLL/sysclk rates for common sample rates, jack insert/button events, DAPM pin switches/routes for headphones/speakers/mics, and suspend/resume through `snd_soc_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp-rt5645.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp.h -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp.h

## Purpose
`acp.h` defines register constants, SRAM addresses, DMA channel/descriptor IDs, I2S instance IDs, tile/power masks, and private data structures for the legacy AMD ACP 2.x PCM DMA driver and related machine drivers.

## Important APIs, Types, And Functions
Important definitions include ACP PTE offsets, SRAM bank addresses, DMA timeout constants, I2S route IDs, DMA channel numbers for SP/BT/MICSP instances, descriptor indices, `mmACP_I2S_16BIT_RESOLUTION_EN`, `enum acp_dma_priority_level`, `struct audio_substream_data`, `struct audio_drv_data`, `struct acp_platform_info`, `union acp_dma_count`, tile and DMA attribute enums, `acp_dma_dscr_transfer_t`, and exported `acp_bt_uart_enable`.

## Control Flow
There is no executable flow. `acp-pcm-dma.c` fills `audio_substream_data` from ALSA stream parameters and machine-driver `acp_platform_info`, then uses the constants to program ACP PTEs, descriptors, SRAM banks, byte counters, and DMA channel control.

## State And Persistence
The structures define persistent runtime state for device and stream objects. The macros encode hardware topology and descriptor layout that persists in ACP SRAM/register programming while streams are active.

## Dependencies And Integration Points
The header includes generated ACP 2.2 register definitions and is shared by legacy machine drivers and `acp-pcm-dma.c`. It is the contract through which machine drivers select playback/capture I2S instances and capture channels.

## Risks And Edge Cases
Wrong constants can route DMA to the wrong SRAM bank, I2S instance, descriptor, or byte counter. `acp_platform_info` is small but critical; missing or stale values cause the DMA driver to use defaults. The external `acp_bt_uart_enable` creates global coupling with machine driver properties.

## Test Signals
Tests should validate every constant path indirectly through playback/capture on SP, BT, and MICSP instances, descriptor programming inspection, byte-counter pointer checks, Stoney offsets, and BT pad selection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/Kconfig

## Purpose
`sound/soc/amd/acp/Kconfig` declares the newer common AMD ACP ASoC infrastructure, platform drivers for Renoir/Rembrandt/ACP6.3/ACP7.0, shared PCM/I2S/PDM components, ACPI machine matching, legacy/SOF machine drivers, and SoundWire machine support.

## Important APIs, Types, And Functions
Important symbols include `SND_SOC_AMD_ACP_COMMON`, `SND_SOC_ACPI_AMD_MATCH`, `SND_SOC_AMD_ACP_PDM`, `SND_SOC_AMD_ACP_LEGACY_COMMON`, `SND_SOC_AMD_ACP_I2S`, `SND_SOC_AMD_ACPI_MACH`, `SND_SOC_AMD_ACP_PCM`, `SND_SOC_AMD_ACP_PCI`, `SND_AMD_ASOC_RENOIR`, `SND_AMD_ASOC_REMBRANDT`, `SND_AMD_ASOC_ACP63`, `SND_AMD_ASOC_ACP70`, `SND_SOC_AMD_MACH_COMMON`, `SND_SOC_AMD_LEGACY_MACH`, `SND_SOC_AMD_SOF_MACH`, SoundWire machine symbols, and `SND_AMD_SOUNDWIRE_ACPI`.

## Control Flow
There is no runtime flow. Enabling `SND_SOC_AMD_ACP_COMMON` exposes internal module symbols and platform choices. Platform symbols select PCM/I2S/PDM/common/machine pieces. Machine symbols select codec dependencies and shared machine helpers. SoundWire symbols add SDW utility and codec dependencies.

## State And Persistence
Build configuration persists in `.config`. Runtime state is in the built ACP PCI/platform, PCM, I2S, PDM, and machine drivers.

## Dependencies And Integration Points
This file is sourced by `sound/soc/amd/Kconfig` and paired with `sound/soc/amd/acp/Makefile`. It integrates with X86, PCI, ACPI, AMD_NODE, I2C, SoundWire, SOF, codec drivers, and ASoC ACPI matching.

## Risks And Edge Cases
The select graph is complex and can pull many codec drivers into a build. Platform symbols require matching PCI/ACPI hardware and machine tables. SoundWire variants depend on both AMD SoundWire support and codec-specific SDW drivers.

## Test Signals
Build matrices should cover each platform symbol, legacy versus SOF machines, SoundWire legacy/SOF machines, and ACPI match helpers, with module dependency checks for selected codec drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/Makefile

## Purpose
`sound/soc/amd/acp/Makefile` builds the modular AMD ACP common stack: PCM, I2S, PDM, PCI, platform-specific drivers, ACPI matching, legacy/SOF machine drivers, and SoundWire helpers.

## Important APIs, Types, And Functions
Composites include `snd-acp-pcm-y`, `snd-acp-i2s-y`, `snd-acp-pdm-y`, `snd-acp-legacy-common-y`, `snd-acp-pci-y`, `snd-amd-sdw-acpi-y`, `snd-amd-acpi-mach-y`, platform drivers `snd-acp-renoir-y`, `snd-acp-rembrandt-y`, `snd-acp63-y`, `snd-acp70-y`, machine drivers `snd-acp-mach-y`, `snd-acp-legacy-mach-y`, `snd-acp-sof-mach-y`, ACPI match modules, and SoundWire machine modules.

## Control Flow
There is no runtime flow. Kbuild composes modules and objects according to the `CONFIG_SND_*` symbols declared in the adjacent Kconfig.

## State And Persistence
Only build artifacts persist. Runtime state belongs to the generated drivers.

## Dependencies And Integration Points
The Makefile is included through `sound/soc/amd/Makefile` when `SND_AMD_ACP_CONFIG` selects the `acp/` subdirectory. It ties the common code in `acp-i2s.c`, `acp-legacy-common.c`, and `acp-legacy-mach.c` to module names.

## Risks And Edge Cases
Machine modules aggregate subdirectory objects such as `acp3x-es83xx`. Kconfig and Makefile drift would break module composition or exported namespace availability. Some objects import/export namespaces, so missing module pieces can fail at link or load time.

## Test Signals
Signals include successful module builds for PCM/I2S/PDM/common/PCI/platform/machine/SDW variants and namespace import/export checks under `modpost`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-i2s.c

## Purpose
`acp-i2s.c` implements generic ASoC CPU DAI operations for AMD ACP I2S/TDM controllers across Renoir, Rembrandt, ACP6.3, and ACP7.x style hardware. It sets format/TDM slots, programs sample resolution and master clock dividers, prepares ring/FIFO registers, and enables/disables stream interrupts.

## Important APIs, Types, And Functions
The exported object is `asoc_acp_cpu_dai_ops`. Important helpers include `acp_set_i2s_clk()`, `acp_i2s_set_fmt()`, `acp_i2s_set_tdm_slot()`, `acp_i2s_hwparams()`, `acp_i2s_prepare()`, `acp_i2s_startup()`, and `acp_i2s_trigger()`. It operates on `struct acp_chip_info`, `struct acp_resource`, and `struct acp_stream` from `amd.h`.

## Control Flow
Startup maps the DAI ID and stream direction to an IRQ bit, PTE offset, FIFO offset, and stream identity. `set_fmt()` switches between I2S and DSP_A/TDM mode. `set_tdm_slot()` validates slot width/count based on ACP generation and stores TX/RX format words for streams with matching DAI IDs. `hw_params()` translates sample format to hardware resolution, writes ITER/IRER sample length, writes TDM format if enabled, and computes LRCLK/BCLK dividers when SoC MCLK is present. Prepare configures DMA size, FIFO address/size, ring buffer address, and external interrupt mask. Trigger writes watermark/buffer size, optionally programs master clock, enables ITER/IRER and IER on start, and clears stream enable plus shared IERs on stop.

## State And Persistence
State persists in `acp_chip_info` arrays for TDM formats and transfer resolutions, `lrclk_div`, `bclk_div`, `tdm_mode`, and `acp_stream` fields such as `dai_id`, `irq_bit`, offsets, direction, and byte count. Hardware state persists in ACP I2STDM/BTTDM/HSTDM registers until stopped or reinitialized.

## Dependencies And Integration Points
The file depends on ASoC DAI callbacks, ACP register macros/resources from `amd.h`, stream allocation by the ACP PCM platform component, interrupt handling in `acp-legacy-common.c`, and platform drivers that register CPU DAIs using `asoc_acp_cpu_dai_ops`.

## Risks And Edge Cases
Generation-specific field layouts differ for ACP6.3/7.x versus older hardware. TDM slot settings are applied by scanning current streams, so order between stream startup and machine `set_tdm_slot()` matters. Some unsupported channel counts log errors but do not immediately return in one branch. Register address selection for ACP7.x uses different memory windows.

## Test Signals
Tests should cover I2S and DSP_A modes, slot widths 8/16/24/32, slot-count limits per generation, S16/S24/S32 rates and dividers, SP/BT/HS playback and capture prepare paths, trigger start/stop interrupt bits, and resume restoration of stored formats/resolutions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-common.c

## Purpose
`acp-legacy-common.c` provides common hardware operations for legacy/non-SOF AMD ACP ASoC platforms. It defines per-generation resources, IRQ handling, PDM/I2S parameter restoration, ACP power/reset init/deinit, machine-device selection, pin-configuration detection, and hardware-op initialization for ACP3.1, ACP6.x, ACP6.3, and ACP7.x.

## Important APIs, Types, And Functions
Exported resources include `rn_rsrc`, `rmb_rsrc`, `acp63_rsrc`, and `acp70_rsrc`. Exported functions include `acp_irq_handler()`, `acp_enable_interrupts()`, `acp_disable_interrupts()`, `restore_acp_pdm_params()`, `restore_acp_i2s_params()`, `acp_init()`, `acp_deinit()`, `acp_machine_select()`, `check_acp_config()`, and `acp31_hw_ops_init()`, `acp6x_hw_ops_init()`, `acp63_hw_ops_init()`, `acp70_hw_ops_init()`.

## Control Flow
IRQ handling reads one or two external interrupt status registers, scans `chip->stream_list` under the ACP spinlock, clears matching stream bits, and calls `snd_pcm_period_elapsed()`. Init powers on ACP through generation-specific PGFSM registers, enables ACP control, performs soft reset, and clears ACP7 zero-shutdown DSP control. Deinit resets and disables control or sets ACP7 DSP control. Config detection reads pin config registers, checks ACPI child PDM devices and `_WOV`, and marks I2S/PDM availability. Machine selection either registers an `acp-pdm-mach` platform device for legacy-only DMIC or finds an ACPI machine and registers its driver name.

## State And Persistence
State persists in `acp_chip_info`: resource pointer, base MMIO, stream list, lock, revision, flags, machine table, PDM/I2S config booleans, channel masks, TDM/format arrays, and selected machine platform device. Hardware state persists in ACP power, reset, interrupt, PDM, I2S, ring, FIFO, and clock registers.

## Dependencies And Integration Points
The file depends on `amd.h`, ACPI, PCI, `mach-config.h`, ASoC ACPI machine matching, ACP PCM/I2S/PDM drivers, and machine drivers registered by name. It exports symbols under namespace `SND_SOC_ACP_COMMON`.

## Risks And Edge Cases
IRQ handling calls period elapsed while holding a spinlock, relying on ALSA expectations. Machine selection returns 0 even if platform-device registration fails after warning. Pin-config interpretation is generation-specific and can misclassify hardware if BIOS values change. ACPI `_WOV` can override child-device evidence for PDM presence.

## Test Signals
Test ACP init/deinit timeout paths, IRQ delivery for active streams on one- and two-controller resources, PDM and I2S restoration after resume, machine selection with matching/missing ACPI machines, pin-config matrices per generation, `_WOV` overrides, and namespace/module dependency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-mach.c -->
# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-mach.c

## Purpose
`acp-legacy-mach.c` is the generic legacy AMD ACP machine driver. It maps platform device IDs to codec/CPU/DMIC topology data, invokes shared machine construction helpers, applies ES83xx-specific ops when needed, handles suspend/resume hooks, and registers dynamically created ASoC cards.

## Important APIs, Types, And Functions
Important static card-data templates include `rt5682_rt1019_data`, `rt5682s_max_data`, `rt5682s_rt1019_data`, `es83xx_rn_data`, `max_nau8825_data`, `rt5682s_rt1019_rmb_data`, and `acp_dmic_data`. Key functions are `acp_asoc_init_ops()`, `acp_asoc_suspend_pre()`, `acp_asoc_resume_post()`, and `acp_asoc_probe()`. `board_ids` maps platform names to templates.

## Control Flow
Probe requires a matching platform ID, allocates an `snd_soc_card`, attaches the template as driver data, stores the `snd_soc_acpi_mach`, initializes codec-specific ops for ES83xx, configures widgets, calls shared probe hooks, records ACP revision from either PDM platform data or ACPI machine params, applies DMI TDM mode quirks, creates DAI links with `acp_legacy_dai_links_create()`, and registers the card. Suspend/resume wrappers normalize a shared helper return value of 1 into success.

## State And Persistence
Card state persists in the devm-allocated `snd_soc_card` and shared `acp_card_drvdata` templates. The templates include CPU IDs, codec IDs, DMIC IDs, SoC MCLK/TDM flags, ACP revision, and ACPI machine pointer. Because templates are static and modified at probe time, they behave as module-global state.

## Dependencies And Integration Points
The driver depends on `acp-mach-common` helpers, ES83xx support under `acp3x-es83xx`, ASoC ACPI machine data, DMI quirks, platform devices created by `acp_machine_select()`, and namespace `SND_SOC_AMD_MACH`.

## Risks And Edge Cases
Static template mutation is not multi-instance friendly. Missing `id_entry` fails probe. If widget/probe/link creation helpers fail, the card is not registered. TDM mode quirks overwrite the template flag globally. The special `acp-pdm-mach` path interprets platform data as an `int` revision.

## Test Signals
Test each `board_ids` platform name, ES83xx ops initialization, PDM-only machine path, DMI TDM quirk application, generated DAI link contents, suspend/resume helper return normalization, registration failure paths, and multiple probe attempts for shared template side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-legacy-mach.c -->
