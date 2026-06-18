# Group Research: subset-b-006388

This grouped report covers the ALSA PCI driver sources assigned to `subset-b-006388`. Each source file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/azt3328.c -->
# sources/distributed-fs/ceph-client/sound/pci/azt3328.c

## Purpose

`azt3328.c` is the ALSA PCI driver for Aztech AZF3328 / PCI168 sound cards. The hardware is largely undocumented, so the driver encodes reverse-engineered behavior for PCI I/O BARs, three PCM-like codecs, a nonstandard AC97-like mixer, MPU401 UART MIDI, genuine OPL3, a gameport, and a 1 MHz-ish DirectX timer exposed through ALSA timer support. It registers a PCI driver for vendor/device pairs `0x122d:0x50dc` and `0x122d:0x80da`.

## Important APIs, Types, and Functions

Core state is held in `struct snd_azf3328`, which owns PCI BAR I/O bases, `reg_lock`, ALSA card, PCM devices, optional AC97 codec, raw MIDI, optional gameport, timer, IRQ number, a write-only shadow for control register `0x6a`, and PM register snapshots. Per-engine runtime state is held in `struct snd_azf3328_codec_data`, one each for playback, capture, and I2S out.

Low-level helpers wrap port I/O: `snd_azf3328_codec_in/out{b,w,l}`, `snd_azf3328_ctrl_in/out{b,w,l}`, gameport helpers, and mixer helpers. `snd_azf3328_io_reg_setb()` performs read-modify-write bit updates for byte registers.

Mixer support is compiled through `AZF_USE_AC97_LAYER`. In the active path, `snd_azf3328_mixer_ac97_map_reg_idx()`, `snd_azf3328_mixer_ac97_read()`, and `snd_azf3328_mixer_ac97_write()` emulate enough AC97 behavior to let ALSA's AC97 layer drive a shifted, noncompliant hardware mixer map. The disabled legacy path defines explicit ALSA mixer controls.

PCM functionality is implemented through `snd_azf3328_pcm_open()`, `snd_azf3328_pcm_prepare()`, `snd_azf3328_pcm_trigger()`, `snd_azf3328_pcm_pointer()`, and per-stream `snd_pcm_ops`. `snd_azf3328_codec_setfmt()` programs rate, width, and channel count. `snd_azf3328_codec_setdmaa()` programs the two-buffer DMA scheme.

Device setup flows through `snd_azf3328_create()`, `__snd_azf3328_probe()`, and `snd_azf3328_probe()`. Interrupts are handled by `snd_azf3328_interrupt()` with fanout to `snd_azf3328_pcm_interrupt()`, timer handling, gameport handling, and MPU401 IRQ handling.

## Control Flow

Probe allocates an ALSA card, enables the PCI device, restricts DMA to 24 bits, requests all PCI regions, maps five I/O BAR bases, initializes three codec descriptors, requests a shared IRQ, sets bus mastering, initializes the mixer, shuts codecs into low-power state, registers MPU401, timer, PCM devices, optional OPL3 timer/hwdep, optional gameport, and finally registers the card.

Playback/capture open binds the ALSA substream to a codec descriptor and applies shared hardware constraints. Prepare mainly records the DMA base. On `START`, trigger mutes PCM playback when appropriate, programs format, stops/resets DMA flags, clears codec IRQ state, writes the two DMA buffer start/length registers, starts DMA with a hardware-specific flag sequence, marks the codec active, and restores mute state. On `STOP`, it clears `DMA_RESUME`, toggles a run bit, marks activity off, and may lower the codec format to reduce power/noise.

The IRQ handler first filters shared interrupts using `IDX_IO_IRQSTATUS`. Timer IRQs call `snd_timer_interrupt()` and acknowledge by writing control byte `0x07`; PCM IRQs read and acknowledge codec-local `IDX_IO_CODEC_IRQTYPE` then call `snd_pcm_period_elapsed()` for attached substreams; MPU401 IRQs delegate to `snd_mpu401_uart_interrupt()`.

Suspend saves selected 32-bit I/O ranges, explicitly patches the write-only `0x6a` shadow into saved control state, suspends AC97 or mixer registers, and powers down. Resume restores game/MPU/OPL3/mixer/control register blocks and returns the card to D0.

## State and Persistence Behavior

Persistent runtime state is mostly hardware register state mirrored in `struct snd_azf3328`. `codec->running` prevents global codec power-disable while sibling codecs are active. `shadow_reg_ctrl_6AH` is essential because register `0x6a` is write-only. AC97 state is delegated to ALSA's AC97 cache when enabled. PM snapshots persist selected control/game/MPU/OPL3/mixer register ranges across suspend.

DMA state is not descriptor-list based. The hardware expects exactly two DMA regions, so ALSA constraints force `periods_min = periods_max = 2`, and `snd_azf3328_codec_setdmaa()` writes two buffer starts plus a packed length word.

## Dependencies and Integration Points

The file integrates with ALSA core, PCM, AC97, rawmidi/MPU401, OPL3, timer, and optional Linux gameport APIs. It depends on `azt3328.h` for register offsets, bit definitions, mixer IDs, rate encoding, and I/O range sizes. It uses PCI managed resource helpers, device-managed IRQs, and simple PM ops.

External user-visible surfaces are ALSA PCM devices `AZF3328 DSP` and `AZF3328 I2S OUT`, AC97 mixer controls, an ALSA timer named `AZF3328 timer`, MPU401 rawmidi, OPL3 hwdep/timers, and optionally a gameport.

## Risks and Edge Cases

Much of the hardware programming is reverse-engineered and annotated as uncertain. The mixer is AC97-like but not AC97-compliant, so register mapping and emulated reads may drift from ALSA AC97 expectations. PCM locking is explicitly called out as not entirely clean, and format changes use undocumented DMA flag tweaking to avoid clicks. The timer can cause interrupt storms if configured too aggressively, so `seqtimer_scaling` and a minimum delay guard are safety-critical. DMA is limited to 24-bit addressing. Suspend/resume restores only selected register ranges, matching observed Windows behavior but risking missed undocumented state.

## Test Signals

Useful validation signals include successful PCI probe and ALSA card registration, PCM playback/capture at all fixed rates including unusual `KNOT` rates, full-duplex playback/capture, period interrupts without underruns, AC97 mixer controls muting/unmuting correctly, OPL3 MIDI playback, MPU401 raw MIDI I/O, ALSA timer operation without IRQ storms, gameport cooked reads, and suspend/resume preserving mixer, codec, MIDI, timer, and gameport behavior. Kernel logs should be checked for AC97 unsupported-register warnings, unknown IRQ type messages, and DMA crackling/underrun reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/azt3328.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/azt3328.h -->
# sources/distributed-fs/ceph-client/sound/pci/azt3328.h

## Purpose

`azt3328.h` is the register and bit-definition contract for the AZF3328 ALSA driver. It documents the reverse-engineered I/O layout for the card's control, gameport, MPU401, OPL3, and mixer regions, plus helper constants used by `azt3328.c` for DMA, IRQ handling, sound format selection, timer programming, gameport control, AC97-like mixer emulation, and suspend/resume sizing.

## Important APIs, Types, and Definitions

The header defines I/O region sizes such as `AZF_IO_SIZE_CTRL`, `AZF_IO_SIZE_GAME`, `AZF_IO_SIZE_MPU`, `AZF_IO_SIZE_OPL3`, and `AZF_IO_SIZE_MIXER`, along with smaller PM save ranges. Codec subregions are declared with `AZF_IO_OFFS_CODEC_PLAYBACK`, `AZF_IO_OFFS_CODEC_CAPTURE`, and `AZF_IO_OFFS_CODEC_I2S_OUT`.

Codec DMA and IRQ registers include `IDX_IO_CODEC_DMA_FLAGS`, `IDX_IO_CODEC_IRQTYPE`, start/length/current-position registers, and `IDX_IO_CODEC_SOUNDFORMAT`. Bit fields such as `DMA_RESUME`, `DMA_RUN_SOMETHING1`, `DMA_RUN_SOMETHING2`, `IRQ_FINISHED_DMABUF_1`, `IRQ_FINISHED_DMABUF_2`, and `SOUNDFORMAT_FLAG_16BIT/2CHANNELS` are consumed by PCM setup and interrupt handling.

`enum azf_freq_t` enumerates supported sample-rate values as actual rate numbers. Frequency selectors such as `SOUNDFORMAT_FREQ_44100`, `SOUNDFORMAT_FREQ_48000`, and several suspected low/high rates map requested ALSA rates into hardware nibbles.

Global control definitions cover the DirectX timer (`IDX_IO_TIMER_VALUE`, `TIMER_VALUE_MASK`, enable/ack bits), IRQ status (`IRQ_PLAYBACK`, `IRQ_RECORDING`, `IRQ_I2S_OUT`, `IRQ_GAMEPORT`, `IRQ_MPU401`, `IRQ_TIMER`), and write-only/unknown control registers around `0x6a`.

Gameport definitions describe legacy port support, axis config, ADC latch/read bits, IRQ enable, and ADC counter-frequency selectors. Mixer definitions list nonstandard AC97-like register offsets and masks for master, PCM, record select, advanced controls, bass/treble, 3D, mute, and volume fields. `AZF_ALIGN()` rounds PM save ranges for 32-bit register snapshots.

## Control Flow Role

This header has no executable control flow, but it shapes all major driver paths. Probe uses region size constants and codec offsets. PCM trigger uses codec DMA/IRQ/format bits. Timer start/stop uses timer masks. Gameport open/read/close uses axis and hardware config bits. Mixer initialization and AC97 emulation translate AC97 indices onto the mixer offsets declared here. Suspend/resume uses PM save-size constants and `AZF_ALIGN()`.

## State and Persistence Behavior

The file identifies which register ranges are saved for power management and which registers are write-only or unreliable. It explicitly marks `IDX_IO_6AH` as write-only, which explains why the implementation maintains `shadow_reg_ctrl_6AH`. The constants also encode hardware limitations, especially the two-region DMA model and the fixed mixer register layout.

## Dependencies and Integration Points

`azt3328.h` is tightly coupled to `azt3328.c` and indirectly to ALSA subsystems that consume the driver's PCM, mixer, timer, MIDI, OPL3, and gameport features. It does not include Linux or ALSA headers itself, keeping it as a pure macro/enum register map.

## Risks and Edge Cases

Many constants are documented as suspected, unknown, unmodifiable, or observed from Windows driver behavior rather than vendor documentation. Incorrect bits can disable playback, cause crackling, break gameport legacy I/O, or misrepresent AC97 capabilities. The AC97 mixer layout intentionally violates standard AC97 offsets, which makes this header's mapping central to correctness.

## Test Signals

The strongest test signals are runtime driver behavior: correct sample rates from all `enum azf_freq_t` choices, period interrupts matching DMA buffer halves, DirectX timer countdown/ack behavior, working mixer controls at the declared offsets, gameport axis/button reads, and suspend/resume preserving only the declared PM ranges without losing audio, MIDI, OPL3, or gameport state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/azt3328.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/bt87x.c -->
# sources/distributed-fs/ceph-client/sound/pci/bt87x.c

## Purpose

`bt87x.c` is an ALSA capture driver for Brooktree Bt878/Bt879 audio functions, commonly found on TV/video capture cards. It exposes analog and/or digital capture PCM devices depending on board metadata, creates a Bt87x RISC DMA program for scatter-gather audio capture, manages capture input controls for analog boards, and filters unsupported DVB/no-audio boards unless `load_all` is requested.

## Important APIs, Types, and Functions

`struct snd_bt87x` stores card, PCI device, MMIO base, IRQ, spinlock, single-open state, active substream, allocated RISC DMA buffer, current period geometry, cached audio control register, interrupt mask, current line/period, and parity error count.

Board behavior is described by `struct snd_bt87x_board`, with digital sample rate, digital format bits, and analog/digital disable flags. Static board tables cover known Hauppauge, Osprey, ATI, Leadtek, Pinnacle, AVerMedia, and related devices, while a denylist blocks known DVB/no-audio cards.

Key functions include `snd_bt87x_create_risc()` for building the hardware RISC instruction loop, `snd_bt87x_interrupt()` for error and period IRQ handling, `snd_bt87x_pcm_open()/close()`, `snd_bt87x_hw_params()/hw_free()`, `snd_bt87x_prepare()`, `snd_bt87x_start()/stop()`, and `snd_bt87x_pointer()`. Mixer-like capture controls are implemented through capture volume, boost, and source get/put callbacks.

Probe flows through `snd_bt87x_detect_card()`, `snd_bt87x_create()`, `__snd_bt87x_probe()`, and `snd_bt87x_probe()`. Module init optionally swaps the PCI ID table to default catch-all Bt878/Bt879 IDs when `load_all` is set.

## Control Flow

Initialization registers a PCI driver. Probe detects board identity using explicit PCI subsystem matches or the denylist. It allocates an ALSA card, maps BAR0 MMIO, initializes `REG_GPIO_DMA_CTL`, disables/clears interrupts, requests a shared IRQ, enables bus mastering, copies board configuration, creates digital and/or analog PCM capture devices, adds analog capture controls if analog is present, names the card, and registers it.

PCM open is exclusive via `test_and_set_bit()` on `chip->opened`. Digital open fixes rate to the board's digital rate and powers down analog input; analog open configures rational-rate constraints using the 1.792 MHz analog clock divider. HW params allocate/build the RISC program, splitting each period across page boundaries as needed. Prepare programs decimation and 8-bit rounding for analog capture formats.

Start writes the RISC program address, packet length, interrupt mask, and enables FIFO/RISC/audio capture. The RISC program raises `RISC_IRQ` at each period end and uses status bits to identify progress. The interrupt handler acknowledges masked status, logs FIFO and PCI/RISC errors, updates `current_line`, compensates for skipped interrupts by comparing status block bits, and calls `snd_pcm_period_elapsed()`.

## State and Persistence Behavior

Runtime state is volatile and hardware-backed. `reg_control` caches `REG_GPIO_DMA_CTL` so controls and stream state can safely update bit fields. `interrupt_mask` may be modified if repeated parity errors force parity interrupt disable. `current_line`, `line_bytes`, and `lines` track the DMA period position. The RISC DMA buffer is allocated lazily and freed on `hw_free`. There is no suspend/resume implementation in this file.

## Dependencies and Integration Points

The driver integrates with ALSA core, PCM, control APIs, PCI, Linux interrupt handling, MMIO accessors, scatter-gather PCM helpers, and PCI status error helpers. It uses `snd_pcm_set_managed_buffer_all()` with `SNDRV_DMA_TYPE_DEV_SG` for capture buffers and manual `snd_dma_alloc_pages()` for the RISC program.

## Risks and Edge Cases

The driver supports only one open capture stream at a time even if both analog and digital devices exist. Unknown cards default to guessed 32 kHz digital behavior unless blocked or configured. RISC program sizing assumes documented period and page-boundary limits. PCI parity errors can be observed from other bus devices; the driver disables parity-related interrupts after too many events. Analog sample rates depend on divider constraints and optional overclock configuration.

## Test Signals

Test with known board IDs and with unknown/denylisted cards. Validate analog capture at allowed rational rates and formats, digital capture at board or `digital_rate` fixed rates, exclusive-open enforcement, RISC DMA across page boundaries, period interrupt cadence, pointer monotonicity, capture volume/boost/source controls, FIFO overrun logging under stress, and parity error throttling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/bt87x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/Makefile

## Purpose

This Makefile defines how the ALSA CA0106 driver module is built. It composes the `snd-ca0106` object from the main driver, mixer support, shared Creative MIDI helper code, and optional procfs diagnostics.

## Important Build Rules

`snd-ca0106-y := ca0106_main.o ca0106_mixer.o ca_midi.o` makes the base module include PCI/PCM/IRQ/init logic, mixer/control logic, and the shared `ca_midi` implementation. `snd-ca0106-$(CONFIG_SND_PROC_FS) += ca0106_proc.o` conditionally includes diagnostic procfs support only when ALSA procfs is enabled. `obj-$(CONFIG_SND_CA0106) += snd-ca0106.o` builds the module when the CA0106 Kconfig option is selected.

## Control Flow Role

The Makefile has no runtime control flow, but it determines which C translation units are linked into the module. `ca0106_main.c` calls `snd_ca0106_mixer()` unconditionally, so `ca0106_mixer.o` is required. It calls `snd_ca0106_proc_init()` only under `CONFIG_SND_PROC_FS`, matching the conditional object rule. MIDI setup in `ca0106_main.c` depends on `ca_midi.o`.

## State and Persistence Behavior

There is no runtime state. Build state depends on kernel configuration symbols. The main risk is configuration mismatch: proc init symbols must be present exactly when `CONFIG_SND_PROC_FS` enables the call site, and the shared MIDI object must remain available to satisfy `ca_midi_init()`.

## Dependencies and Integration Points

This file integrates the CA0106 subdirectory with the kernel build system. It depends on `CONFIG_SND_CA0106` and `CONFIG_SND_PROC_FS`, and it shares `ca_midi.o` with nearby Creative ALSA drivers.

## Risks and Edge Cases

Removing `ca_midi.o` would break MIDI symbol resolution. Making `ca0106_proc.o` unconditional would add procfs dependencies to non-proc builds; making it absent when procfs is enabled would break `snd_ca0106_proc_init()`. Object ordering is simple and should not affect behavior because normal kernel module linking resolves symbols across all listed objects.

## Test Signals

Build with `CONFIG_SND_CA0106=m/y` and `CONFIG_SND_PROC_FS=y` to verify all four CA0106-specific objects plus `ca_midi.o` link. Build with procfs disabled to verify `ca0106_proc.o` is omitted and no unresolved proc symbol remains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106.h -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106.h

## Purpose

`ca0106.h` is the shared hardware contract for the Creative CA0106 ALSA driver. It defines PCI BAR registers, pointer-indexed register numbers, interrupt bits, playback/capture DMA registers, SPDIF status and routing fields, I2C ADC controls, SPI DAC controls, MIDI constants, logical channel mappings, and the core driver data structures used by `ca0106_main.c`, `ca0106_mixer.c`, and `ca0106_proc.c`.

## Important APIs, Types, and Definitions

Top-level PCI function registers include `CA0106_PTR`, `CA0106_DATA`, `CA0106_IPR`, `CA0106_INTE`, `CA0106_HCFG`, `CA0106_GPIO`, and AC97 address/data registers. Interrupt masks cover MIDI, SPDIF user/frame events, SPI/I2C completion, audio interrupt status, GPIO, SRC lock, timers, and PCI errors.

Pointer-indexed audio registers include playback period-list registers (`PLAYBACK_LIST_ADDR`, `PLAYBACK_LIST_SIZE`, `PLAYBACK_LIST_PTR`), playback/capture DMA address, size, pointer, FIFO offset, `BASIC_INTERRUPT`, SPDIF channel status registers `SPCS0` through `SPCS3`, routing registers, capture source/volume registers, extended interrupt mask/status registers, counters, SPI, and I2C registers.

SPDIF definitions encode IEC958 channel status fields, sample rates, word lengths, copyright, professional/consumer mode, and routing masks. I2C definitions describe the WM8775-like ADC transaction format and ADC registers such as attenuation, power, master mode, and mux selection. SPI definitions describe WM8768-like DAC register packing, attenuation, format, mute, phase, and power-down bits.

Core types are `struct snd_ca0106_channel`, `struct snd_ca0106_pcm`, `struct snd_ca0106_details`, and `struct snd_ca0106`. The chip struct owns ALSA card/PCI state, I/O port, IRQ, model/serial, spinlock, optional AC97 codec, four PCM devices, playback/capture channel arrays, SPDIF state arrays, capture source state, I2C capture volume cache, MIDI devices, SPI DAC register cache, and PM volume snapshots.

The header declares shared functions: `snd_ca0106_mixer()`, `snd_ca0106_proc_init()`, `snd_ca0106_ptr_read()`, `snd_ca0106_ptr_write()`, `snd_ca0106_i2c_write()`, `snd_ca0106_spi_write()`, and PM mixer save/restore helpers.

## Control Flow Role

This header drives the control decisions in the implementation files. Main probe selects behavior from `struct snd_ca0106_details`, initializes GPIO/I2C/SPI according to capability flags, programs pointer registers from the declared constants, and exposes PCM channels using the logical channel mappings. Mixer controls use the same constants to update SPDIF, capture source, playback volume, I2C ADC, and SPI DAC state. Procfs diagnostics dump and write the pointer and flat register spaces defined here.

## State and Persistence Behavior

The header defines which state must be cached in software: SPDIF default and per-stream status, selected capture source, I2C per-source volumes, shared mic/line selection, SPI DAC register images, and saved PM volumes. The pointer register model means channel-specific state is selected by a `reg, channel` pair, protected in implementation by `emu_lock`.

## Dependencies and Integration Points

The header includes `ca_midi.h` and is included by all CA0106 source files. It binds the driver to ALSA AC97, PCM, control, MIDI, procfs diagnostics, Linux PCI I/O, and optional PM support. The register definitions are specific to Creative Audigy LS, Live 24-bit, Audigy SE, X-Fi Extreme Audio variants, and compatible motherboard devices.

## Risks and Edge Cases

Many fields are reverse-engineered or annotated as unknown. Some settings are global despite per-channel PCM APIs, especially HCFG format bits and parts of `CAPTURE_CONTROL`, so concurrent streams with different formats/rates can conflict. Incorrect SPI DAC mapping can mute or power down the wrong analog channel. Incorrect GPIO mode can swap line/mic, side-out/line-in, or SPDIF/analog behavior. The header notes capture rate and S32_LE limitations.

## Test Signals

Useful validation includes building all CA0106 objects against this header, probing supported subsystem IDs, exercising all four PCM devices, testing SPDIF PCM and AC3/DTS status bits, analog routing, AC97 and non-AC97 boards, I2C ADC capture source/volume changes, SPI DAC mute/power controls, MIDI UART A operation, proc register dumps, and suspend/resume restoration of cached mixer/SPI/I2C/SPDIF state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_main.c -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_main.c

## Purpose

`ca0106_main.c` is the main ALSA PCI driver for Creative CA0106-based cards such as Audigy LS, Live 24-bit, Audigy SE, X-Fi Extreme Audio, and several onboard variants. It owns PCI probing, chip identification, low-level pointer register access, SPI/I2C helper implementations, PCM playback/capture devices, DMA period-list setup, interrupt handling, MIDI initialization, chip initialization/stop, and suspend/resume.

## Important APIs, Types, and Functions

The driver uses `struct snd_ca0106` from `ca0106.h` as its central state. `ca0106_chip_details[]` maps subsystem serials to board names and capability flags: AC97 presence, GPIO type, I2C ADC, and SPI DAC channel map.

`snd_ca0106_ptr_read()` and `snd_ca0106_ptr_write()` are the fundamental indexed-register accessors, serializing `CA0106_PTR`/`CA0106_DATA` cycles with `emu_lock`. `snd_ca0106_spi_write()` writes 16-bit SPI DAC commands and polls completion. `snd_ca0106_i2c_write()` writes ADC register/value pairs through the I2C engine with retry/abort handling.

PCM code is split by logical stereo pairs: front, rear, center/LFE, and side/unknown. Playback/capture open functions allocate `struct snd_ca0106_pcm`, bind channel state, set hardware constraints, and power SPI DACs for non-front playback channels. Prepare functions program rates, formats, DMA addresses, period lists, and buffer pointers. Trigger functions update `BASIC_INTERRUPT` and `EXTENDED_INT_MASK`. Pointer callbacks read hardware pointer registers.

Probe/setup functions include `snd_ca0106_create()`, `ca0106_init_chip()`, `ca0106_stop_chip()`, `snd_ca0106_pcm()`, `snd_ca0106_ac97()`, `snd_ca0106_midi()`, `__snd_ca0106_probe()`, and `snd_ca0106_probe()`.

## Control Flow

Probe allocates an ALSA card, enables PCI, sets a 32-bit DMA mask, requests BARs, records the I/O port, requests a shared IRQ, allocates a 1024-byte DMA buffer for playback period tables, enables bus mastering, reads subsystem IDs, selects board details, initializes the chip, creates four PCM devices, optionally creates an AC97 mixer, creates CA0106 mixer controls, initializes MIDI UART A, optionally initializes procfs diagnostics, registers the card, and stores driver data.

Chip initialization disables interrupts, initializes SPDIF status words, mutes playback/capture paths, configures SPDIF/analog routing, capture feedback, routing registers, capture source defaults, GPIO mode, base interrupt enables, HCFG audio enable, optional I2C ADC register defaults and cached volumes, and optional SPI DAC defaults plus front DAC power-up.

Playback prepare writes a per-channel period table into the shared DMA table buffer, sets rate fields in `BASIC_INTERRUPT` and `CAPTURE_CONTROL`, sets global S16/S32 HCFG playback format, writes playback list/address/size/pointer registers, and unmutes output. Capture prepare sets capture rate/format, updates I2C oversampling for ADC boards, and writes capture DMA address/size/pointer.

Playback trigger walks all linked playback substreams in the sync group, sets their running state, accumulates channel start and period interrupt bits, and then updates hardware once. Capture trigger handles a single channel. The IRQ handler reads `CA0106_IPR` and `EXTENDED_INT`, calls `snd_pcm_period_elapsed()` for active playback/capture channels whose extended bits fired, delegates MIDI A interrupts through `ca_midi`, acknowledges extended and global interrupt status, and returns shared IRQ status.

Suspend changes power state, suspends AC97 if present, saves mixer volumes, stops the chip, and resume reinitializes hardware, resumes AC97, restores mixer state, rewrites SPI registers, and returns to D0.

## State and Persistence Behavior

The driver caches board identity, SPDIF defaults and stream bits, capture source selections, I2C volumes, SPI DAC register images, channel use/running state, and PM volume snapshots. The playback period table DMA buffer is persistent for the card lifetime and partitioned per channel. Runtime PCM private data is allocated per open substream and freed through `runtime->private_free`.

Some hardware settings are global despite per-channel APIs, including HCFG S32 playback/capture bits and parts of rate programming. SPI DAC power is managed on playback open/close to reduce power, with front kept powered.

## Dependencies and Integration Points

The file integrates with ALSA core, PCM, AC97, procfs, PCI, DMA mapping, interrupts, PM, and the shared `ca_midi` helper. It depends heavily on `ca0106.h` register definitions and calls mixer/proc functions implemented in sibling files.

## Risks and Edge Cases

Known comments mention unload stability problems, incomplete capture channel coverage, limited capture rates, and global format conflicts. `snd_ca0106_midi()` appears to set MIDI A `rx_enable` to `INTE_MIDI_TX_B`, which is suspicious because receive status uses `IPR_MIDI_RX_A`. `snd_ca0106_i2c_write()` has a cumulative timeout counter across retries. Playback prepare writes `PLAYBACK_PERIOD_SIZE` twice, ending with zero, which is intentional or experimental but fragile. Concurrent streams at different rates/formats can race global register fields.

## Test Signals

Validate probe across supported subsystem IDs and forced `subsystem=`. Test four PCM devices, sync-start grouped playback, period interrupts, pointer stability warnings, S16/S32 formats, 48/96/192 kHz playback and capture, SPDIF AC3/DTS routing, analog output on SPI and non-SPI boards, I2C ADC capture source and oversampling, AC97 boards, MIDI UART A RX/TX, module unload, and suspend/resume with mixer/SPI/SPDIF state restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_mixer.c

## Purpose

`ca0106_mixer.c` implements ALSA mixer/control surfaces for the CA0106 driver. It maps user controls to CA0106 pointer registers, GPIO mode bits, I2C ADC source/attenuation registers, SPI DAC mute bits, SPDIF IEC958 status words, and virtual master controls. It also cleans up and renames AC97 controls to match the CA0106 signal path.

## Important APIs, Types, and Functions

Hardware routing helpers include `ca0106_spdif_enable()`, `ca0106_set_capture_source()`, `ca0106_set_i2c_capture_source()`, `ca0106_set_capture_mic_line_in()`, and `ca0106_set_spdif_bits()`.

Control callbacks include shared SPDIF switch get/put, digital capture source enum get/put, I2C analog capture source enum get/put, shared mic/line or line/side enum get/put, SPDIF default/stream/mask get/put, pointer-register volume get/put, I2C volume get/put, and SPI mute get/put.

Macros `CA_VOLUME()` and `I2C_VOLUME()` define repeated controls with TLV dB scales. `snd_ca0106_volume_ctls[]` defines analog and IEC958 playback volumes, capture feedback volume, IEC958 controls, SPDIF switch, and capture source controls. `snd_ca0106_volume_i2c_adc_ctls[]` adds per-source ADC capture volumes. `snd_ca0106_volume_spi_dac_ctl()` dynamically creates analog playback switches for SPI-DAC boards.

`snd_ca0106_mixer()` is the exported setup entry point. Under PM sleep, `snd_ca0106_mixer_suspend()` and `snd_ca0106_mixer_resume()` save and restore key volume/routing state.

## Control Flow

Mixer setup removes many generic AC97 controls that do not match this hardware path and renames AC97 playback controls to capture-oriented names. It adds CA0106-specific volume/SPDIF/capture controls, conditionally adds I2C ADC controls and a GPIO shared-jack selector, conditionally adds SPI DAC mute controls, creates a virtual `Master Playback Volume` with follower controls, and for SPI boards creates a virtual `Master Playback Switch`.

When users toggle IEC958 playback, `ca0106_spdif_enable()` switches `SPDIF_SELECT1/2`, updates capture control bit `0x1000`, and adjusts GPIO bits. Capture source controls update `CAPTURE_SOURCE` nibble fields or I2C ADC mux/attenuation. Volume controls translate ALSA 0..255 values to inverted CA0106 attenuation bytes and write all four byte lanes. SPI mute controls update cached DAC registers and send one SPI command.

On suspend, selected pointer-register volumes are saved. On resume, volumes are restored, SPDIF mode and capture source are re-applied, I2C source/volume is forced, all SPDIF status words are rewritten, and shared input GPIO is restored for I2C ADC boards.

## State and Persistence Behavior

The mixer relies on state cached in `struct snd_ca0106`: `spdif_enable`, `capture_source`, `i2c_capture_source`, `i2c_capture_volume`, `capture_mic_line_in`, `spdif_bits`, `spdif_str_bits`, `spi_dac_reg`, and `saved_vol`. Controls return cached values for software-owned state and read pointer registers for hardware volume state.

Default SPDIF writes deliberately mirror default and stream status for older alsa-lib compatibility. I2C source switching mutes the ADC before changing attenuation and mux. SPI mute uses cached register images because DAC register readback is not available through this path.

## Dependencies and Integration Points

The file depends on `ca0106.h`, ALSA control/TLV APIs, AC97 controls already created by `ca0106_main.c` on AC97-capable boards, and the low-level pointer/I2C/SPI accessors from `ca0106_main.c`. It exposes user-visible ALSA mixer and PCM IEC958 controls.

## Risks and Edge Cases

Control removal/renaming is name-based, so upstream AC97 naming changes can leave stale controls or fail to rename expected controls. Several controls update global hardware fields and can affect active streams. `snd_ca0106_proc_i2c_write()` is separate, but mixer I2C writes still assume the ADC transaction helper succeeds. Dynamic SPI controls trust `details->spi_dac` channel-to-DAC mapping; a wrong table entry mutes the wrong channel. Resume unconditionally calls `ca0106_set_i2c_capture_source()` even though only some boards have I2C state initialized, but the later shared-jack restore is guarded.

## Test Signals

Test all mixer controls with `amixer`: analog/IEC958 volumes, capture feedback, IEC958 switch, digital and analog capture source enums, I2C per-source capture volumes, shared mic/line or line/side selector, SPI DAC playback switches, and virtual master followers. Confirm register changes through proc dumps, verify SPDIF status defaults and stream overrides, test resume restoration, and test active playback/capture while controls change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_proc.c -->
# sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_proc.c

## Purpose

`ca0106_proc.c` provides optional ALSA procfs diagnostics and low-level register poking for CA0106 devices when `CONFIG_SND_PROC_FS` is enabled. It exposes IEC958/SPDIF input status decoding, flat PCI I/O register dumps, pointer-register dumps, pointer-register writes, and I2C writes.

## Important APIs, Types, and Functions

`struct snd_ca0106_category_str` maps IEC958 consumer category codes to names. `snd_ca0106_proc_dump_iec958()` decodes a 32-bit channel status value into readable consumer or professional SPDIF fields using ALSA `asoundef.h` IEC958 constants.

Read callbacks include `snd_ca0106_proc_iec958()`, `snd_ca0106_proc_reg_read32()`, `snd_ca0106_proc_reg_read16()`, `snd_ca0106_proc_reg_read8()`, `snd_ca0106_proc_reg_read1()`, and `snd_ca0106_proc_reg_read2()`. Write callbacks include `snd_ca0106_proc_reg_write32()`, `snd_ca0106_proc_reg_write()`, and `snd_ca0106_proc_i2c_write()`.

`snd_ca0106_proc_init()` registers proc entries: `iec958`, `ca0106_reg32`, `ca0106_reg16`, `ca0106_reg8`, `ca0106_regs1`, `ca0106_i2c`, and `ca0106_regs2`.

## Control Flow

The main driver calls `snd_ca0106_proc_init()` during probe only under `CONFIG_SND_PROC_FS`. The `iec958` reader checks `SAMPLE_RATE_TRACKER_STATUS`, prints lock/audio-valid state and estimated sample rate, and if SPDIF is locked reads `SPDIF_INPUT_STATUS` and decodes channel status fields.

Flat register readers dump offsets below `0x20` in 32-bit, 16-bit, or 8-bit widths, taking `emu_lock` around port reads. Pointer-register readers dump `0x00..0x3f` and `0x40..0x7f` for channels 0 through 3 using `snd_ca0106_ptr_read()`. Write entries parse hex text lines: flat `reg value` for `ca0106_reg32`, indexed `reg channel value` for `ca0106_regs1`, and `reg value` for `ca0106_i2c`.

## State and Persistence Behavior

This file does not own long-lived state, but it can mutate hardware state through proc writes. Pointer-register and I2C writes persist in device registers until changed, reset, suspend/resume reinit, or module unload. Register reads are snapshots and may race with active stream hardware movement despite locking only the host access cycle.

## Dependencies and Integration Points

The file depends on ALSA proc/info APIs, IEC958 constants from `sound/asoundef.h`, low-level CA0106 pointer and I2C helpers from `ca0106_main.c`, and register constants from `ca0106.h`. It is conditionally linked by the CA0106 Makefile and conditionally called from the main driver.

## Risks and Edge Cases

The proc write interfaces are powerful and can disrupt live audio, routing, DMA, GPIO, or codec state. `snd_ca0106_proc_i2c_write()` uses `if ((reg <= 0x7f) || (val <= 0x1ff))`, which permits writes when only one side is in range; this looks like it should be an AND and can pass invalid register/value pairs to `snd_ca0106_i2c_write()`, which will reject them but still logs errors. Flat 32-bit writes mask the register to a dword boundary and allow any offset below `0x40`, including sensitive control registers.

## Test Signals

With procfs enabled, verify each proc entry exists. Read `iec958` with no lock, with locked audio, and with non-audio streams. Compare register dumps against expected initialization values. Exercise write paths only on test hardware: valid pointer writes should appear in subsequent dumps, invalid indexed writes should be ignored by bounds checks, and invalid I2C writes should be rejected by the I2C helper without corrupting ADC state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/ca0106/ca0106_proc.c -->
