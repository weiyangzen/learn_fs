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
