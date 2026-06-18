# subset-b-006558 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/cs4231.c -->
# sources/distributed-fs/ceph-client/sound/sparc/cs4231.c

## Purpose
This file is the ALSA platform driver for Sun SPARC CS4231 audio devices found behind SBus APC DMA or EBus DMA. It detects Open Firmware nodes named `SUNW,CS4231`/`audio`, creates one ALSA card with one full-duplex PCM, a card timer, and CS4231 mixer controls, and hides the different SBus and EBus DMA engines behind a common `cs4231_dma_control` callback table.

## Important APIs, types, and functions
`struct snd_cs4231` is the driver state: ALSA card/PCM/timer pointers, mapped register base, platform device, IRQs, codec register image, MCE/open mutexes, register spinlock, playback/capture substreams, period counters, and two `cs4231_dma_control` objects. `struct cs4231_dma_control` abstracts `prepare`, `enable`, `request`, and current-address callbacks for SBus APC and EBus DMA.

Codec access is through `__cs4231_readb`, `__cs4231_writeb`, `snd_cs4231_ready`, `snd_cs4231_out`, `snd_cs4231_outm`, and `snd_cs4231_in`. Mode-change and calibration are managed by `snd_cs4231_mce_up`, `snd_cs4231_mce_down`, `snd_cs4231_calibrate_mute`, and `snd_cs4231_init`. PCM behavior is implemented by `snd_cs4231_playback_open`, `snd_cs4231_capture_open`, `snd_cs4231_*_hw_params`, `snd_cs4231_*_prepare`, `snd_cs4231_trigger`, and pointer callbacks. Mixer controls use generic single/double/mux helpers over the cached register image.

## Control flow
`cs4231_probe` dispatches to SBus or EBus probe based on the parent OF node. Both paths call `cs4231_attach_begin`, allocate a managed ALSA card, map device resources, initialize locks and the default register image, bind the proper DMA callback table, detect the chip with `snd_cs4231_probe`, initialize codec registers, then finish by creating PCM, mixer, timer, and registering the card.

Opening playback or capture reserves the respective mode under `open_mutex`, clears pending IRQ state on first open, stores the substream, applies the rate constraint list, and enables sync-start semantics. `hw_params` computes the CS4231 playback or capture format byte from ALSA format, channel count, and one of the fixed supported rates, then programs it inside MCE with outputs muted during calibration-sensitive transitions. `prepare` clears the enable bits and resets period counters. `trigger` handles grouped start/stop for playback and capture, prepares/enables DMA, prequeues periods through `snd_cs4231_advance_dma`, and updates `CS4231_IFACE_CTRL`.

SBus interrupts acknowledge APC and codec status, call playback/capture period callbacks when next-address interrupts arrive, dispatch card timer ticks, and count overrange on capture IRQs. EBus uses DMA callbacks for playback/capture period completion instead of the SBus APC interrupt path. Removal frees the ALSA card, which invokes low-level device free hooks to release IRQs, DMA registrations, and mappings.

## State and persistence behavior
The driver persists no on-disk state. Runtime state is the codec register image, open mode bitmask, MCE bit, calibration mute flag, ALSA substream pointers, DMA queue period counters, and platform resource mappings. The register image is authoritative for mixer values and is replayed to hardware during updates. DMA state is split between the ALSA runtime buffer and the hardware-specific DMA engine, which is kept fed one period at a time.

## Dependencies and integration points
This driver integrates Linux platform/Open Firmware probing, SBus helpers, optional SPARC64 PCI/EBus DMA helpers, ALSA core, ALSA PCM, mixer controls, and ALSA timer. It depends on `sound/cs4231-regs.h` register definitions, SPARC bus I/O primitives, platform IRQ/resource data, and the old CS4231 fixed-rate clock table.

## Risks and edge cases
The most fragile areas are MCE/calibration ordering, interrupt acknowledgement, and DMA period queueing. `snd_cs4231_advance_dma` loops until the DMA engine refuses another period; incorrect `request` semantics could spin or overqueue. Period sizes must fit the 24-bit APC count and the code warns on larger values. EBus and SBus register spacing differs, so the `CS4231_FLAG_EBUS` read/write split is critical. `snd_cs4231_timer_open` ignores the return from `snd_cs4231_open`, so timer open conflicts are not propagated. Power management is explicitly left as a TODO.

## Test signals
Useful signals are successful probe on SBus and EBus systems, card registration with PCM/mixer/timer, playback and capture at every listed fixed rate and supported format, sync-start full-duplex trigger, period interrupts advancing without stalls, pointer values staying inside the ring buffer, mixer changes matching hardware output, capture overrange increments, timer tick delivery, and clean remove after partial probe failures. Kernel diagnostics around auto-calibration timeout, invalid chip ID, IRQ request failure, and DMA registration failure are high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/cs4231.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/dbri.c -->
# sources/distributed-fs/ceph-client/sound/sparc/dbri.c

## Purpose
This file is the ALSA SBus driver for Sun DBRI audio hardware paired with a CS4215 multimedia codec. It programs the DBRI command queue, interrupt queue, CHI time-slot fabric, data pipes, and DMA descriptors, then exposes the CS4215 as one full-duplex ALSA PCM plus mixer controls and proc diagnostics.

## Important APIs, types, and functions
`struct snd_dbri` owns the mapped DBRI registers, coherent `struct dbri_dma` command/interrupt/descriptor block, command pointer and lock, interrupt queue cursor, 32 pipe records, descriptor links, CS4215 state, and playback/capture `dbri_streaminfo`. `struct dbri_pipe` tracks each DBRI pipe's SDP word, time-slot linkage, active descriptor, descriptor ring head, and fixed-data receive target. `struct cs4215` stores data/control time-slot images, codec status/version, detected onboard/speakerbox selection, frame offset, precision, and channels.

DBRI command synchronization is handled by `dbri_cmdlock`, `dbri_cmdsend`, `dbri_cmdwait`, `dbri_reset`, and `dbri_initialize`. Pipe and time-slot setup flows through `setup_pipe`, `reset_pipe`, `link_time_slot`, `xmit_fixed`, `recv_fixed`, `setup_descs`, and `xmit_descs`. CS4215 control is implemented by `cs4215_setup_pipes`, `cs4215_init_data`, `cs4215_setdata`, `cs4215_setctrl`, `cs4215_open`, `cs4215_prepare`, and `cs4215_init`. ALSA callbacks are collected in `snd_dbri_ops`.

## Control flow
`dbri_probe` allocates an ALSA card, maps the SBus resource, allocates the coherent command/interrupt/descriptor block, requests the shared IRQ, initializes DBRI, probes/configures CS4215, then creates PCM, mixer, proc entries, and registers the card. `dbri_initialize` resets DBRI, initializes pipe state, sets the circular interrupt queue, writes the first command pointer to register 8, and waits for completion.

The CS4215 probe detects onboard versus speakerbox codec through PIO bits, creates fixed and memory pipes for control/data modes, enables fixed receive for status/version slots, sends control mode frames, then leaves the codec in data mode. PCM open initializes per-stream state, installs format/channel constraints, and opens CS4215 data mode. `hw_params` programs CS4215 rate/format/channels and maps the ALSA runtime buffer for DBRI DMA. `prepare` selects pipe 4 for playback or pipe 6 for capture, builds a descriptor ring split by period and DBRI maximum descriptor size, and resets the stream offset. `trigger START` submits descriptor rings with SDP commands; `STOP` clears the pipe.

Interrupts read DBRI register 1 to acknowledge and detect SBus errors, then drain nonzero words from the circular interrupt buffer. Buffer-ready interrupts advance receive descriptors and call `snd_pcm_period_elapsed`; transmit-complete and marker interrupts walk completed transmit descriptors, reset status, update offsets, and notify ALSA. Fixed-data-change interrupts reverse bit order if needed and update CS4215 status/version memory.

## State and persistence behavior
There is no filesystem persistence. Device-visible state lives in the coherent `dbri_dma` block and hardware registers. Host state tracks a circular command buffer terminated by WAIT/JUMP pairs, an interrupt queue pointer, descriptor rings, pipe linkages, CS4215 register images, and ALSA stream offsets. Mixer controls update cached CS4215 data/control bytes and send fixed CHI data, muting briefly before changes to reduce clicks. Runtime DMA mappings are established in `hw_params` and released in `hw_free`.

## Dependencies and integration points
The driver depends on SPARC SBus register access, Open Firmware platform resources, DMA mapping APIs, ALSA card/PCM/control/proc APIs, and MIDI-independent CS4215 audio formatting knowledge. It integrates with `SNDRV_DMA_TYPE_CONTINUOUS` buffers, shared IRQ handling, and `/proc/asound` diagnostics. The code is specific to DBRI+CS4215 timing, PIO wiring, and CHI frame layout.

## Risks and edge cases
Command queue wrapping and DBRI reread semantics are subtle; wrong command lengths or locking can corrupt the queue. Descriptor accounting mixes descriptor byte counts, period sizes, and `runtime->buffer_size`; DMA unmap uses frame count as a byte length, which is a risk to audit. `snd_cs4215_put_single` computes `changed` after overwriting cached bytes, so change reporting can be wrong. CS4215 mode switching relies on microsecond delays and fixed offsets, with a known limitation for 8-bit stereo. Interrupt handlers drop and reacquire `dbri->lock` around ALSA callbacks, so close/stop races need care. Underrun recovery is mostly a FIXME.

## Test signals
Test probe on DBRIe/DBRIf nodes with onboard and speakerbox codecs, successful CS4215 version detection, playback/capture for supported rates and formats, constraints forcing stereo to S16_BE, descriptor ring wrap without pointer jumps, period interrupts on both directions, mixer volume/switch updates with audible changes, proc `regs` output, clean remove, and behavior under underrun/SBus error logs. Fault injection around DMA allocation, register mapping, IRQ request, and CS4215 no-response paths is valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/sparc/dbri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/Kconfig -->
# sources/distributed-fs/ceph-client/sound/spi/Kconfig

## Purpose
This Kconfig file defines the ALSA SPI sound-device menu and the AT73C213 DAC driver options.

## Important APIs, types, and functions
`menuconfig SND_SPI` enables the SPI sound-device subtree when `SPI` is available. `config SND_AT73C213` is the tristate symbol for the Atmel AT73C213 DAC driver and selects `SND_PCM`. `config SND_AT73C213_TARGET_BITRATE` is an integer build-time target sample rate used by the driver bitrate calculator.

## Control flow
There is no runtime control flow. At configuration time, enabling `SND_SPI` reveals `SND_AT73C213`; enabling that driver reveals the target bitrate prompt with an 8000 to 50000 range and 48000 default.

## State and persistence behavior
The file persists only kernel configuration symbols. `CONFIG_SND_AT73C213_TARGET_BITRATE` is compiled into `at73c213.c` and affects clock divisor search at probe time.

## Dependencies and integration points
It integrates ALSA SPI audio with the kernel Kconfig system. The driver depends on `ATMEL_SSC` and SPI support, and it produces a `snd-at73c213` module when built as `m`.

## Risks and edge cases
The bitrate is compile-time, not runtime PCM-configurable; users may expect arbitrary PCM rates but the driver restricts runtime to the calculated `chip->bitrate`. Missing `ATMEL_SSC` hides the driver even if SPI is enabled.

## Test signals
Configuration tests should verify visibility under `SPI`, hidden behavior without `ATMEL_SSC`, module naming as `snd-at73c213`, and compile-time propagation of nondefault bitrate values inside the valid range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/Makefile -->
# sources/distributed-fs/ceph-client/sound/spi/Makefile

## Purpose
This Kbuild file builds the ALSA SPI AT73C213 driver module.

## Important APIs, types, and functions
`snd-at73c213-y := at73c213.o` defines the module contents. `obj-$(CONFIG_SND_AT73C213) += snd-at73c213.o` links the module or built-in object based on the Kconfig symbol.

## Control flow
There is no runtime flow. Kbuild compiles `at73c213.c` into `at73c213.o` and links it into `snd-at73c213.o` when configured.

## State and persistence behavior
The Makefile has only static build-graph state.

## Dependencies and integration points
It depends on the kernel ALSA and SPI build hierarchy and must remain aligned with `Kconfig` and the `module_spi_driver` entry in `at73c213.c`.

## Risks and edge cases
Adding helper source files for the driver requires extending `snd-at73c213-y`; otherwise symbols will be unresolved. Disabling `CONFIG_SND_AT73C213` omits the driver regardless of source presence.

## Test signals
Build with `CONFIG_SND_AT73C213=m` and `=y`, verify the resulting `snd-at73c213` target, and verify no object is emitted when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/at73c213.c -->
# sources/distributed-fs/ceph-client/sound/spi/at73c213.c

## Purpose
This file is the ALSA SPI driver for the Atmel AT73C213 16-bit stereo DAC attached to an Atmel SSC serial controller. It configures clocks and SSC transmit framing, initializes the DAC over SPI, exposes one playback-only PCM device at one calculated bitrate, provides DAC mixer controls, handles SSC transmit interrupts, and implements basic suspend/resume and power-down sequencing.

## Important APIs, types, and functions
`struct snd_at73c213` owns the ALSA card/PCM/substream, platform board data, SSC device, SPI device, IRQ, calculated bitrate, current period index, cached DAC register image, SPI buffers, SSC spinlock, and mixer mutex. `snd_at73c213_write_reg` is the SPI register write boundary and updates `reg_image` on success. `snd_at73c213_set_bitrate` computes SSC and DAC clock rates from `CONFIG_SND_AT73C213_TARGET_BITRATE`.

PCM callbacks are `snd_at73c213_pcm_open`, `close`, `hw_params`, `prepare`, `trigger`, and `pointer`. `snd_at73c213_interrupt` maintains the SSC PDC next-buffer registers and notifies ALSA period completion. Mixer access is implemented by mono/stereo get/put helpers and `snd_at73c213_controls`. Device setup is performed by `snd_at73c213_ssc_init`, `snd_at73c213_chip_init`, `snd_at73c213_dev_init`, `snd_at73c213_probe`, and `snd_at73c213_remove`.

## Control flow
Probe requires `spi->dev.platform_data` with a valid `at73c213_board_info` and DAC clock. It allocates an ALSA card, requests the SSC by board `ssc_id`, initializes locks, enables the SSC clock, requests the SSC IRQ, seeds `reg_image`, programs SSC transmit clock/frame registers, calculates the final bitrate, powers and precharges the DAC via SPI writes and delays, creates PCM and mixer controls, registers a low-level device for cleanup, then registers the ALSA card.

On PCM open, the runtime hardware rate range is narrowed to the calculated bitrate and the SSC clock is enabled. `hw_params` updates SSC transmit frame word count for mono or stereo. `prepare` programs current and next PDC transmit pointers/counts for the first two periods. `trigger START` enables ENDTX interrupts and PDC TX; `STOP` disables PDC TX and the interrupt. On ENDTX, the IRQ handler advances `chip->period`, programs the next PDC buffer, releases the spinlock, and calls `snd_pcm_period_elapsed`.

Remove stops SSC TX, mutes outputs, powers down PA and DAC in a timed sequence, disables the DAC master clock, frees SSC, and frees the ALSA card. Suspend disables SSC TX and both clocks; resume re-enables the DAC and SSC clocks and TX.

## State and persistence behavior
No disk state is used. Runtime state includes the fixed calculated bitrate, `reg_image`, current substream pointer, period index, SSC PDC register state, and clock enable state. Mixer state is cached in `reg_image` and written to hardware through SPI. The driver does not replay the cached register image on resume; resume only re-enables clocks and SSC TX.

## Dependencies and integration points
The driver depends on Linux SPI, the legacy Atmel SSC API, platform `at73c213_board_info`, Linux clock APIs, IRQ handling, ALSA card/PCM/control APIs, and register constants from `at73c213.h`. The PCM buffer is allocated against the SSC platform device.

## Risks and edge cases
The IRQ handler dereferences `chip->substream` unconditionally, so interrupts when no playback is open would be hazardous if ENDTX is left enabled. Clock enable/disable balancing is spread across probe, open/close, suspend/resume, and remove. The driver supports only `S16_BE` and one runtime rate, which can surprise user space. Resume does not reinitialize DAC registers after power loss. `AT73C213_MONO_SWITCH` contains a duplicate `.info` initializer. DMA pointer math casts DMA addresses through `long`, which is architecture-sensitive. Remove continues cleanup even if an SPI mute write fails, but some power-down steps may be skipped by `goto out`.

## Test signals
Test probe with valid and missing platform data, bitrate calculation logs for several target rates, playback at the reported fixed rate in mono and stereo, period interrupt continuity, pointer wrap, mixer control read/write effects, suspend/resume during idle and playback, and remove power-down without leaked IRQ or SSC reference. Negative tests should cover invalid clocks, unavailable SSC, IRQ request failure, and SPI write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/at73c213.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/at73c213.h -->
# sources/distributed-fs/ceph-client/sound/spi/at73c213.h

## Purpose
This private header defines AT73C213 DAC register addresses and bit positions used by the SPI driver.

## Important APIs, types, and functions
It defines register addresses for DAC control, line input gain, master playback gain, line out gain, output level control, mixer control, clock/sample-frequency control, miscellaneous settings, precharge, auxiliary gain, reset, and power amplifier control. For each register, bit-position macros such as `DAC_CTRL_ONDACL`, `DAC_PRECH_ONMSTR`, and `PA_CTRL_APAON` describe fields used by initialization, mixer, and power-down code.

## Control flow
There is no executable control flow. The macros feed SPI register writes in `at73c213.c`, especially chip initialization, mixer controls, suspend/remove power sequencing, and PCM framing setup.

## State and persistence behavior
The header itself stores no state. Its register indices line up with `snd_at73c213_original_image` and the 18-byte `reg_image` cache in the driver.

## Dependencies and integration points
It is included only by the AT73C213 SPI driver and complements public platform data from `linux/spi/at73c213.h`.

## Risks and edge cases
Register numbers and bit positions are hardware ABI. Any mismatch corrupts mixer behavior or power sequencing. The header has no masks for multi-bit fields beyond shift positions, so callers must supply correct values.

## Test signals
Compile coverage plus runtime mixer and power-sequence tests are the practical validation signals. Comparing SPI transactions against the AT73C213 datasheet is useful for changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/spi/at73c213.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/Kconfig -->
# sources/distributed-fs/ceph-client/sound/synth/Kconfig

## Purpose
This Kconfig file declares the internal ALSA EMUX wavetable synthesizer support symbol.

## Important APIs, types, and functions
`config SND_SYNTH_EMUX` is a tristate symbol with no prompt in this file. It is selected or depended on by concrete drivers that need the shared EMU wavetable synthesizer layer.

## Control flow
There is no runtime flow. At configuration time, other Kconfig entries control whether this hidden symbol is enabled.

## State and persistence behavior
The only state is the generated kernel configuration value, which controls whether `sound/synth/emux` is built.

## Dependencies and integration points
It integrates the shared EMUX layer into Kconfig without making it a direct user-facing option.

## Risks and edge cases
Because the symbol has no prompt, build failures can occur if dependent drivers expect EMUX objects but fail to select the symbol. Direct user configuration is intentionally limited.

## Test signals
Kconfig tests should verify that EMUX-dependent drivers select or enable this symbol and that disabling all consumers omits the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/Makefile -->
# sources/distributed-fs/ceph-client/sound/synth/Makefile

## Purpose
This Kbuild file builds shared ALSA synthesizer support: utility memory management and the EMUX subdirectory.

## Important APIs, types, and functions
`snd-util-mem-y := util_mem.o` defines the shared memory helper module. `obj-$(CONFIG_SND_EMU10K1)`, `obj-$(CONFIG_SND_TRIDENT)`, and `obj-$(CONFIG_SND_SBAWE_SEQ)` add `snd-util-mem.o` for consumers. `obj-$(CONFIG_SND_SEQUENCER) += emux/` descends into the EMUX build when the ALSA sequencer is enabled.

## Control flow
There is no runtime flow. Kbuild emits helper objects and recurses into `emux/` based on configuration.

## State and persistence behavior
The file encodes static build dependencies only.

## Dependencies and integration points
It connects consumer sound drivers to `util_mem.o` and the EMUX layer. The EMUX subdirectory still gates its actual module on `CONFIG_SND_SYNTH_EMUX`.

## Risks and edge cases
Build skew is the main risk: new utility-memory consumers require another `obj-*` line, and EMUX source changes must stay coordinated with the subdirectory Makefile. Recursing into `emux/` when the sequencer is enabled does not by itself build EMUX unless `SND_SYNTH_EMUX` is set.

## Test signals
Build with EMU10K1, Trident, SBAWE, sequencer, and no-consumer combinations to confirm the expected objects and no duplicate or missing symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/Makefile -->
# sources/distributed-fs/ceph-client/sound/synth/emux/Makefile

## Purpose
This Kbuild file defines the `snd-emux-synth` module, the shared ALSA EMU wavetable synthesizer implementation.

## Important APIs, types, and functions
`snd-emux-synth-y` includes `emux.o`, `emux_synth.o`, `emux_seq.o`, `emux_nrpn.o`, `emux_effect.o`, `emux_hwdep.o`, and `soundfont.o`. `snd-emux-synth-$(CONFIG_SND_PROC_FS)` optionally adds `emux_proc.o`. A conditional adds `emux_oss.o` when `CONFIG_SND_SEQUENCER_OSS` is nonempty. `obj-$(CONFIG_SND_SYNTH_EMUX)` controls final linkage.

## Control flow
There is no runtime flow. Kbuild selects which support files contribute to the module based on procfs and OSS sequencer options.

## State and persistence behavior
Only static build graph state is encoded.

## Dependencies and integration points
It integrates the EMUX core, synth voice logic, sequencer interface, NRPN/SYSEX handling, raw effects, hwdep patch loading, soundfont logic, optional proc diagnostics, and optional OSS compatibility into one module.

## Risks and edge cases
Changing feature guards can create unresolved symbols because prototypes in `emux_voice.h` depend on `CONFIG_SND_PROC_FS`, `CONFIG_SND_SEQUENCER_OSS`, and `SNDRV_EMUX_USE_RAW_EFFECT`. `emux_oss.o` is included by a nonempty test rather than `obj-*`, so the exact Kconfig string behavior matters.

## Test signals
Build combinations with procfs on/off and OSS sequencer on/off should confirm the expected object set and symbol closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux.c

## Purpose
This file provides the lifecycle entry points for the shared EMUX wavetable synthesizer layer used by EMU8000/EMU10K1-style drivers. It allocates the core `snd_emux` object, registers soundfont/hwdep/sequencer/virtual-MIDI/proc interfaces, and tears them down.

## Important APIs, types, and functions
Exported APIs are `snd_emux_new`, `snd_emux_register`, and `snd_emux_free`. Soundfont callbacks `sf_sample_new`, `sf_sample_free`, and `sf_sample_reset` bridge the generic soundfont loader to hardware-specific `emu->ops` methods. `snd_emux_register` validates hardware and voice counts, duplicates the device name, allocates the voice array, creates `snd_sf_list`, initializes hwdep, voices, sequencer ports, optional OSS sequencer support, virtual MIDI, and proc entries.

## Control flow
Hardware drivers call `snd_emux_new`, fill `emu->hw`, `emu->ops`, `max_voices`, memory header, and port counts, then call `snd_emux_register`. Registration creates all user-facing interfaces in dependency order: soundfont list first, hwdep patch loading, voice initialization, ALSA sequencer client/ports, optional OSS facade, virtual raw MIDI, and proc diagnostics. `snd_emux_free` shuts down the pending note-off timer, removes proc/virmidi/OSS/sequencer/hwdep, frees soundfonts, voices, name, and the object.

## State and persistence behavior
State is in-memory only: locks, timer state, use counter, soundfont list, voice table, sequencer clients/ports, optional OSS and virmidi devices, and hardware operation callbacks. Loaded soundfonts and samples live in kernel memory or hardware memory through `memhdr`/hardware ops.

## Dependencies and integration points
The file integrates ALSA core, ALSA soundfont support, hwdep, sequencer, optional OSS sequencer, virtual raw MIDI, procfs, timers, and hardware-specific EMUX operation callbacks. It exports symbols for lower-level sound card drivers.

## Risks and edge cases
Several registration failure paths return directly without unwinding previously allocated pieces, relying on caller cleanup or leaking until free is invoked. Hardware ops must be complete before registration; missing sample callbacks or invalid `max_voices` fail or crash later. `snd_emux_init_seq` return is not checked, so later interfaces may initialize with no valid client if sequencer creation fails.

## Test signals
Test signals include successful registration by an EMUX consumer, hwdep node creation, sequencer ports, virmidi devices when configured, proc entry, soundfont load/reset/free callbacks, and clean `snd_emux_free` after partial registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_effect.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_effect.c

## Purpose
This file implements optional raw EMUX effect handling when `SNDRV_EMUX_USE_RAW_EFFECT` is enabled. It maps AWE/EMUX effect slots to soundfont voice parameter fields, stores per-channel effect overrides, applies them to new voices, and updates selected parameters on currently playing voices.

## Important APIs, types, and functions
`parm_defs` maps each effect type to byte/word layout, limits, soundfont parameter offset, and real-time update mask. `effect_set_byte`, `effect_set_word`, and `effect_get_offset` apply set/add/off effect semantics and sample/loop offsets. Public functions include `snd_emux_send_effect`, optional `snd_emux_send_effect_oss`, `snd_emux_setup_effect`, `snd_emux_create_effect`, `snd_emux_delete_effect`, and `snd_emux_clear_effect`.

## Control flow
Each EMUX port gets an effect table per MIDI channel. Incoming effect commands store value and mode in `chan->private`. If the effect has a real-time update mask and a valid parameter offset, `snd_emux_send_effect` walks active voices for that channel under `voice_lock`, restores the original zone parameter byte/word, applies the effect value, then calls `snd_emux_update_channel`. When a new voice is prepared, `snd_emux_setup_effect` applies all active channel effects and adjusts start/loop offsets before the hardware voice is triggered.

## State and persistence behavior
Effect state persists per port/channel in `struct snd_emux_effect_table` until reset/clear/delete. It is not written to disk. Per-voice register copies are modified from the original zone data; soundfont zone data remains the baseline.

## Dependencies and integration points
It depends on `soundfont_voice_parm`, MIDI channel private storage, EMUX update masks, and the synth voice setup path. OSS compatibility can translate OSS effect encodings into the same raw effect API.

## Risks and edge cases
The code is compiled only under a feature macro, so call sites must remain guard-aligned. In `snd_emux_send_effect`, the real-time loop checks `parm_defs[i].type` instead of `parm_defs[type].type`, which is suspicious because `i` is a voice index, not an effect type. Endianness-sensitive byte offsets must match soundfont parameter layout. Sample and loop offset effects can push addresses outside intended sample ranges if not constrained elsewhere.

## Test signals
Exercise AWE/OSS raw effects, real-time cutoff/Q/LFO/pitch updates on sustained notes, new note setup with active effects, sample-start and loop offset effects, port reset clearing effects, and builds with the raw-effect macro disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_effect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_hwdep.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_hwdep.c

## Purpose
This file exposes the EMUX wavetable hwdep interface used by user space to load soundfont/GUS patches, reset or remove samples, query memory, and set miscellaneous per-port modes.

## Important APIs, types, and functions
`snd_emux_hwdep_load_patch` copies a `soundfont_patch_info` header from user space and dispatches to GUS patch loading, generic soundfont loading, or hardware-specific `emu->ops.load_fx`. `snd_emux_hwdep_misc_mode` updates control values for all ports or one selected port with nospec-index hardening. `snd_emux_hwdep_ioctl` handles `SNDRV_EMUX_IOCTL_VERSION`, `LOAD_PATCH`, `RESET_SAMPLES`, `REMOVE_LAST_SAMPLES`, `MEM_AVAIL`, and `MISC_MODE`. Exported setup/teardown are `snd_emux_init_hwdep` and `snd_emux_delete_hwdep`.

## Control flow
Registration creates an ALSA hwdep device named `SNDRV_EMUX_HWDEP_NAME`, assigns EMUX wavetable iface, installs ioctl and compat ioctl handlers, marks the device exclusive, stores `emu` as private data, and registers the card. Ioctls are synchronous; patch loading passes the original user pointer and length to soundfont helpers after a header copy.

## State and persistence behavior
No disk state is stored. Ioctls mutate the soundfont list, hardware sample memory through callbacks, and per-port `ctrls` values. `TMP_CLIENT_ID` tags hwdep-loaded soundfont data.

## Dependencies and integration points
This file integrates ALSA hwdep, soundfont loader, util memory reporting, hardware-specific EMUX ops, user-copy APIs, and `array_index_nospec`.

## Risks and edge cases
Patch lengths come from user-supplied headers and must remain validated by downstream loaders. Unknown ioctl commands return success with no action, which may hide user-space mistakes. `snd_emux_init_hwdep` calls `snd_card_register`, so registration ordering with the parent card is important. Misc mode updates do not lock `register_mutex`, so concurrent port teardown must be considered.

## Test signals
Test hwdep open exclusivity, version ioctl, valid and invalid soundfont/GUS patch loading, sample reset/removal, memory availability queries with and without `memhdr`, misc mode for all ports and one port, 32-bit compat ioctl, and invalid user pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_nrpn.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_nrpn.c

## Purpose
This file converts MIDI NRPN, XG controller, and SYSEX events into EMUX raw effect or port update operations. It provides AWE32-specific NRPN effects, experimental GS and XG mappings, and SYSEX master-volume handling.

## Important APIs, types, and functions
`struct nrpn_conv_table` maps a MIDI control number to an EMUX effect and conversion callback. Conversion helpers such as `fx_delay`, `fx_attack`, `fx_decay`, `fx_conv_pitch`, `gs_cutoff`, and `xg_filterQ` translate MIDI values into soundfont/EMUX units. Public functions are `snd_emux_nrpn`, `snd_emux_xg_control`, and `snd_emux_sysex`.

## Control flow
For AWE32 NRPNs, `snd_emux_nrpn` matches MSB 127 and LSB 0-26, combines data-entry MSB/LSB into a signed value centered at 8192, and sends a set-mode raw effect. In GS mode with NRPN MSB 1, it uses only data-entry MSB and sends add-mode GS effects. XG controller handling is invoked from `snd_emux_control` and maps controller 71/72/73/74 to cutoff, release, attack, and resonance effects. SYSEX master volume triggers a port volume update; unknown parsed SYSEX events are delegated to hardware `emu->ops.sysex` when present.

## State and persistence behavior
This file owns no persistent storage. It mutates per-channel effect state through `snd_emux_send_effect` and causes live voice updates through the synth layer.

## Dependencies and integration points
It depends on ALSA MIDI parser constants, EMUX raw effect APIs, soundfont parameter calculators, MIDI channel control arrays, and optional hardware SYSEX callbacks.

## Risks and edge cases
The conversion tables are described as experimental for GS/XG and use fixed sensitivity arrays tuned for particular soundfonts. `snd_emux_xg_control` validates only upper bound against `ARRAY_SIZE(chan->control)`; negative params are not expected but would be unsafe if passed. Raw effect support must be present for conversion outputs to have effect.

## Test signals
Send AWE32 NRPNs for every table entry, GS NRPNs in GS mode, XG controllers in XG mode, master-volume SYSEX, unknown SYSEX delegation, and boundary values 0/64/127 to verify conversion signs and magnitudes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_nrpn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_oss.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_oss.c

## Purpose
This file implements OSS sequencer compatibility for the EMUX wavetable synth. It registers an OSS synth device, creates per-open EMUX ports, supports OSS patch loading/ioctls, and translates OSS private/AWE/GUS control events into EMUX MIDI or raw effect operations.

## Important APIs, types, and functions
`snd_emux_init_seq_oss` and `snd_emux_detach_seq_oss` manage the OSS sequencer device. The `oss_callback` table points to open, close, ioctl, patch load, and reset handlers. `snd_emux_open_seq_oss` creates an OSS port and increments module/card use counts; `snd_emux_close_seq_oss` silences and detaches it. `emuspec_control`, `gusspec_control`, and `fake_event` implement private event translation.

## Control flow
Initialization creates a `SNDRV_SEQ_DEV_ID_OSS` device using device number 1 to avoid OPL3 conflicts, marks it as sample/AWE32 compatible, and registers callbacks. On OSS open, the driver creates a writable sequencer port with 32 channels, stores OSS arguments, sets MIDI or synth mode, and resets the port. Raw OSS events with `SEQ_PRIVATE` are parsed: EMUX-specific commands update effects, terminate voices, switch port mode, change drum flags, or call hardware `oss_ioctl`; GUS commands update sample, pan, or sample-start effects. Close stops all sounds, releases soundfont client locks, detaches the port, and decrements module usage.

## State and persistence behavior
State persists per OSS open in a dynamically created `snd_emux_port`, its channel set, drum flags, volume attenuation, and associated soundfont client number. Patch loads mutate the shared EMUX soundfont list. No disk persistence exists.

## Dependencies and integration points
It integrates ALSA OSS sequencer emulation, EMUX sequencer/event APIs, soundfont loaders, Linux ultrasound compatibility constants, MIDI control constants, and optional raw effect support.

## Risks and edge cases
Private event parsing uses unaligned casts from raw byte data to short/int values, which can be architecture-sensitive. Many OSS commands are unsupported no-ops. Port creation failure must correctly unwind module counts. Soundfont client numbers are derived from port numbers and must avoid collisions. Mode switching resets the port and may interrupt active notes.

## Test signals
Test OSS synth registration, open/close cycles, patch loading in GUS and soundfont formats, reset/ioctl memory queries, AWE private effect events, terminate/release commands, MIDI versus synth mode transitions, GUS sample/pan/position commands, and builds without OSS sequencer support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_proc.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_proc.c

## Purpose
This file provides a `/proc/asound` text diagnostics entry for EMUX wavetable synthesizers when ALSA procfs support is enabled.

## Important APIs, types, and functions
`snd_emux_proc_info_read` prints device name, sequencer ports, use count, max and allocated voices, memory size/availability/block count, and soundfont/instrument/sample lock counters. `snd_emux_proc_init` creates `wavetableD<device>` under the card proc root. `snd_emux_proc_free` removes it.

## Control flow
Registration calls `snd_emux_proc_init`, which creates a card entry and attaches the read callback. Reads take `emu->register_mutex`, then `emu->sflist->presets_mutex` while printing soundfont counters. Teardown frees the entry and clears `emu->proc`.

## State and persistence behavior
The proc entry stores only a pointer to `emu`; it exposes live in-memory counters and does not persist settings.

## Dependencies and integration points
It depends on ALSA info/proc APIs, EMUX core state, util memory headers, and soundfont list internals. `emux_voice.h` supplies inline no-op replacements when procfs is disabled.

## Risks and edge cases
Read-side locking must stay consistent with sequencer and soundfont mutation paths to avoid stale pointers. The optional debug block is disabled but references voice internals useful during troubleshooting. Entry creation failure is silently ignored.

## Test signals
Verify `wavetableD*` appears when procfs is enabled, prints correct port and memory counters after soundfont loads/unloads, handles no `memhdr` or no `sflist`, and disappears after EMUX free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_seq.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_seq.c

## Purpose
This file implements the ALSA sequencer and virtual-MIDI interface for the EMUX synth. It creates kernel sequencer clients and ports, processes MIDI events through ALSA MIDI emulation callbacks, manages port reset/use counts, and attaches optional virtual raw MIDI devices.

## Important APIs, types, and functions
`emux_ops` maps MIDI note/control/NRPN/SYSEX callbacks to EMUX synth functions. `snd_emux_init_seq` creates the kernel client and configured MIDI ports. `snd_emux_create_port` allocates an EMUX port and channel set, optionally creates raw effect tables, and attaches a sequencer port. `snd_emux_reset_port`, `snd_emux_event_input`, `snd_emux_inc_count`, `snd_emux_dec_count`, `snd_emux_init_virmidi`, and `snd_emux_delete_virmidi` form the public control surface.

## Control flow
Initialization creates a kernel sequencer client named after the device, clamps `num_ports` to valid limits, builds callbacks, and attaches one 16-channel port per configured port. Each non-OSS port is writable/subscribable and advertises MIDI GM/GS/XG hardware synth types. On first subscription, `snd_emux_use` resets the port and increments hardware/card module refs; on unuse it silences the port and decrements refs. Incoming sequencer events are passed to `snd_midi_process_event`, which invokes `emux_ops`. Virmidi initialization creates rawmidi devices and points them at sequencer ports.

## State and persistence behavior
State persists in `emu->client`, `emu->ports`, `emu->portptrs`, `emu->used`, port channel sets, per-port controls, drum flags, optional effect tables, and virtual rawmidi pointers. No disk persistence exists. When usage count drops to zero, all voices are terminated.

## Dependencies and integration points
This file integrates ALSA sequencer kernel clients, MIDI event parsing, virmidi, module reference counting, EMUX synth voice callbacks, optional raw effects, and OSS-created ports.

## Risks and edge cases
`snd_emux_create_port` does not free the allocated port if `snd_seq_event_port_attach` fails and returns a negative port id. Registration callers do not always check `snd_emux_init_seq` failures. Module reference handling must remain balanced across use/unuse and OSS open/close. Virmidi port indexing assumes `midi_ports` does not exceed created sequencer ports.

## Test signals
Test sequencer client creation, port counts and caps, subscription use/unuse, MIDI note/control routing, port reset drum flags, module ref behavior, virmidi creation/deletion, failure injection for port attach and rawmidi registration, and teardown terminating active voices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_synth.c -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_synth.c

## Purpose
This file is the main EMUX MIDI synthesis engine. It maps MIDI notes to soundfont zones, allocates and prepares hardware voices, handles note-off/key-pressure/controller updates, calculates pitch/volume/pan parameters, terminates voices, and initializes/locks voice records.

## Important APIs, types, and functions
Public callbacks include `snd_emux_note_on`, `snd_emux_note_off`, `snd_emux_key_press`, `snd_emux_update_channel`, `snd_emux_update_port`, `snd_emux_control`, `snd_emux_terminate_note`, `snd_emux_terminate_all`, `snd_emux_sounds_off_all`, `snd_emux_init_voices`, `snd_emux_lock_voice`, and `snd_emux_unlock_voice`. Internal helpers include `get_zone`, `get_bank`, `exclusive_note_off`, `terminate_voice`, `update_voice`, `setup_voice`, `calc_pan`, `calc_volume`, and `calc_pitch`.

## Control flow
Note-on resolves the active bank/preset, searches soundfont zones for note/velocity, applies exclusive-class note-off for drums, allocates one hardware voice per matching zone through `emu->ops.get_voice`, fills voice fields, copies and computes register state, optionally lets hardware prepare, then triggers all standby voices for that MIDI channel. Note-off marks matching voices released; if note-on and note-off occur in the same jiffy, release is deferred by a timer to avoid hardware artifacts. Key pressure and MIDI controls recalculate live voice volume, pitch, pan, or modulation and call hardware update callbacks.

Termination functions walk the voice table under `voice_lock`, call hardware terminate/free/reset callbacks, and clear voice ownership. `setup_voice` copies the soundfont zone, applies raw effects, computes current attenuation, pitch, pan/aux, filter target, pitch target, and volume target. Bank selection follows XG, GS, and default/drum conventions. Voice initialization marks all voices off and binds them to `emu` and hardware.

## State and persistence behavior
Voice state is held in `emu->voices`: state, time ordering, MIDI channel, port, key/note/velocity, soundfont zone/sample block, copied register set, computed attenuation/pitch/pan/filter targets, and hardware identifiers. The global `use_time` counter drives allocation age and termination ordering. A timer persists pending same-jiffy note releases. No disk persistence exists.

## Dependencies and integration points
The engine depends on ALSA MIDI channel state, soundfont zone search and volume tables, EMUX hardware operation callbacks, raw effects, jiffies/timers, and sequencer event routing from `emux_seq.c`. Hardware drivers provide voice allocation, prepare, trigger, release, terminate, update, free/reset, and optional pitch shift.

## Risks and edge cases
Hardware callbacks are invoked under `voice_lock` in many paths, so callback locking must not recurse or sleep unexpectedly. Same-jiffy note-off deferral prevents one artifact but adds timer ordering complexity. `snd_emux_update_channel` updates all voices with a matching channel pointer regardless of state before `update_voice` filters. Soundfont zones without samples produce voices with null blocks and depend on hardware prepare handling. Volume/pitch calculations use many lookup tables and clamps; regressions are audible rather than compile-visible.

## Test signals
Test note-on/off for melodic and drum banks, multi-zone layered presets, exclusive drum classes, immediate note-off deferral, pitchbend/RPN tuning, pan modes, expression/master volume, key pressure, all-notes/sounds-off, voice lock/unlock, hardware callback ordering, and stress with max voices exhausted.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_voice.h -->
# sources/distributed-fs/ceph-client/sound/synth/emux/emux_voice.h

## Purpose
This private EMUX header centralizes cross-file prototypes for sequencer, synth voice, raw effects, NRPN/SYSEX, OSS, proc, and hwdep support. It is the internal contract between EMUX implementation files.

## Important APIs, types, and functions
The header declares sequencer functions such as `snd_emux_init_seq`, `snd_emux_create_port`, `snd_emux_event_input`, and virmidi helpers; synth functions such as note on/off, control, update, timer, and sound-off helpers; raw effect functions under `SNDRV_EMUX_USE_RAW_EFFECT`; NRPN/SYSEX functions; OSS attach/detach; proc functions or no-op inlines depending on `CONFIG_SND_PROC_FS`; and hwdep setup/teardown. `STATE_IS_PLAYING` abstracts the voice state test against `SNDRV_EMUX_ST_ON`.

## Control flow
There is no executable flow beyond the proc no-op inline definitions. The declarations define how `emux.c` sequences registration and teardown and how `emux_seq.c` routes MIDI events into `emux_synth.c`, `emux_nrpn.c`, and optional effect/OSS/proc layers.

## State and persistence behavior
The header stores no state. It exposes functions that mutate EMUX in-memory voice, port, soundfont, hwdep, and proc state.

## Dependencies and integration points
It includes Linux wait/sched and ALSA core/EMUX synth public headers. It connects all objects listed in the EMUX Makefile and encodes feature guards for raw effects and procfs.

## Risks and edge cases
Prototype guards must match object inclusion in the Makefile. If `SNDRV_EMUX_USE_RAW_EFFECT`, `CONFIG_SND_PROC_FS`, or OSS build options drift from call sites, builds can fail or no-op unexpectedly. `STATE_IS_PLAYING` treats any state bit overlapping `SNDRV_EMUX_ST_ON` as playing, so state bit definitions must remain compatible.

## Test signals
Compile every EMUX configuration combination, especially procfs on/off, OSS on/off, and raw effects on/off. Runtime signals include successful registration and teardown paths that call the declared interfaces in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/synth/emux/emux_voice.h -->
