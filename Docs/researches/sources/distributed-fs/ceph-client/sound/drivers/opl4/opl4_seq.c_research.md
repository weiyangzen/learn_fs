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
