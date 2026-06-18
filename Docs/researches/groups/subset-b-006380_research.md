# Research: subset-b-006380

Grouped research for Sound Blaster, SC-6000, SoundScape, and WaveFront ISA ALSA sources. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb16.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb16.c

## Purpose
This is the card-level driver for legacy ISA and ISA PnP Sound Blaster 16 cards. When included through `sbawe.c` with `SNDRV_SBAWE` defined, the same implementation also supports Sound Blaster AWE32/AWE64 variants and optional EMU8000 wavetable setup. It resolves module parameters or PnP resources, creates the shared `struct snd_sb` DSP object, attaches PCM, mixer, MPU-401, OPL3, optional CSP, and optional EMU8000 devices, and registers the ALSA card.

## Important APIs, Types, and Functions
The user-visible configuration surface is the array of module parameters: `index`, `id`, `enable`, optional `isapnp`, `port`, `mpu_port`, `fm_port`, optional `awe_port`, `irq`, `dma8`, `dma16`, `mic_agc`, optional `csp`, and optional `seq_ports`. `struct snd_card_sb16` stores the devm-owned FM reservation, the `struct snd_sb *chip`, and PnP logical-device pointers. `snd_card_sb16_pnp()` activates the PnP audio and optional wavetable logical devices and copies resources into the module parameter arrays. `snd_sb16_card_new()` wraps `snd_devm_card_new()`. `snd_sb16_probe()` is the common device constructor for both ISA and PnP. ISA entry points are `snd_sb16_isa_match()`, `snd_sb16_isa_probe()`, and `snd_sb16_isa_probe1()`. PnP entry is `snd_sb16_pnp_detect()`. Module lifetime is handled by `alsa_card_sb16_init()` and `alsa_card_sb16_exit()`.

## Control Flow
For legacy ISA cards, the ISA driver skips slots disabled by `enable[]` or selected for PnP. It auto-finds IRQ and DMA channels when requested, then probes a fixed port or tries 0x220, 0x240, 0x260, and 0x280. `snd_sb16_isa_probe1()` creates the ALSA card, reserves the legacy FM region at 0x388 to avoid conflicts, sets FM and AWE ports derived from the base address, and calls `snd_sb16_probe()`. For PnP cards, `snd_sb16_pnp_detect()` selects the next enabled PnP slot, creates the card, activates logical devices, imports PnP resources, and calls the same probe function.

Inside `snd_sb16_probe()`, the driver calls `snd_sbdsp_create()` with `snd_sb16dsp_interrupt` and requested DMA channels, verifies that the detected hardware is `SB_HW_16`, configures non-PnP IRQ/DMA/MPU mixer registers with `snd_sb16dsp_configure()`, creates SB16 PCM via `snd_sb16dsp_pcm()`, optionally creates an MPU-401 UART, optionally creates OPL3 hwdep, builds mixer controls, attaches CSP when requested and available, attaches EMU8000 for AWE builds, applies the Mic AGC register bit, and registers the card.

## State and Persistence
State is in module parameter arrays, devm-managed ALSA card private data, `struct snd_sb`, and hardware registers. The file does not persist configuration to disk. Power management saves only mixer register state through `snd_sbmixer_suspend()` and restores it after `snd_sbdsp_reset()` in resume. PnP resources overwrite the module parameter arrays for the selected slot, so later longname construction and setup use resolved values.

## Dependencies and Integration Points
This file depends on Linux ISA, PnP, IRQ, DMA, and module frameworks, plus ALSA core, SB common APIs, SB16 PCM APIs, mixer APIs, OPL3, MPU-401, optional SB16 CSP, optional EMU8000, and optional sequencer support. It is built as `sb16` normally and as `sbawe` when included by `sbawe.c`.

## Risks and Edge Cases
Resource probing is fragile because old ISA hardware may not respond reliably. PnP and ISA paths share global parameter arrays, so failed attempts can leave tried port values in memory. The code returns errors for SB Pro/ALS100 detections in the SB16 module and asks the user to load another driver. Optional devices are partly fatal: OPL absence is tolerated, but EMU8000 failure for AWE is fatal. `sprintf()` is used for card strings, relying on ALSA fixed-size fields and known small values.

## Test Signals
Useful signals include successful module load for both ISA and PnP paths, card longname showing expected base/IRQ/DMA, `aplay -l` and `arecord -l` showing SB16 DSP, mixer controls including Mic AGC and optional 16-bit DMA allocation, optional MPU/OPL/CSP/EMU devices appearing, interrupt-driven playback/capture, and suspend/resume preserving mixer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb16_csp.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb16_csp.c

## Purpose
This file implements ALSA hwdep support for the SB16 Creative Signal Processor, also known as ASP/CSP. It detects the CSP, creates a hwdep device, loads and unloads CSP microcode, autoloads kernel firmware for compressed PCM formats, starts/stops/pauses/restarts the processor, exposes QSound mixer controls, and publishes a read-only proc status entry.

## Important APIs, Types, and Functions
`snd_sb_csp_new()` is the exported constructor. It calls `csp_detect()`, creates `SB16-CSP` hwdep, allocates `struct snd_sb_csp`, fills function pointers in `p->ops`, initializes `access_mutex`, and creates the proc entry. The hwdep operations are `snd_sb_csp_open()`, `snd_sb_csp_ioctl()`, and `snd_sb_csp_release()`. Ioctls support `SNDRV_SB_CSP_IOCTL_INFO`, `LOAD_CODE`, `UNLOAD_CODE`, `START`, `STOP`, `PAUSE`, and `RESTART`.

Microcode parsing centers on `snd_sb_csp_riff_load()`, which reads a user-supplied RIFF/CSP container, finds a requested function, loads `init` and `main` blocks through `snd_sb_csp_load_user()`, and fills codec capability fields. `snd_sb_csp_autoload()` requests built-in firmware names for mu-law, A-law, and IMA ADPCM. Hardware helpers include `command_seq()`, `set_codec_parameter()`, `set_register()`, `read_register()`, `set_mode_register()`, and `get_version()`. QSound controls are built and removed by `snd_sb_qsound_build()` and `snd_sb_qsound_destroy()`.

## Control Flow
Detection writes and reads CSP register 0x83 under the SB register lock, checks version range 0x10..0x1f, and resets the DSP. User-space opens the hwdep exclusively through `snd_sb_csp_use()`, which is guarded by `access_mutex` and rejects concurrent users. `LOAD_CODE` refuses to run while the CSP is active, validates RIFF headers and chunk bounds, loads initialization chunks first, then the required main chunk, maps VOC codec IDs to ALSA format capability bits, decouples CSP from IRQ/DMA lines, and marks the code loaded. `UNLOAD_CODE` clears capabilities and QSound controls when not running.

The PCM engine in `sb16_main.c` calls the `ops` callbacks to autoload and start codecs during PCM prepare. `snd_sb_csp_start()` validates loaded state and requested width/channels, mutes PCM mixer volume during the hardware transition, sets STOP/RUN mode, programs sample type and start command, records run state, and enables QSound if applicable. Stop disables QSound, sends STOP, restores volume, and clears running/paused bits.

## State and Persistence
Runtime state is in `struct snd_sb_csp`: `used`, `running` bit flags, `mode`, accepted format/channel/width/rate masks, run width/channel, loaded codec name/function, firmware cache pointers, QSound controls, QSound positions, and locks. Firmware blobs requested by `request_firmware()` are cached in `p->csp_programs` until hwdep free. No state is persisted beyond the kernel object lifetime.

## Dependencies and Integration Points
The file depends on ALSA hwdep, control, proc info, SB16 CSP UAPI definitions, SB mixer/DSP helpers from the Sound Blaster core, and Linux firmware loading. It exports `snd_sb_csp_new()` for `sb16.c` and is used at runtime by `sb16_main.c` through the CSP ops table.

## Risks and Edge Cases
RIFF parsing operates on user pointers and must preserve length checks; malformed lengths or unsupported VOC types return errors. `snd_sb_csp_unuse()` decrements `used` without checking underflow, so caller pairing matters. Some helper calls ignore intermediate command failures, reflecting historical hardware assumptions. QSound control removal calls `snd_ctl_remove()` on possibly NULL members after partial build failure, relying on ALSA tolerance. Firmware absence disables autoloaded compressed formats.

## Test Signals
Look for `cspD*` proc entries, `SB16-CSP` hwdep, successful `LOAD_CODE`/`INFO`/`START`/`STOP` ioctl sequences, autoloaded mu-law/A-law/IMA playback and capture through normal PCM open/prepare, QSound controls appearing only for QSound firmware, and clean unload while no PCM stream is running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb16_csp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb16_main.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb16_main.c

## Purpose
This file implements the SB16 DSP PCM engine, interrupt handler, DMA allocation control, and non-PnP DSP mixer-register configuration. It is the shared low-level PCM implementation used by SB16-class cards and some clones.

## Important APIs, Types, and Functions
The exported APIs are `snd_sb16dsp_pcm()`, `snd_sb16dsp_get_pcm_ops()`, `snd_sb16dsp_configure()`, and `snd_sb16dsp_interrupt()`. ALSA PCM operations are `snd_sb16_playback_open/close/prepare/trigger/pointer` and capture equivalents. `snd_sb16_setup_rate()` programs shared sample-rate registers. Optional CSP glue functions add compressed formats and start/stop CSP processing. The control `snd_sb16_dma_control` exposes "16-bit DMA Allocation" with Auto, Playback, and Capture choices.

## Control Flow
Opening playback or capture takes `open_lock`, rejects duplicate stream direction, chooses 16-bit DMA if available and not reserved for the opposite direction, otherwise falls back to 8-bit DMA, and sets runtime format/rate/buffer constraints. If no 16-bit channel exists, DSP v4 can still accept 16-bit samples through 8-bit DMA, so the mode combines 8-bit DMA ownership with 16-bit sample format. CSP hooks may add compressed formats for manually loaded or autoloadable codecs.

Prepare calls optional CSP prepare, computes signed/unsigned and mono/stereo format bytes, programs the shared input and output sample rate if not rate-locked, programs ISA DMA with autoinit, writes the DSP auto-init command and period count, and leaves DMA disabled until trigger. Trigger start/resume locks the rate for the active direction and enables the chosen DSP DMA engine; stop/suspend disables it, handles the AWE32 DSP4.13 quirk by re-enabling the other direction if still active, and clears the rate lock bit.

The interrupt handler reads SB16 IRQ status from mixer register `SB_DSP4_IRQSTATUS`, dispatches MPU input to the MPU callback, services 8-bit and 16-bit IRQs separately, calls `snd_pcm_period_elapsed()` for active substreams matching the width, updates CSP QSound during playback, disables unexpected DMA interrupts, and acknowledges the appropriate interrupt type.

## State and Persistence
State lives in `struct snd_sb`: `mode`, `force_mode16`, `locked_rate`, DMA sizes, substream pointers, `open_lock`, `reg_lock`, `mixer_lock`, optional `csp`, and MPU callback fields. There is no persistent storage. The "16-bit DMA Allocation" control changes `force_mode16` only while PCM is idle and disables both DMA channels on change.

## Dependencies and Integration Points
The file depends on ALSA PCM/control APIs, ISA DMA helpers, SB command/ack/mixer helpers, optional CSP UAPI and callbacks, and optional MPU interrupt integration. It is constructed by SB16 card drivers through `snd_sb16dsp_pcm()` and used by compatible drivers through exported PCM ops.

## Risks and Edge Cases
Full duplex is constrained by asymmetric 8-bit and 16-bit DMA channels, and the code contains hardware-specific workarounds for buggy capture/playback transitions. Shared sample-rate locking means simultaneous playback and capture must use the same rate. The interrupt handler always returns `IRQ_HANDLED`, which is normal for non-shared ISA IRQs but can hide spurious signals on shared clone configurations. CSP state writes `chip->open` with CSP mode values, so CSP and PCM open state share a field with care.

## Test Signals
Verify supported format/rate constraints for 8-bit-only, 16-bit, and single-DMA configurations; playback/capture DMA starts only on trigger; pointer callbacks track DMA counters; "16-bit DMA Allocation" rejects changes while streams are active; simultaneous streams lock to one rate; and interrupts produce period elapsed callbacks for both 8-bit and 16-bit modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb16_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb8.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb8.c

## Purpose
This is the card-level ISA driver for Sound Blaster 1.0, 2.0, and Pro class cards and compatible devices. It resolves legacy resources, creates the low-level SB DSP object, adds PCM, mixer, OPL3, and MIDI devices, and registers the ALSA card.

## Important APIs, Types, and Functions
Module parameters are `index`, `id`, `enable`, `port`, `irq`, and `dma8`. `struct snd_sb8` stores the FM reservation and `struct snd_sb *chip`. `snd_sb8_interrupt()` routes the single ISA interrupt to either PCM or MIDI handling depending on `chip->open & SB_OPEN_PCM`. `snd_sb8_match()` validates enabled slots and requires explicit IRQ and DMA. `snd_sb8_probe()` constructs the card. Optional PM callbacks save and restore mixer state.

## Control Flow
Probe creates a devm ALSA card, reserves 0x388 for FM conflict avoidance, and either probes the requested DSP base or auto-probes 0x220, 0x240, and 0x260. It rejects SB16-class detections and suggests the SB16 or ALS100 driver. It then creates SB8 PCM, mixer controls, OPL3 hwdep at either base+8 for SB1/SB2 or base/base+2 for Pro, creates SB8 MIDI rawmidi, fills card strings, registers the card, and stores driver data.

## State and Persistence
State is limited to module parameter arrays, the ALSA card private area, the shared `struct snd_sb`, and mixer hardware registers. Suspend marks the card D3hot and saves mixer registers; resume resets the DSP, restores mixer registers, and marks D0. No disk persistence exists.

## Dependencies and Integration Points
The file uses the Linux ISA driver framework, devm resource management, ALSA core, SB common DSP creation, SB8 PCM, SB mixer, SB8 MIDI, and OPL3 hwdep.

## Risks and Edge Cases
Auto-probing legacy IO ports can collide with unrelated ISA devices on real hardware. IRQ and DMA are mandatory because there is no reliable autodetection here. Interrupt routing depends on `chip->open`, so incorrect open state can send MIDI interrupts to PCM or vice versa. SB Pro stereo and older DSP behavior are handled in `sb8_main.c`, not here.

## Test Signals
Module load should create one card per enabled slot with expected `SB8` or `SB Pro` names. Playback/capture devices should be half-duplex. Mixer controls should match the detected hardware generation. MIDI rawmidi should work when PCM is not open. Suspend/resume should preserve mixer values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb8_main.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb8_main.c

## Purpose
This file implements the low-level PCM engine and interrupt handling for 8-bit Sound Blaster, Sound Blaster Pro, and Jazz16-like cards. It handles legacy DSP command programming, ISA DMA, SB Pro stereo constraints, and half-duplex ALSA PCM registration.

## Important APIs, Types, and Functions
The exported APIs are `snd_sb8dsp_pcm()` and `snd_sb8dsp_interrupt()`, with MIDI exports declared for companion `sb8_midi.c`. PCM operations include `snd_sb8_open()`, `snd_sb8_close()`, playback/capture prepare and trigger functions, and pointer callbacks. Rate constraints use `clock`, `hw_constraints_clock`, `stereo_clocks`, `snd_sb8_hw_constraint_rate_channels()`, and `snd_sb8_hw_constraint_channels_rate()`.

## Control Flow
Open is half-duplex: it rejects any already open PCM stream, records playback or capture substream, assigns base hardware constraints, then adjusts constraints by hardware type. SB Pro allows stereo only at particular timer-derived rates, Jazz16 permits wider rates and optional 16-bit samples when DMA16 is valid, and later DMA configurations loosen buffer size limits.

Playback prepare chooses the DSP command family based on hardware and rate, handles SB Pro stereo by enabling mixer stereo, forcing a dummy interrupt sequence, setting the sample-rate divisor, optionally disabling playback filter, setting the block size, and programming ISA DMA in autoinit write mode. Capture prepare similarly selects input command mode, disables speaker, sets stereo/sample-rate/filter state, programs block size, and programs DMA read mode. Triggers start the stored DSP command; single-cycle SB1 commands write a count every start. Stops disable DMA or reset DSP for high-speed modes and restore stereo/filter state.

The interrupt handler acknowledges the 8-bit DSP interrupt, switches on `chip->mode`, retriggers non-autoinit SB1-style transfers when needed, and calls `snd_pcm_period_elapsed()` for the active substream.

## State and Persistence
State is held in `struct snd_sb`: mode bits, playback/capture format commands, period and buffer sizes, substream pointers, DMA numbers, and temporary use of `force_mode16` to stash old SB Pro mixer filter/stereo register values. No persistent storage is used.

## Dependencies and Integration Points
The code depends on SB command and ack helpers, SB mixer helpers, ALSA PCM runtime constraints, and ISA DMA helpers. It is invoked by `sb8.c` after `snd_sbdsp_create()` detects a compatible DSP.

## Risks and Edge Cases
The code documents lack of access to old SB8 hardware and contains timing-sensitive paths. Stereo setup uses a forced interrupt and temporary mixer/filter state. `force_mode16` is repurposed for SB Pro filter state, so future changes must avoid assuming it only means 16-bit DMA allocation in SB8 contexts. Some trigger switch statements do not reject unknown commands explicitly.

## Test Signals
Confirm mono playback/capture on SB1/SB2, SB Pro stereo only at legal rates, Jazz16 16-bit mode when DMA16 is 5 or 7, period interrupts in both autoinit and single-cycle modes, correct DMA pointer reporting, and mixer filter/stereo restoration after stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb8_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb8_midi.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb8_midi.c

## Purpose
This file implements the raw MIDI interface for 8-bit Sound Blaster DSP MIDI mode. It supports input, output, and duplex UART behavior on DSP version 2.0 and later, using timer-driven polling for output.

## Important APIs, Types, and Functions
The exported functions are `snd_sb8dsp_midi_interrupt()` and `snd_sb8dsp_midi()`. RawMIDI callbacks are `snd_sb8dsp_midi_input_open/close/trigger` and output equivalents. `snd_sb8dsp_midi_output_write()` drains ALSA transmit bytes to the DSP. `snd_sb8dsp_midi_output_timer()` keeps output moving while triggered.

## Control Flow
Opening input or output checks `chip->open` under `open_lock`. DSP 2.0+ allows the opposite MIDI stream and its trigger flags to coexist; older DSPs do not. On first MIDI open, the DSP is reset and DSP 2.0+ is put into IRQ UART mode. Input trigger enables or disables input interrupt mode, issuing `SB_DSP_MIDI_INPUT_IRQ` toggles on old hardware. Output trigger starts a one-jiffy timer and immediately attempts to write. Output writing peeks one byte at a time, waits briefly for FIFO availability on DSP 2.0+, writes either directly or through `SB_DSP_MIDI_OUTPUT`, acknowledges transmitted bytes, and stops the timer when no data remains.

Interrupt handling drains up to 64 bytes while data is available, acknowledges orphan interrupts when no rawmidi exists, and calls `snd_rawmidi_receive()` only when the input trigger is active.

## State and Persistence
State is in `struct snd_sb`: `open` bits, MIDI substream pointers, `midi_timer`, and `midi_input_lock`. No persistent storage exists.

## Dependencies and Integration Points
This file depends on ALSA rawmidi APIs, SB IO-port macros and DSP command helpers, and the card-level interrupt dispatcher in `sb8.c`.

## Risks and Edge Cases
Timer and interrupt paths share open and virtual stream state, so lock pairing matters. Output uses small hard busy-waits and a periodic timer rather than hardware transmit interrupts. Closing output deletes the timer synchronously, which is important for avoiding use-after-close. `snd_sb8dsp_midi_interrupt()` returns `IRQ_HANDLED` even when it drains no triggered data as long as a rawmidi exists.

## Test Signals
Open/close both MIDI directions on DSP 2.0+ for duplex, verify old hardware rejects conflicting opens, confirm output timer stops after transmit buffer drains, confirm input data is ignored until trigger is enabled, and verify MIDI use while PCM is closed because `sb8.c` routes the shared IRQ by `SB_OPEN_PCM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb8_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb_common.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb_common.c

## Purpose
This file provides the shared low-level Sound Blaster DSP creation, command, byte-read, reset, and hardware-detection routines used by SB8, SB16, and compatible drivers. It also exports mixer functions implemented in `sb_mixer.c`.

## Important APIs, Types, and Functions
Exports include `snd_sbdsp_command()`, `snd_sbdsp_get_byte()`, `snd_sbdsp_reset()`, and `snd_sbdsp_create()`. Internal helpers are `snd_sbdsp_version()` and `snd_sbdsp_probe()`. `snd_sbdsp_create()` allocates and initializes `struct snd_sb`, requests IRQ, IO region, and ISA DMA channels, then probes the DSP.

## Control Flow
`snd_sbdsp_command()` busy-waits until the DSP command port is writable and sends one byte. `snd_sbdsp_get_byte()` busy-waits until data is available and reads one byte. Reset toggles the reset register and expects the 0xaa ready byte. Probe resets the DSP, sends `SB_DSP_GET_VERSION`, maps major/minor version to `SB_HW_10`, `SB_HW_20`, `SB_HW_201`, `SB_HW_PRO`, or `SB_HW_16` for auto hardware mode, and fills `chip->name` and `chip->version`.

`snd_sbdsp_create()` initializes all spinlocks, default resource fields, installs the IRQ handler, stores `card->sync_irq`, requests the base 16-byte port region unless ALS4000 skips allocation, requests DMA8 and DMA16 when available and valid, assigns card/hardware fields, and calls probe. Invalid 16-bit DMA on non-ALS100 cards is silently treated as no duplex by setting `dma16 = -1`.

## State and Persistence
State is the allocated `struct snd_sb`, devm-owned resources, IRQ/DMA numbers, detected hardware enum, DSP version, and name. No persistent storage is used.

## Dependencies and Integration Points
The file depends on Linux IO ports, IRQs, ISA DMA helpers, ALSA core, and `sound/sb.h`. It is the common constructor used by `sb8.c`, `sb16.c`, and clone drivers. It also exports mixer symbols from the same module boundary.

## Risks and Edge Cases
The command and read routines use long busy loops and return generic timeout failures, so dead hardware can stall CPU briefly. Detection relies on version bytes after reset and can misclassify clones unless a specific hardware enum was provided. ALS4000 skips IO/DMA allocation here, so its caller must have already handled resources. Shared IRQ flags are only used for ALS4000 and CS5530 hardware enums.

## Test Signals
Confirm reset returns 0xaa, version mapping produces expected hardware names, resource conflicts fail with `-EBUSY`, invalid DMA16 degrades to no duplex where intended, and exported helpers work for SB8/SB16 card constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb_mixer.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sb_mixer.c

## Purpose
This file implements Sound Blaster mixer register IO, ALSA mixer controls for multiple SB hardware generations and clones, initialization of default mixer values, and suspend/resume save-restore of mixer registers.

## Important APIs, Types, and Functions
Public functions are `snd_sbmixer_write()`, `snd_sbmixer_read()`, `snd_sbmixer_add_ctl()`, `snd_sbmixer_new()`, and PM-only `snd_sbmixer_suspend()`/`snd_sbmixer_resume()`. Control callbacks cover single and double register fields, SB Pro capture source mux, SB16 input route booleans, DT019x capture source enum, and ALS4000 mono capture route enum. Hardware-specific control arrays include `snd_sb20_controls`, `snd_sbpro_controls`, `snd_sb16_controls`, `snd_dt019x_controls`, and `snd_als4000_controls`.

## Control Flow
Read/write helpers select a mixer register through `MIXER_ADDR`, delay, then read or write `MIXER_DATA`. Control callbacks decode `private_value` fields to identify registers, bit shifts, and masks, and perform locked read-modify-write operations under `mixer_lock`. `snd_sbmixer_add_ctl()` selects a callback template by control type, names it, assigns index and encoded private value, and registers it.

`snd_sbmixer_new()` chooses a mixer profile based on `chip->hardware`. `snd_sbmixer_init()` resets the mixer, writes profile-specific mute/default values, registers all controls, adds the component string, and fills `card->mixername`. SB1.x has no mixer. ALS4000 receives both a subset of SB16 controls and ALS4000-specific controls.

For PM, profile-specific register lists define which registers are saved into `chip->saved_regs`. Resume writes those values back in the same order.

## State and Persistence
Mixer state is hardware-register backed. The only in-memory snapshot is `chip->saved_regs` during suspend. ALSA control values read current hardware state rather than cached software state. There is no persistent storage across driver unload.

## Dependencies and Integration Points
The file depends on ALSA control APIs, SB register constants and macros, and `struct snd_sb` locks. It is called by SB card front ends after DSP creation and by PM callbacks in card-level drivers.

## Risks and Edge Cases
Control encoding in `private_value` is dense; incorrect macros can silently target wrong bits. ALS4000 comments note uncertain 3D control semantics. `snd_sbmixer_init()` resets the mixer every time a profile is initialized, which matters for ALS4000 where two initializations run. Suspend save arrays must fit `chip->saved_regs`.

## Test Signals
Inspect `amixer controls` for the expected profile; verify put/get round trips for single, double, enum, and input-route controls; confirm default values mute expected channels; verify SB1.x creates no mixer; and suspend/resume restores changed mixer values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sb_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sbawe.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/sbawe.c

## Purpose
This is a tiny build wrapper that compiles `sb16.c` in Sound Blaster AWE mode. It defines `SNDRV_SBAWE` and includes the SB16 card-level implementation.

## Important APIs, Types, and Functions
No functions are defined directly. Defining `SNDRV_SBAWE` changes compile-time branches in `sb16.c`: module description and driver names become AWE-specific, the PnP ID table uses AWE32/AWE64 IDs, optional EMU8000 support is enabled when the sequencer is configured, and AWE port/seq parameter arrays are available.

## Control Flow
At compile time the preprocessor expands `sb16.c` with AWE paths enabled. Runtime probe flow is therefore the same as `sb16.c`, with extra PnP wavetable logical-device handling and `snd_emu8000_new()` when an AWE port is present.

## State and Persistence
All state belongs to the included SB16 implementation. No additional persistent state is introduced here.

## Dependencies and Integration Points
This wrapper depends entirely on `sb16.c` and the build system selecting the AWE module target.

## Risks and Edge Cases
Because this includes a C file rather than sharing a library symbol, compile-time macro branches must remain side-effect free for both SB16 and SBAWE builds. Any change to `sb16.c` must be considered in both modes.

## Test Signals
Build the AWE module, verify module metadata names AWE, ensure AWE PnP IDs bind, and confirm EMU8000 creation when the wavetable port is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/sbawe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sc6000.c -->
# sources/distributed-fs/ceph-client/sound/isa/sc6000.c

## Purpose
This file implements the ISA driver for Gallant SC-6000, Audio Excel DSP 16, Zoltrix AV302, SC-6600, and SC-7000 cards. These cards have a proprietary CompuMedia DSP/config interface and expose an AD1848/CS4231-compatible WSS codec for PCM.

## Important APIs, Types, and Functions
Module parameters configure base `port`, WSS `mss_port`, optional `mpu_port`, audio `irq`, `mpu_irq`, `dma`, and `joystick`. `struct snd_sc6000` stores mapped DSP and MSS IO windows, WSS chip pointer, computed config bytes, hardware config bytes, and `old_dsp` detection. Hardware helpers translate IRQ/DMA values into soft config bytes, read/write the DSP, reset it, write hardware config, set board config, initialize MSS mode, and detect old DSP behavior. Main probe is `__snd_sc6000_probe()` wrapped by `snd_sc6000_probe()`.

## Control Flow
Match validates explicit base and MSS ports, allowed port values, IRQ/DMA mappings, and optional MPU settings. Probe creates the ALSA card, auto-finds IRQ/DMA if requested, reserves and maps the DSP and MSS IO regions, computes config bytes with `sc6000_prepare_board()`, resets and identifies the DSP by copyright/version, detects old DSP behavior, writes hardware config when supported, programs soft config twice around resets, initializes Microsoft Sound System mode, and writes the MSS config byte.

After board setup, the driver creates a WSS device at `mss_port + 4`, adds PCM and mixer, renames AUX mixer controls to FM/CD, optionally adds OPL3 at 0x388, optionally creates an MPU-401 UART, fills card strings, and registers the card. Free disables board config by writing zero. Resume resets and reprograms the board before resuming the WSS chip.

## State and Persistence
State is per-card private data plus module parameters. Hardware config bytes are recomputed and retained in memory for resume. Mixer and PCM state are delegated to the WSS core. No persistent storage exists.

## Dependencies and Integration Points
The file uses Linux ISA, IO mapping, legacy IRQ/DMA finders, ALSA core, WSS codec APIs, OPL3, MPU-401, and ALSA control rename APIs.

## Risks and Edge Cases
The driver is based on OSS behavior and undocumented command magic. DSP reads use timeouts and partial string reads because command result length is not self-describing. WSS creation uses `mss_port + 4`, reflecting the codec window offset. Mixer renaming assumes default WSS control names exist. Incorrect config encoding can disable joystick, MPU, IDE, or WSS paths.

## Test Signals
Probe should log model and DSP version, create WSS PCM/mixer at the expected port, rename Aux controls to FM/CD, optionally expose OPL3 and MPU-401, disable board config on free, and reinitialize after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sc6000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sscape.c -->
# sources/distributed-fs/ceph-client/sound/isa/sscape.c

## Purpose
This is the ALSA ISA and ISA PnP driver for ENSONIQ SoundScape cards, including MediaFX/SoundFX, SoundScape, SoundScape PnP, and SoundScape VIVO variants. It detects and configures the SoundScape board, uploads MIDI firmware over ISA DMA for non-VIVO boards, creates the AD1845/WSS PCM and mixer path, and creates MPU-401 MIDI support.

## Important APIs, Types, and Functions
`struct soundscape` stores lock, IO bases, IRQs, DMA channels, IC type, card type, resources, WSS chip, MIDI volume, joystick and firmware/MIDI enable state, and device pointer. Low-level helpers access ODIE/OPUS registers and host-mode ports: `sscape_write_unsafe()`, `sscape_read_unsafe()`, `set_host_mode_unsafe()`, `set_midi_mode_unsafe()`, `host_read_ctrl_unsafe()`, and `host_write_ctrl_unsafe()`. Firmware upload is handled by `upload_dma_data()`, `sscape_upload_bootblock()`, and `sscape_upload_microcode()`. Board setup uses `detect_sscape()` and `sscape_configure_board()`. Device creation is split into `create_ad1845()`, `create_mpu401()`, and `create_sscape()`.

## Control Flow
Legacy ISA probing requires explicit IO, IRQ, MPU IRQ, and DMA. PnP probing reads resources from the logical device, distinguishes VIVO from PnP by ID, derives WSS and second DMA settings, and stores them in `struct soundscape`. `create_sscape()` reserves IO, requests DMA, initializes the lock, detects the hardware with port/register tests, configures DMA/IRQ/codec routing and joystick state, creates the AD1845/WSS PCM/mixer/timer path, and then handles MIDI firmware for non-VIVO cards.

Firmware upload allocates a 32 KiB DMA buffer, resets the board, configures channel A DMA, copies firmware in chunks, starts board DMA, waits for completion, boots the board, and waits for OBP and host startup acknowledgements. The bootblock firmware `scope.cod` returns a microcode version, and the driver then loads `sndscape.coN`. After firmware upload, it creates MPU-401 rawmidi, initializes MIDI volume state, and restores MIDI host commands.

## State and Persistence
Runtime state includes stored module/PnP settings, board type, IC type, WSS chip state, MIDI volume, and whether MIDI firmware was enabled. Suspend saves WSS state. Resume reconfigures board registers, reloads MIDI firmware when enabled, restores MIDI state, resumes WSS, and marks power D0. No disk persistence exists, but firmware files are required at probe and resume.

## Dependencies and Integration Points
The file depends on Linux ISA, PnP, firmware loading, IO ports, ISA DMA, ALSA WSS, MPU-401, and ALSA control APIs. It registers both an ISA driver and, when configured, a PnP card driver. It declares firmware dependencies for `scope.cod` and `sndscape.co0` through `sndscape.co4`.

## Risks and Edge Cases
The driver contains many undocumented magic values and comments noting behavior inferred from OSS code. Firmware upload uses DMA and mixed spinlock/sleeping waits, so lock boundaries are critical. MIDI is deliberately disabled if MPU-401 verification fails to avoid hangs. Resume can partially fail MIDI restore but still resumes WSS. PnP and ISA registration share module state flags.

## Test Signals
Probe should identify the card type and IO/IRQ/DMA settings, create WSS PCM/mixer/timer, create the MIDI mixer control for non-VIVO cards, load `scope.cod` and a matching `sndscape.coN`, expose MPU-401 only after firmware, reject MIDI open when firmware verification fails, and reload firmware plus restore MIDI volume after suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sscape.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/wavefront/Makefile

## Purpose
This Makefile defines the ALSA WaveFront module composition for Turtle Beach Maui/Tropez/Tropez+ support.

## Important APIs, Types, and Functions
It sets `snd-wavefront-y := wavefront.o wavefront_fx.o wavefront_synth.o wavefront_midi.o`, meaning those four objects are linked into one module. It adds `snd-wavefront.o` to the build when `CONFIG_SND_WAVEFRONT` is enabled.

## Control Flow
There is no runtime control flow. Build-time flow is Kbuild object aggregation: the module entry points are in `wavefront.c`, while FX, synth, and MIDI support are linked into the same object.

## State and Persistence
No runtime state. Build state is controlled by `CONFIG_SND_WAVEFRONT`.

## Dependencies and Integration Points
The file integrates this directory with the parent ALSA ISA Kbuild. It requires all four object files to compile cleanly because they become a single module.

## Risks and Edge Cases
Adding or removing WaveFront support files requires updating this list. Since `wavefront_synth.o` is linked but not part of this work item, behavior referenced by `wavefront.c` depends on that sibling object.

## Test Signals
With `CONFIG_SND_WAVEFRONT=m`, Kbuild should produce `snd-wavefront.ko` containing symbols from card, FX, synth, and MIDI implementation files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront.c -->
# sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront.c

## Purpose
This is the card-level driver for Turtle Beach WaveFront family cards, including Maui, Tropez, and Tropez+. It combines CS4232/WSS PCM, OPL3, optional CS4232 MPU-401, ICS2115 wavetable synth hwdep, WaveFront internal/external MIDI, and optional YSS225 FX processor support.

## Important APIs, Types, and Functions
Module parameters configure CS4232 PCM port/IRQ/DMA, CS4232 MPU port/IRQ, ICS2115 port/IRQ, FM port, PnP enablement, and whether to use the hidden CS4232 MIDI interface. PnP resource import is in `snd_wavefront_pnp()`. ICS2115 IRQ dispatch is `snd_wavefront_ics2115_interrupt()`. Constructors include `snd_wavefront_new_synth()`, `snd_wavefront_new_fx()`, `snd_wavefront_new_midi()`, `snd_wavefront_card_new()`, and common `snd_wavefront_probe()`.

## Control Flow
PnP detection activates the CS4232 WSS logical device, optional CS4232 MPU logical device, and ICS2115 synth logical device, then copies resources into module arrays. Common probe creates WSS PCM and timer, optional OPL3 hwdep, reserves the ICS2115 IO window, requests the ICS2115 IRQ, initializes wavefront interrupt and MIDI locks/waitqueue, detects and starts the WaveFront synth, creates the synth hwdep, creates WSS mixer, optionally creates CS4232 MPU, creates internal and external ICS2115 rawmidi devices, creates the FX hwdep if the synth detection reported FX support, fills card strings, and registers the card.

The shared ICS2115 interrupt handler routes interrupts to MIDI or internal synth logic based on `acard->wavefront.interrupts_are_midi`. The first WaveFront MIDI device initialization sets the MIDI base and starts the ICS2115 UART/virtual MIDI mode; subsequent internal/external rawmidi devices share that initialized interface.

## State and Persistence
State is stored in `snd_wavefront_card_t` and nested `snd_wavefront_t`: IRQ, base ports, resources, interrupt mode, waitqueue, MIDI locks/state, and FX initialized flag. Module parameter arrays hold configured or PnP-discovered resources. There is no suspend/resume implementation in this file, and no persistent storage.

## Dependencies and Integration Points
This file depends on Linux ISA, PnP, IRQ, ALSA core, WSS, OPL3, MPU-401, and WaveFront synth/FX/MIDI APIs declared in `sound/snd_wavefront.h` and implemented by sibling object files.

## Risks and Edge Cases
The ISA path requires explicit CS4232 and ICS2115 ports. PnP device comments indicate some logical devices are ignored. The `snd_wavefront_new_midi()` helper uses a static `first` flag, which can be problematic for multiple cards because it is module-global rather than per-card. Suspend/resume is marked FIXME, so state and firmware may not survive power transitions.

## Test Signals
Successful probe should show WSS PCM/timer/mixer, optional OPL3, synth hwdep with ICS2115 interface, two WaveFront MIDI rawmidi devices, optional CS4232 MPU, and optional YSS225 FX hwdep on Tropez+. Verify ICS2115 IRQs switch to MIDI after MIDI start and that internal/external rawmidi devices both transmit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_fx.c -->
# sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_fx.c

## Purpose
This file implements low-level support for the YSS225 FX processor present on Tropez+ WaveFront cards. It detects the FX processor, initializes it from firmware register data, exposes a hwdep ioctl interface, supports mute, and writes YSS225 DSP memory pages.

## Important APIs, Types, and Functions
Public functions are `snd_wavefront_fx_detect()`, `snd_wavefront_fx_open()`, `snd_wavefront_fx_release()`, `snd_wavefront_fx_ioctl()`, and `snd_wavefront_fx_start()`. Internal helpers are `wavefront_fx_idle()`, `wavefront_fx_mute()`, and `wavefront_fx_memset()`. Firmware dependency is `yamaha/yss225_registers.bin`.

## Control Flow
Detection checks whether the FX status port appears idle; on non-FX cards it reports likely Maui/Tropez and returns failure. `snd_wavefront_fx_start()` exits early if already initialized, requests firmware, then treats the firmware as port-offset/value pairs. Offsets 8 through 15 are written relative to the WaveFront base; `WAIT_IDLE` entries wait for the FX processor to become idle; any invalid offset aborts initialization. On success it sets `fx_initialized`.

The hwdep open/release pins and unpins the module. The ioctl reads a `wavefront_fx_info` request from user space. `WFFX_MUTE` calls mute but currently returns `-EIO`. `WFFX_MEMSET` validates count and range, copies user page data for multi-word writes, then writes one or many 16-bit values to page/address registers using load-control bits and idle waits.

## State and Persistence
State is in the shared `snd_wavefront_t`: FX port addresses and `fx_initialized`. The FX processor itself holds loaded register/memory state. There is no persistent storage, and no suspend/resume reload path in the card driver.

## Dependencies and Integration Points
This file integrates with the card-level WaveFront hwdep constructor in `wavefront.c`, the Linux firmware loader, ALSA hwdep APIs, and WaveFront type definitions.

## Risks and Edge Cases
The initialization firmware format is simple but trusted for valid register offsets; invalid data aborts. `WFFX_MUTE` returning `-EIO` after doing the operation looks suspicious and may confuse userspace. Some paths return `-1` instead of standard errno. The single-word memset path logs with `dev_err`, producing noisy error-level output for a normal operation.

## Test Signals
On Tropez+, FX detection should pass, firmware load should set `fx_initialized`, YSS225 hwdep should appear, `WFFX_MEMSET` should update valid page/address ranges and reject invalid ones, and non-FX cards should not create the FX device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_fx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_midi.c -->
# sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_midi.c

## Purpose
This file implements the low-level MIDI support for the WaveFront ICS2115 interface. It provides rawmidi callbacks for separate internal and external MIDI buses and supports Turtle Beach "Virtual MIDI" mode, where switch bytes route traffic between the synth bus and external MIDI bus.

## Important APIs, Types, and Functions
Public symbols are the rawmidi ops `snd_wavefront_midi_output` and `snd_wavefront_midi_input`, plus `snd_wavefront_midi_interrupt()`, `snd_wavefront_midi_enable_virtual()`, `snd_wavefront_midi_disable_virtual()`, and `snd_wavefront_midi_start()`. Helpers wrap MPU status/data ports: `wf_mpu_status()`, `input_avail()`, `output_ready()`, `read_data()`, `write_data()`, and `get_wavefront_midi()`. Output scheduling uses `snd_wavefront_midi_output_write()` and a timer callback.

## Control Flow
Rawmidi open records input or output substreams by `internal_mpu` or `external_mpu` ID stored in `rmidi->private_data`. Trigger callbacks toggle mode bits under the MIDI virtual lock. Output trigger starts a one-jiffy timer if needed and immediately drains bytes. The drain function first flushes the currently selected output bus, then optionally sends `WF_INTERNAL_SWITCH` or `WF_EXTERNAL_SWITCH` before writing data for the other bus. It filters switch bytes from user data while in virtual mode so users cannot accidentally alter routing.

The interrupt handler checks for incoming data. If no input is pending it treats the interrupt as an opportunity to write output. When bytes arrive, virtual mode switch bytes update the selected input substream; normal bytes are delivered through `snd_rawmidi_receive()` only when that bus has input trigger enabled. It then attempts output write again.

`snd_wavefront_midi_start()` waits for the ICS2115 MPU to be ready, marks future ICS2115 interrupts as MIDI-owned, sends UART mode command, waits for MPU ACK, enables external MIDI-to-synth routing, forces virtual MIDI off then on to resynchronize switch bytes, and updates software virtual-mode state.

## State and Persistence
State lives in `snd_wavefront_midi_t`: base ports, command/status/data ports, input and output substream arrays, mode bits, `output_mpu`, `input_mpu`, virtual-mode flag, timer count, timer object, timer card, and locks. No persistent storage exists.

## Dependencies and Integration Points
This file depends on ALSA rawmidi, WaveFront synth command helpers (`snd_wavefront_cmd()`), ICS2115 interrupt routing in `wavefront.c`, and constants from `sound/snd_wavefront.h`.

## Risks and Edge Cases
Several comments identify hard timing loops that should not exist in modern kernel code. The interrupt handler has static `substream` and `mpu` variables, which are shared across all cards and can be wrong for multi-card systems. In virtual input mode, the `WF_INTERNAL_SWITCH` case assigns `substream_output[internal_mpu]` instead of the input substream, which looks like a potential routing bug. Timer lifetime depends on `istimer` reference counting and close/trigger interactions.

## Test Signals
Verify UART mode ACK during MIDI start, internal and external rawmidi devices open independently, virtual mode emits and consumes switch bytes correctly, user-supplied switch bytes are filtered in virtual output mode, incoming bytes route to the triggered input substream, output timer drains queued bytes, and MIDI interrupt routing remains stable under simultaneous internal/external traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/wavefront/wavefront_midi.c -->
