# subset-b-006358 Research

Grouped research for the listed ALSA sound driver files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mtpav.c -->
# sources/distributed-fs/ceph-client/sound/drivers/mtpav.c

## Purpose
Implements the ALSA raw-MIDI driver for the MOTU MidiTimePiece AV on a legacy PC parallel port. The driver exposes hardware, remote, computer, ADAT, and broadcast MIDI substreams while translating ALSA rawmidi traffic into the MTPAV parallel-port byte protocol.

## Important APIs, Types, And Functions
`struct mtpav` owns the ALSA card, I/O resource, IRQ, rawmidi device, timer, spinlock, selected input/output port state, and `struct mtpav_port` array. `translate_subdevice_to_hwport()` and `translate_hwport_to_subdevice()` map ALSA substream numbers to MTP hardware port selectors. `snd_mtpav_getreg()`, `snd_mtpav_mputreg()`, `snd_mtpav_wait_rfdhi()`, and `snd_mtpav_send_byte()` are the low-level parallel register helpers. Rawmidi callbacks are provided through `snd_mtpav_input` and `snd_mtpav_output`.

## Control Flow
Module init registers a platform driver and synthetic platform device. Probe creates a managed ALSA card, initializes locks and timers, creates rawmidi substreams, requests the fixed I/O region and IRQ, scans ports into smart routing mode, then registers the card. Output trigger writes immediately and uses `timer_list` polling to continue draining rawmidi output buffers. Input open enables parallel-port interrupts; the IRQ handler reads nibble-encoded bytes, recognizes `0xf5` port-change messages, and delivers data to the currently selected rawmidi input substream.

## State And Persistence
State is runtime-only: open/trigger bits per port, running status per output port, IRQ/timer reference counts, current MTP input/output selectors, and ALSA rawmidi buffers. Module parameters persist only as load-time configuration (`index`, `id`, `port`, `irq`, `hwports`).

## Dependencies And Integration
Depends on ISA-style I/O (`inb`/`outb`), Linux timers/IRQs, platform devices, and ALSA core/rawmidi. It integrates with user space through ALSA rawmidi subdevices and card naming.

## Risks And Test Signals
The driver touches legacy hardware directly and has busy-wait loops without hard failure reporting if the device is absent or slow. The output trigger path appears suspicious because it increments the timer reference only when `MTPAV_MODE_OUTPUT_TRIGGERED` is already set, which can prevent timer startup on the first trigger. Useful tests are hardware probe/load, rawmidi substream enumeration, interrupt-driven input, multi-port output routing, close/unload timer cleanup, and invalid `hwports` clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mtpav.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mts64.c -->
# sources/distributed-fs/ceph-client/sound/drivers/mts64.c

## Purpose
Provides an ALSA raw-MIDI and control driver for the ESI Miditerminal 4140 parallel-port MIDI interface. It exposes four MIDI outputs, five inputs including an SMPTE timecode input, and ALSA controls for the device's SMPTE generator.

## Important APIs, Types, And Functions
`struct mts64` stores the ALSA card, rawmidi, parport device, open count, selected MIDI ports, input trigger bits, SMPTE switch/time/fps state, and input substream pointers. Hardware helpers include `mts64_write_command()`, `mts64_write_data()`, `mts64_read()`, `mts64_read_char()`, `mts64_probe()`, `mts64_device_init()`, `mts64_smpte_start()`, and `mts64_smpte_stop()`. ALSA controls are created by `snd_mts64_ctl_create()`, and rawmidi is created by `snd_mts64_rawmidi_create()`.

## Control Flow
Module init registers a platform driver and a parport driver. The parport match callback creates a platform device carrying the discovered parport. Platform probe claims the parport exclusively, creates an ALSA card and `struct mts64`, probes the hardware command echo, creates rawmidi and SMPTE controls, initializes the device, and registers the card. Rawmidi open enters communication mode on first open and close leaves it on last close. Output trigger drains pending rawmidi bytes to the selected output port. The parport IRQ reads a status/data word; status values either update the current input port or deliver MIDI data to the triggered input substream.

## State And Persistence
No disk persistence exists. Runtime state includes parport claim ownership, open count, current input/output port selectors, triggered input masks, SMPTE settings, and ALSA control values. Module arrays (`index`, `id`, `enable`) configure card instances at load time.

## Dependencies And Integration
Uses Linux parport registration and callbacks, platform devices, ALSA core/rawmidi/control APIs, spinlocks, and device-managed card cleanup through `snd_card_free()`.

## Risks And Test Signals
The driver relies on precise parallel-port protocol timing and exclusive parport access. SMPTE time setters store values but do not automatically restart hardware when playback is already enabled, so user-visible behavior depends on toggling the switch. `snd_mts64_rawmidi_output_trigger()` ignores the `up` argument and drains whenever called. Test signals include device detection, parport claim/release, rawmidi loop traffic, SMPTE control read/write behavior, IRQ delivery on all mapped ports, and cleanup on failed probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/mts64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/Makefile -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/Makefile

## Purpose
Defines the kernel build composition for the ALSA OPL3 FM support modules. It separates the common OPL3 library from the optional sequencer synth layer and conditionally includes OSS sequencer emulation.

## Important APIs, Types, And Functions
The build targets are `snd-opl3-lib-y := opl3_lib.o opl3_synth.o` and `snd-opl3-synth-y := opl3_seq.o opl3_midi.o opl3_drums.o`, with `opl3_oss.o` appended when `CONFIG_SND_SEQUENCER_OSS` is enabled.

## Control Flow
Kbuild links `snd-opl3-lib.o` for both `CONFIG_SND_OPL3_LIB` and `CONFIG_SND_OPL4_LIB`, reflecting OPL4's reuse of the FM OPL3 core. `CONFIG_SND_OPL3_LIB_SEQ` builds the sequencer-facing synth module.

## State And Persistence
The file is declarative build metadata and has no runtime state.

## Dependencies And Integration
Integrates with ALSA Kconfig symbols for OPL3, OPL4, sequencer, and OSS emulation. The OPL4 dependency on `snd-opl3-lib.o` is an important cross-folder integration point.

## Risks And Test Signals
Misconfigured object grouping would break symbol availability for drivers that create OPL3 or OPL4 devices. Build tests across `CONFIG_SND_OPL3_LIB`, `CONFIG_SND_OPL4_LIB`, `CONFIG_SND_OPL3_LIB_SEQ`, and `CONFIG_SND_SEQUENCER_OSS` are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_drums.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_drums.c

## Purpose
Implements the optional internal OPL2/OPL3 percussion mode used by the OPL3 sequencer synth when `use_internal_drums` is enabled. It maps GM drum notes to the five hardware percussion bits and programs fixed bass, hi-hat, snare, tom, and cymbal voices.

## Important APIs, Types, And Functions
`snd_opl3_drum_table` maps notes 35-81 to OPL3 percussion bit masks. `struct snd_opl3_drum_voice` and `struct snd_opl3_drum_note` describe fixed register settings. `snd_opl3_load_drums()` initializes the reserved percussion voices, and `snd_opl3_drum_switch()` turns a note on/off and updates per-hit volume/pan.

## Control Flow
Sequencer setup reserves voices 6-8, calls `snd_opl3_load_drums()`, enables percussion mode in `opl3->drum_reg`, and routes drum note-on/off events through `snd_opl3_drum_switch()`. On note-on, the code selects the relevant predescribed drum voice, adjusts level and stereo bits from MIDI velocity/pan, sets the percussion bit, and writes `OPL3_REG_PERCUSSION`. On note-off it clears that bit.

## State And Persistence
State lives in OPL3 hardware registers and `opl3->drum_reg`. There is no independent persistence; percussion setup is recreated on each synth subscription.

## Dependencies And Integration
Depends on `snd_opl3_regmap`, `snd_opl3_calc_volume()`, OPL3 register constants from `<sound/opl3.h>`, and the command callback stored in `struct snd_opl3`.

## Risks And Test Signals
The mapping compresses many GM notes onto five shared hardware percussion bits, so overlapping notes of the same hardware drum can cut each other off. Tests should cover notes below/above 35-81, velocity-to-level behavior, pan changes, percussion mode disabled, and interactions with melodic voices when internal drums reserve voices 6-8.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_drums.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_lib.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_lib.c

## Purpose
Provides the common ALSA OPL2/OPL3/OPL4 FM chip library: low-level register writes, chip detection, hardware timer exposure, codec object lifetime, and hwdep/sequencer device registration.

## Important APIs, Types, And Functions
Exports `snd_opl3_new()`, `snd_opl3_init()`, `snd_opl3_create()`, `snd_opl3_timer_new()`, `snd_opl3_hwdep_new()`, and `snd_opl3_interrupt()`. Internal helpers include `snd_opl2_command()`, `snd_opl3_command()`, `snd_opl3_detect()`, and timer start/stop routines for FM timer 1 and timer 2.

## Control Flow
Callers create an OPL3 object with ports and hardware type. The library optionally reserves I/O regions, chooses an OPL2-style or OPL3-style command function, detects chip type through the FM timer status sequence when auto-detecting, initializes OPL3 mode for capable chips, and registers an ALSA codec device. `snd_opl3_hwdep_new()` exposes a direct FM hwdep device and, when sequencer support is enabled, creates an OPL3 sequencer device carrying the `struct snd_opl3 *`. Interrupts inspect the FM status register and notify ALSA timers.

## State And Persistence
Runtime state includes port resources, hardware type, max voice count, timer enable bits, locks, hwdep pointer, and optional sequencer device pointer. There is no persistent storage.

## Dependencies And Integration
Uses raw I/O port access, ALSA card/device/hwdep/timer/sequencer APIs, and OPL register constants. OPL4 creation reuses this library for the FM half, passing integrated ports to avoid duplicate resource ownership.

## Risks And Test Signals
Detection depends on timer behavior that some integrated hardware does not implement, hence special hardware cases bypass detection. Resource-release ordering is important because failures call `snd_device_free()`. Tests should build with/without sequencer and OSS, probe OPL2/OPL3/OPL4 hardware types, exercise hwdep ioctls, verify timer interrupts, and test duplicate I/O region rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_midi.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_midi.c

## Purpose
Converts ALSA MIDI channel events into OPL2/OPL3 FM register programming for the sequencer and OSS synth paths. It handles voice allocation, patch lookup, pitch/volume math, note lifecycle, and controller effects.

## Important APIs, Types, And Functions
Public MIDI callbacks are `snd_opl3_note_on()`, `snd_opl3_note_off()`, `snd_opl3_key_press()`, `snd_opl3_terminate_note()`, `snd_opl3_control()`, `snd_opl3_nrpn()`, and `snd_opl3_sysex()`. Shared helpers include `snd_opl3_calc_volume()` and `snd_opl3_timer_func()`. The file also contains logarithmic volume and pitch tables, `opl3_get_voice()`, `snd_opl3_kill_voice()`, and pitch update helpers.

## Control Flow
For note-on, the code chooses bank/program from sequencer mode, drum status, or OSS mode, finds a loaded patch, determines 2-op versus 4-op capability, allocates a voice, clears any previous key-on state, sets the OPL3 4-op connection register if needed, writes operator registers, computes f-number/block, keys the voice on, schedules fixed-duration note-off if requested, and records voice bookkeeping. Note-off scans voices matching channel/note in sequencer mode or remaps the OSS voice and clears key-on. Controller events update vibrato/tremolo depth or recompute pitch bend.

## State And Persistence
State is in `opl3->voices[]`, `use_time`, `connection_reg`, `drum_reg`, system timer fields, channel state, and loaded patches managed elsewhere. It is runtime-only and reset during synth setup/cleanup.

## Dependencies And Integration
Depends on `opl3_synth.c` patch storage, `opl3_drums.c` for internal percussion, ALSA MIDI channel processing, and the low-level `opl3->command()` callback.

## Risks And Test Signals
Voice stealing is heuristic and must avoid corrupting paired 4-op voices. Extra-program recursion is intentionally limited but still complicates note-off grouping. Fixed-duration notes depend on jiffies equality in the timer callback, which is timing-sensitive. Test signals include 2-op/4-op patches, pitch bend, pan, volume/expression, percussion, extra program patches, OSS voice remapping, and voice exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_oss.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_oss.c

## Purpose
Provides OSS sequencer emulation glue for the OPL3 FM synth. It registers the FM synth with ALSA's OSS sequencer layer, creates an OSS-facing sequencer port, maps OSS patch loading into the shared OPL3 patch table, and manages open/close lifecycle.

## Important APIs, Types, And Functions
Exports `snd_opl3_init_seq_oss()` and `snd_opl3_free_seq_oss()`. Static callbacks include `snd_opl3_open_seq_oss()`, `snd_opl3_close_seq_oss()`, `snd_opl3_ioctl_seq_oss()`, `snd_opl3_load_patch_seq_oss()`, `snd_opl3_reset_seq_oss()`, and `snd_opl3_oss_event_input()`.

## Control Flow
Initialization allocates an `SNDRV_SEQ_DEV_ID_OSS` device, fills `snd_seq_oss_reg` with FM synth type/subtype/voice count, creates a write-only sequencer port, and registers callbacks. Open calls `snd_opl3_synth_setup()`, attaches the OSS channel set address to the OSS argument, increments the module reference, and selects synth mode. Events are processed through `snd_midi_process_event()` unless they are raw OSS event wrappers. Patch loading copies an OSS `sbi_instrument`, validates channel/program range, and calls `snd_opl3_load_patch()` in bank 127.

## State And Persistence
State is runtime-only: OSS sequencer device pointer, OSS MIDI channel set, synth mode, module reference, and the shared patch table. Closing releases synth setup and module ownership.

## Dependencies And Integration
Depends on `CONFIG_SND_SEQUENCER_OSS`, ALSA sequencer OSS callbacks, shared OPL3 MIDI ops, and patch APIs from `opl3_synth.c`.

## Risks And Test Signals
`snd_opl3_init_seq_oss()` appears to register the OSS synth only when `snd_opl3_oss_create_port()` returns nonzero, which is counterintuitive and should be verified against expected ALSA device registration behavior. Test signals include OSS synth enumeration, patch loading for FM and OPL3 formats, ioctl behavior, open exclusivity with hwdep/sequencer users, and module reference release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_oss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_seq.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_seq.c

## Purpose
Registers the native ALSA sequencer client and port for OPL2/OPL3/OPL4 FM synthesis and coordinates synth setup/teardown around port subscriptions.

## Important APIs, Types, And Functions
Exports usage helpers declared in `opl3_voice.h`: `snd_opl3_synth_use_inc()`, `snd_opl3_synth_use_dec()`, `snd_opl3_synth_setup()`, and `snd_opl3_synth_cleanup()`. The sequencer driver callbacks are `snd_opl3_seq_probe()` and `snd_opl3_seq_remove()`. MIDI operations are gathered in the exported `opl3_ops`.

## Control Flow
The OPL3 hwdep registration creates a sequencer device, and this module's `module_snd_seq_driver()` probes it. Probe initializes voice locking, creates a kernel sequencer client, allocates a 16-channel MIDI channel set, attaches a write/subscription-capable synth port, sets up the fixed-duration system timer, and optionally initializes OSS emulation. Port use takes the hwdep open mutex, resets the chip, initializes voice bookkeeping, optionally reserves internal drum voices, increments module references for non-system senders, and switches to sequencer mode. Unuse cleans up the timer and hardware state and releases references.

## State And Persistence
Runtime state includes `seq_client`, `chset`, voice states, `use_time`, `connection_reg`, drum mode, system timer status, and hwdep `used` count. No persistent data is stored.

## Dependencies And Integration
Depends on ALSA sequencer device registration, MIDI channel helpers, OPL3 low-level reset/command functions, `opl3_midi.c` callbacks, optional `opl3_drums.c`, and optional OSS emulation.

## Risks And Test Signals
Subscription setup enforces exclusivity through hwdep usage, so races around open/unuse and wakeups are important. Internal drum mode reduces melodic voices by marking voices 6-8 unavailable. Test signals include sequencer client/port creation, subscribe/unsubscribe, module reference accounting, MIDI event synthesis, internal drums on/off, and removal while ports are unused.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_synth.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_synth.c

## Purpose
Implements the direct FM synthesis hwdep interface and shared OPL3 patch management. It accepts DM/FM ioctls to reset, play notes, set operator parameters, configure rhythm/mode/4-op connections, and load SBI-style patches through hwdep writes.

## Important APIs, Types, And Functions
Exports `snd_opl3_load_patch()`, `snd_opl3_find_patch()`, `snd_opl3_clear_patches()`, and `snd_opl3_reset()`. Hwdep entry points are `snd_opl3_open()`, `snd_opl3_ioctl()`, `snd_opl3_write()`, and `snd_opl3_release()`. Internal helpers include `snd_opl3_play_note()`, `snd_opl3_set_voice()`, `snd_opl3_set_params()`, `snd_opl3_set_mode()`, and `snd_opl3_set_connection()`.

## Control Flow
Userspace hwdep ioctls copy DM/FM structs from user memory, validate voice/operator/mode ranges, and emit OPL register writes through `opl3->command()`. `snd_opl3_write()` parses consecutive SBI records, detects 2-op or 4-op signatures, and inserts them into the hash table. Reset mutes operator levels, clears key-on registers, returns to melodic OPL2 mode, and clears rhythm state. Release resets the chip.

## State And Persistence
Patch data is held in an in-memory hash table on `struct snd_opl3`; it is freed by `snd_opl3_clear_patches()` and not persisted. Hardware mode, rhythm flag, max voices, and connection state are runtime register-backed state.

## Dependencies And Integration
Depends on ALSA hwdep ABI types from `<sound/asound_fm.h>`, user copy helpers, OPL3 register maps, and sequencer support for patch loading when enabled.

## Risks And Test Signals
Direct register programming is exposed to user space, so bounds checks on voice/operator indices are critical; this file uses `array_index_nospec()` in the operator path. Patch hash collisions are simple linked lists. Tests should cover ioctl ABI compatibility, invalid voice/operator/mode inputs, SBI patch loading, reset after release, OPL2 versus OPL3 mode limits, and patch cleanup on device free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_voice.h -->
# sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_voice.h

## Purpose
Provides local cross-file declarations for the OPL3 FM synth implementation. It binds the sequencer, MIDI event, internal drum, OSS emulation, register map, and shared MIDI operation table together without exposing those internals outside the OPL3 driver directory.

## Important APIs, Types, And Functions
Declares synth lifecycle functions from `opl3_seq.c`, MIDI callbacks and helpers from `opl3_midi.c`, drum helpers from `opl3_drums.c`, optional OSS initialization/free hooks from `opl3_oss.c`, and external data `snd_opl3_regmap`, `use_internal_drums`, and `opl3_ops`.

## Control Flow
The header has no executable control flow. Its preprocessor branch maps OSS functions to no-ops when `CONFIG_SND_SEQUENCER_OSS` is disabled, allowing core sequencer code to call the hooks unconditionally.

## State And Persistence
No state is stored in the header. It declares shared runtime state owned by other compilation units.

## Dependencies And Integration
Includes `<sound/opl3.h>` for `struct snd_opl3`, MIDI channel types, and OPL constants. It is the internal integration surface for the OPL3 sequencer object built by the Makefile.

## Risks And Test Signals
Prototype drift would break cross-file builds. The no-op OSS macros are important for configuration coverage. Build tests with OSS enabled and disabled are the main signal; sparse/compiler warnings catch signature mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl3/opl3_voice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/Makefile -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/Makefile

## Purpose
Defines Kbuild objects for the ALSA OPL4 wavetable driver, split into a common device/mixer/proc library and an optional sequencer synth module with static YRW801 instrument data.

## Important APIs, Types, And Functions
`snd-opl4-lib-y` includes `opl4_lib.o` and `opl4_mixer.o`, with `opl4_proc.o` conditional on `CONFIG_SND_PROC_FS`. `snd-opl4-synth-y` includes `opl4_seq.o`, `opl4_synth.o`, and `yrw801.o`.

## Control Flow
`CONFIG_SND_OPL4_LIB` builds `snd-opl4-lib.o`; `CONFIG_SND_OPL4_LIB_SEQ` builds the sequencer synth object. The OPL4 library also causes the OPL3 library to be built via the OPL3 Makefile.

## State And Persistence
The file is declarative build state only.

## Dependencies And Integration
Integrates OPL4 with ALSA procfs, sequencer support, and the OPL3 FM core. The object split mirrors runtime layering: low-level PCM/mixer/proc support separate from MIDI wavetable synthesis.

## Risks And Test Signals
Configuration-specific build failures are the main risk, especially procfs off and sequencer off combinations. Kconfig matrix builds are the relevant tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_lib.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_lib.c

## Purpose
Implements low-level access, detection, object creation, and ALSA device registration for Yamaha OPL4 chips. It also creates the paired OPL3 FM device because OPL4 includes an FM-compatible portion.

## Important APIs, Types, And Functions
Exports `snd_opl4_write()`, `snd_opl4_read()`, `snd_opl4_read_memory()`, `snd_opl4_write_memory()`, and `snd_opl4_create()`. Internal helpers include `snd_opl4_wait()`, `snd_opl4_enable_opl4()`, `snd_opl4_detect()`, and optional sequencer device creation.

## Control Flow
`snd_opl4_create()` allocates `struct snd_opl4`, reserves FM and PCM/MIX I/O regions, initializes locks, enables OPL4 mode through the FM register block, detects device ID and mixer readback behavior, registers an ALSA codec device, creates an integrated OPL3 object on the FM ports, re-enables OPL4 after OPL3 initialization, then creates mixer/proc and sequencer devices when configured. Memory read/write temporarily sets memory-access mode, loads the 24-bit address registers, streams bytes through the memory data port, then restores the configuration register.

## State And Persistence
Runtime state includes I/O resources, hardware variant, locks, proc entry, sequencer device pointer, and the paired OPL3 object returned to callers. OPL4 external ROM/SRAM contents are hardware state; the driver does not persist copies.

## Dependencies And Integration
Depends on ALSA device registration, OPL3 library creation, raw I/O port access, resource management, OPL4 mixer/proc helpers, and optional sequencer device creation.

## Risks And Test Signals
The wait loop is bounded but silently continues after timeout, so absent or wedged hardware can produce misleading follow-up I/O. Detection writes mixer registers and memory configuration, making restore behavior important. Tests should cover OPL4 versus OPL4-ML detection, resource conflicts, OPL3 pairing, memory read/write through procfs, mixer creation, and sequencer device creation only for supported variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_local.h -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_local.h

## Purpose
Defines the private OPL4 driver contract: register numbers, bit masks, wavetable data structures, voice state, the `struct snd_opl4` device object, and cross-file function prototypes.

## Important APIs, Types, And Functions
Important types are `struct opl4_sound`, `struct opl4_region`, `struct opl4_region_ptr`, `struct opl4_voice`, and `struct snd_opl4`. It also declares low-level memory/register helpers, mixer/proc creation, sequencer globals, synth callbacks, `snd_yrw801_detect()`, and `snd_yrw801_regions[]`.

## Control Flow
No executable flow exists. Conditional procfs declarations become no-op inline functions when `CONFIG_SND_PROC_FS` is disabled, preserving call sites in `opl4_lib.c`.

## State And Persistence
The header defines runtime state layout: I/O ports/resources, hardware type, register lock, optional proc memory access flag, access mutex, sequencer usage flag, channel set, 24 voices, and off/on voice lists. Persistent storage is not implemented.

## Dependencies And Integration
Includes `<sound/opl4.h>` and references OPL3 hardware constants. It is the central integration point for the OPL4 library, mixer, proc, sequencer, synth, and YRW801 table.

## Risks And Test Signals
Because this header encodes register masks and struct layout used across files, incorrect constants can corrupt hardware programming globally. Build coverage with procfs/sequencer toggles and runtime smoke tests for mixer, memory, and note playback are the useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_mixer.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_mixer.c

## Purpose
Adds ALSA mixer controls for OPL4 FM and wavetable playback volume. The controls manipulate the OPL4 mix-control registers with stereo left/right attenuation values.

## Important APIs, Types, And Functions
`snd_opl4_ctl_info()`, `snd_opl4_ctl_get()`, and `snd_opl4_ctl_put()` implement a two-channel integer control ranging from 0 to 7. `snd_opl4_controls[]` defines `"FM Playback Volume"` and `"Wavetable Playback Volume"`. `snd_opl4_create_mixer()` appends `,OPL4` to the card mixer name and registers both controls.

## Control Flow
On get, the driver reads the register under `reg_lock`, inverts the hardware attenuation values (`7 - value`) into user-facing volume values, and returns left/right values. On put, it converts user values back to hardware attenuation, writes the register, and reports whether the value changed.

## State And Persistence
State is stored in OPL4 mixer registers. ALSA control values are not persisted by the driver; userspace mixers may save/restore them externally.

## Dependencies And Integration
Uses ALSA control APIs and the low-level `snd_opl4_read()`/`snd_opl4_write()` helpers from `opl4_lib.c`.

## Risks And Test Signals
Values are masked to three bits, so out-of-range user values are wrapped rather than rejected. `strcat(card->mixername, ",OPL4")` assumes enough space in the ALSA mixer name buffer. Tests should cover get/put round trips, left/right inversion, invalid high values, and mixer registration during OPL4 probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_proc.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_proc.c

## Purpose
Exposes OPL4 memory through an ALSA proc binary entry named `opl4-mem`. On classic OPL4 it allows read/write access to external ROM/SRAM space; on OPL4-ML it exposes read-only-size semantics for internal ROM.

## Important APIs, Types, And Functions
`snd_opl4_create_proc()` creates the proc entry, sets size and content type, and assigns `snd_opl4_mem_proc_ops`. `snd_opl4_mem_proc_open()` and release serialize access with `memory_access`; read/write handlers allocate temporary buffers, copy to/from user, and call `snd_opl4_read_memory()` or `snd_opl4_write_memory()`. `snd_opl4_free_proc()` removes the entry.

## Control Flow
Open takes `access_mutex` and rejects concurrent access with `-EBUSY`. Read allocates a kernel buffer of requested count, reads device memory at the file offset, copies it to user space, and frees the buffer. Write copies user bytes into a temporary buffer, writes them to device memory, and frees it.

## State And Persistence
Runtime state includes the proc entry pointer and `memory_access` count. The only persistent-like state is actual OPL4 external memory if writable hardware is present; the driver does not validate memory content.

## Dependencies And Integration
Depends on `CONFIG_SND_PROC_FS`, ALSA info/proc APIs, vmalloc/vfree, user copy helpers, and OPL4 memory helpers.

## Risks And Test Signals
Large reads/writes vmalloc the full request size and do not clamp offsets/counts against entry size in the file code itself. Write access to external SRAM can alter hardware memory. Tests should cover concurrent open rejection, read/write at boundary offsets, OPL4 versus OPL4-ML entry sizing and mode bits, and cleanup on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_seq.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_seq.c

## Purpose
Registers the ALSA sequencer client and MIDI-compatible port for OPL4 wavetable synthesis. It validates the YRW801 ROM, owns port subscription lifecycle, and routes sequencer events to the OPL4 synth callbacks.

## Important APIs, Types, And Functions
Module parameter `volume_boost` adjusts synthesized volume in `opl4_synth.c`. Core callbacks are `snd_opl4_seq_use()`, `snd_opl4_seq_unuse()`, `snd_opl4_seq_event_input()`, `snd_opl4_seq_probe()`, and `snd_opl4_seq_remove()`. `opl4_ops` maps MIDI events to `snd_opl4_note_on/off`, `snd_opl4_terminate_note`, `snd_opl4_control`, and `snd_opl4_sysex`.

## Control Flow
The OPL4 library creates a sequencer device. Probe verifies the YRW801 ROM signature, allocates a 16-channel MIDI channel set, creates a kernel sequencer client, and attaches a write/subscription-capable 24-voice port. Subscription use takes `access_mutex`, enforces single active use, increments the module reference for non-system senders, and resets the synth. Unuse shuts voices down, decrements usage, and releases the module reference.

## State And Persistence
State includes `used`, `seq_client`, `chset`, channel state, and the OPL4 voice lists reset by the synth layer. No file persistence exists.

## Dependencies And Integration
Depends on ALSA sequencer and MIDI channel helpers, `yrw801.c` region data, synth callbacks in `opl4_synth.c`, and `struct snd_opl4` from `opl4_local.h`.

## Risks And Test Signals
YRW801 detection gates the entire sequencer interface, so cards without the expected ROM signature will expose library/mixer pieces but no wavetable port. Single-use locking must release module references correctly on errors. Tests should cover ROM detect failure/success, port creation/removal, subscribe/unsubscribe, volume_boost changes, and event-to-note playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_synth.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_synth.c

## Purpose
Implements OPL4 wavetable MIDI synthesis: voice allocation, tone selection from YRW801 regions, volume/pan/pitch/vibrato calculations, register programming, note on/off, controllers, and GS master volume sysex handling.

## Important APIs, Types, And Functions
Exports `snd_opl4_synth_reset()`, `snd_opl4_synth_shutdown()`, `snd_opl4_note_on()`, `snd_opl4_note_off()`, `snd_opl4_terminate_note()`, `snd_opl4_control()`, and `snd_opl4_sysex()`. Important helpers include `snd_opl4_update_volume()`, `snd_opl4_update_pan()`, `snd_opl4_update_vibrato_depth()`, `snd_opl4_update_pitch()`, `snd_opl4_get_voice()`, and `snd_opl4_wait_for_wave_headers()`.

## Control Flow
Reset damps all 24 voices, initializes off/on voice lists, and clears MIDI channels. Note-on selects program or drum region, finds up to two matching key regions, steals from the oldest off voice or oldest on voice, writes tone number registers to trigger header load, sets pan/pitch/initial level while loading, waits for header completion, writes envelope/LFO/tremolo parameters, then sets key-on. Note-off clears key-on and moves voices to the off list; terminate also sets damp. Controllers update active voices by channel for modwheel/vibrato depth, main volume, pan, expression, and pitch bend. Parsed GS master volume sysex updates all active voice volumes.

## State And Persistence
Voice state is held in `opl4->voices[]`, `off_voices`, `on_voices`, each voice's channel/note/velocity/sound pointers, cached register fields, and MIDI channel data. The YRW801 region table is static read-only data.

## Dependencies And Integration
Depends on OPL4 register helpers, YRW801 regions, ALSA MIDI channel semantics, `volume_boost` from `opl4_seq.c`, and OPL4 register constants from `opl4_local.h`.

## Risks And Test Signals
Voice stealing can cut active notes under high polyphony. No voice is played if a note has no matching region; no explicit error is reported. Pitch and volume math clamp values but depends on static lookup tables. Tests should cover melodic and drum programs, two-region layered sounds, voice exhaustion, controllers on active notes, pitch bend and tuning, sysex master volume, and shutdown/reset muting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/yrw801.c -->
# sources/distributed-fs/ceph-client/sound/drivers/opl4/yrw801.c

## Purpose
Contains detection logic and static General MIDI instrument metadata for Yamaha YRW801 wavetable ROMs used with OPL4. The synth layer uses this table to translate MIDI programs/drum notes into OPL4 tone numbers and register parameters.

## Important APIs, Types, And Functions
`snd_yrw801_detect()` reads ROM offsets `0x001200` and `0x1ffffe` to validate the `"CopyrightYAMAHA"` signature and ROM version. `snd_yrw801_regions[0x81]` exports 128 melodic program region sets plus a drum region set. Each `struct opl4_region` maps a key range to `struct opl4_sound` fields such as tone, pitch offset, key scaling, pan, vibrato, attenuation, volume factor, and envelope/LFO/tremolo registers.

## Control Flow
The OPL4 sequencer probe calls `snd_yrw801_detect()` before creating the port. During note-on, `opl4_synth.c` indexes `snd_yrw801_regions` by program or `0x80` for drums, scans regions whose key range contains the note, and uses up to two matching `opl4_sound` entries for layered playback.

## State And Persistence
The region table is static read-only kernel data. Detection reads hardware ROM but does not cache any parsed dynamic metadata beyond returning success/failure.

## Dependencies And Integration
Depends on OPL4 memory reads from `opl4_lib.c` and structures from `opl4_local.h`. It is tightly coupled to `snd_opl4_note_on()`'s table indexing and two-voice layering behavior.

## Risks And Test Signals
The static table assumes practical OPL4 deployments use YRW801; other ROM/SRAM sound sets are not dynamically supported. A bad signature disables the sequencer path. Tests should cover ROM detection, table bounds for programs 0-127 and drums, key-range matching, layered regions, and representative instruments across low/mid/high notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/opl4/yrw801.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcmtest.c -->
# sources/distributed-fs/ceph-client/sound/drivers/pcmtest.c

## Purpose
Implements a virtual ALSA PCM driver for PCM middle-layer testing and fuzzing. It simulates playback/capture, supports interleaved and non-interleaved buffers, fills capture data with random or pattern data, checks playback data against per-channel patterns, injects callback errors/delays, and exposes debugfs status/pattern controls.

## Important APIs, Types, And Functions
`struct pcmtst` owns the ALSA card, PCM, and platform device. `struct pcmtst_buf_iter` tracks simulated DMA position, period position, bytes per tick, format/access properties, corruption state, and a timer. PCM callbacks include open/close/trigger/prepare/hw_params/hw_free/ioctl/sync_stop/pointer. Debugfs helpers manage pattern buffers and expose `pc_test`, `ioctl_test`, `fill_patternN`, and `fill_patternN_len`.

## Control Flow
Module init allocates pattern buffers, creates debugfs entries, registers a platform device, and registers the platform driver. Probe creates a managed ALSA card and an 8-playback/8-capture PCM with managed DMA buffers. Open allocates the iterator and timer. Prepare computes sample bytes, period bytes, interleaving mode, channel block size, and per-tick transfer bytes. Trigger start resets the iterator and starts the timer; each timer tick checks playback data, fills capture data, advances period state, calls `snd_pcm_period_elapsed()` at period boundaries, and rearms itself with optional delay. Close stops the timer and stores playback test result.

## State And Persistence
State is runtime-only: module parameters, debugfs flags, pattern buffers, simulated DMA position, timer state, and corruption result. Debugfs writes can change in-memory pattern data until module unload.

## Dependencies And Integration
Depends on ALSA PCM/platform/card APIs, Linux timers, DMA buffer helpers, debugfs, random bytes, and selftests in the ALSA test suite.

## Risks And Test Signals
Debugfs pattern writes silently crop beyond 4096 bytes and pattern reads can expose padded buffer contents. Timer callbacks and trigger/sync_stop paths must avoid sleeping in trigger context while still synchronizing on close. Tests should cover all injected error parameters, reset ioctl flagging, playback pattern validation, capture patterns/random mode, interleaved/non-interleaved access, pause/resume, period elapsed timing, and module cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcmtest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/Makefile -->
# sources/distributed-fs/ceph-client/sound/drivers/pcsp/Makefile

## Purpose
Defines the PC speaker ALSA module composition. It links platform/card setup, PCM playback engine, mixer controls, and input beeper support into `snd-pcsp.o`.

## Important APIs, Types, And Functions
`snd-pcsp-y := pcsp.o pcsp_lib.o pcsp_mixer.o pcsp_input.o` and `obj-$(CONFIG_SND_PCSP) += snd-pcsp.o` are the complete build declarations.

## Control Flow
Kbuild compiles the four object files when `CONFIG_SND_PCSP` is enabled and links them into one module.

## State And Persistence
No runtime state exists in this file.

## Dependencies And Integration
The object list references `pcsp_mixer.c`, which is outside the requested source list but is required for `snd_pcsp_new_mixer()` used by `pcsp.c`.

## Risks And Test Signals
Omitting any object breaks link-time symbols for PCM, mixer, or input support. Build tests with `CONFIG_SND_PCSP=m/y` are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.c -->
# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.c

## Purpose
Provides the platform-driver entry point for the ALSA PC speaker driver. It creates the global `pcsp_chip`, registers the input beeper device, optionally creates PCM playback, creates mixer controls, and stops the speaker on suspend/shutdown/free.

## Important APIs, Types, And Functions
Defines module parameters `index`, `id`, `enable`, and `nopcm`, plus global `struct snd_pcsp pcsp_chip`. Important functions are `snd_pcsp_create()`, `snd_card_pcsp_probe()`, `alsa_card_pcsp_init()`, `pcsp_probe()`, `pcsp_stop_beep()`, `pcsp_suspend()`, `pcsp_shutdown()`, `pcsp_init()`, and `pcsp_exit()`.

## Control Flow
Module init registers a platform driver named `pcspkr` unless disabled. Probe first registers the input beeper device, then creates an ALSA card and initializes timer parameters based on hrtimer resolution and CPU loop calibration. If timer resolution is insufficient, it forces `nopcm` mode. Otherwise it creates the PCM device via `snd_pcsp_new_pcm()`, always creates mixer controls, names/registers the card, and records chip driver data. Suspend, shutdown, and card free all stop PCM/beep output.

## State And Persistence
`pcsp_chip` is a single global runtime object containing the card, input device, hrtimer, playback pointers, port state, enable flags, treble settings, and PCM state. There is no persistence beyond module parameters.

## Dependencies And Integration
Depends on platform device alias `platform:pcspkr`, ALSA core/PCM, hrtimer setup, input beeper initialization, mixer creation, and PC speaker PIT helpers.

## Risks And Test Signals
The design is single-device only and rejects nonzero device numbers. PCM availability depends on hrtimer resolution and can silently degrade to beep-only mode with warnings. Tests should cover module enable/nopcm combinations, platform probe, debug-pagealloc warning, suspend/shutdown stop behavior, and card registration with and without PCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.h -->
# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.h

## Purpose
Defines shared constants, timing calculations, state, and cross-file prototypes for the PC speaker ALSA driver.

## Important APIs, Types, And Functions
Macros derive PIT dividers, sample rates, hrtimer periods, buffer limits, and pointer increments: `DIV_18KHZ`, `PCSP_DEFAULT_SRATE`, `PCSP_RATE()`, `PCSP_PERIOD_NS()`, `PCSP_BUFFER_SIZE`, and related limits. `struct snd_pcsp` stores ALSA card/PCM/input pointers, hrtimer, port metadata, playback substream, sample format state, playback/period pointers, timer-active flag, PIT port latch state, and mixer flags. It declares `pcsp_chip`, `pcsp_do_timer()`, `pcsp_sync_stop()`, `snd_pcsp_new_pcm()`, and `snd_pcsp_new_mixer()`.

## Control Flow
The header has no executable flow but its macros determine runtime hrtimer cadence and PCM hardware constraints used by `pcsp.c` and `pcsp_lib.c`.

## State And Persistence
No state is stored in the header, but it defines the global runtime object layout. The driver persists nothing to disk.

## Dependencies And Integration
Includes hrtimer, i8253, and timex kernel headers and is included by platform, PCM, mixer, and input implementation files.

## Risks And Test Signals
Timing macros depend on integer arithmetic and PIT constants; mistakes affect sample rate, hrtimer period, and buffer pointer advancement. Build-time tests catch prototype drift; runtime tests should verify reported PCM rate, period constraints, and pointer movement at default treble settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.c -->
# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.c

## Purpose
Implements the input-subsystem beeper side of the PC speaker driver. It accepts `EV_SND` bell/tone events and programs PIT counter 2 directly unless PCM playback is active or beep output is muted.

## Important APIs, Types, And Functions
`pcspkr_do_sound()` performs the PIT and port `0x61` programming under `i8253_lock`. `pcspkr_stop_sound()` disables counter 2. `pcspkr_input_event()` validates sound events and converts tone frequency to PIT count. `pcspkr_input_init()` allocates/registers an input device with `SND_BELL` and `SND_TONE` capabilities.

## Control Flow
Platform probe calls `pcspkr_input_init()`. When userspace emits a bell or tone event, `pcspkr_input_event()` ignores it if PCM hrtimer playback is active or the mixer `pcspkr` flag is off. Bell events with nonzero value become 1000 Hz. Tone values between 20 and 32767 Hz are converted to PIT divisor counts; invalid or zero values stop sound. The low-level helper writes the PIT mode and divisor then enables/disables bits in port `0x61`.

## State And Persistence
The input device is devm-managed. Audible state is hardware PIT/speaker state plus `pcsp_chip.timer_active` and `pcsp_chip.pcspkr`; there is no persistence.

## Dependencies And Integration
Depends on Linux input APIs, ISA port I/O, global `pcsp_chip`, and `i8253_lock`. It integrates with mixer controls through `pcsp_chip.pcspkr` and with PCM playback through `timer_active` exclusion.

## Risks And Test Signals
Direct PIT programming can conflict with PCM playback if gating fails, hence the active-timer check is critical. Tests should cover bell/tone on/off, invalid event rejection, mute behavior, PCM-active suppression, suspend/shutdown stop, and input device registration metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.h -->
# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.h

## Purpose
Declares the small public interface between PC speaker platform setup and the input beeper implementation.

## Important APIs, Types, And Functions
Declares `pcspkr_input_init(struct input_dev **rdev, struct device *dev)` and `pcspkr_stop_sound(void)`.

## Control Flow
No executable flow exists. `pcsp.c` calls `pcspkr_input_init()` during platform probe and `pcspkr_stop_sound()` during shutdown/suspend/free paths.

## State And Persistence
No state is defined. State is owned by `pcsp_input.c` and the shared `pcsp_chip`.

## Dependencies And Integration
Relies on forward-visible `struct input_dev` and `struct device` declarations from includers. It is the boundary that lets `pcsp.c` stop beeps without knowing PIT programming details.

## Risks And Test Signals
Prototype drift would break the PC speaker module build. Build tests and suspend/shutdown smoke tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_input.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_lib.c -->
# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_lib.c

## Purpose
Implements the PCM playback engine for the PC speaker driver. It converts mono PCM sample bytes into PIT counter 2 pulses using an hrtimer, advances ALSA buffer pointers, and reports period elapsed through a workqueue.

## Important APIs, Types, And Functions
Exports `pcsp_do_timer()`, `pcsp_sync_stop()`, and `snd_pcsp_new_pcm()`. Internal helpers include `pcsp_timer_update()`, `pcsp_pointer_update()`, `pcsp_start_playing()`, `pcsp_stop_playing()`, and PCM callbacks for open/close/hw_params/hw_free/prepare/trigger/pointer. Module parameter `nforce_wa` changes PIT programming for an NForce chipset workaround.

## Control Flow
PCM open rejects active playback, sets runtime hardware constraints, and records the substream. Prepare stops any existing timer, resets pointers, and records sample size/sign. Trigger start programs PIT mode, stores port `0x61` state, marks timer active, and starts the hrtimer. Each timer callback writes a pulse width derived from the current sample, optionally handles the NForce half-cycle workaround, updates playback and period pointers, queues `snd_pcm_period_elapsed()` on `system_highpri_wq`, and rearms itself. Stop clears `timer_active` and restores PIT mode/port bits. Sync stop cancels the hrtimer and pending work.

## State And Persistence
State is in global `pcsp_chip`: playback substream pointer, format size/sign, playback/period pointers, timer-active flag, half-cycle state, nanosecond remainder, and saved port value. There is no persistence.

## Dependencies And Integration
Depends on ALSA PCM helpers, hrtimers, workqueues, PIT `i8253_lock`, raw I/O ports, and shared constants/state from `pcsp.h`. Mixer controls can toggle `chip->enable`, affecting whether pulses are emitted.

## Risks And Test Signals
The callback path touches hardware from hrtimer context and defers ALSA period notifications to avoid long IRQ work. Pointer math assumes mono and fixed rate constraints. Tests should cover start/stop races, close/hw_free synchronization, S16 and U8 formats, period elapsed timing, pointer wraparound, `nforce_wa`, mixer enable gating, and suppression of input beeps while PCM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_lib.c -->
