<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/snd_wavefront.h -->
# sources/distributed-fs/ceph-client/include/sound/snd_wavefront.h

## Purpose
`snd_wavefront.h` defines the internal ALSA driver interface for Turtle Beach WaveFront synthesizer cards, including MIDI, synth, FX processor, PnP, I/O port, and interrupt state.

## Important APIs, types, and functions
Types include `snd_wavefront_midi_t`, `snd_wavefront_t`, and `snd_wavefront_card_t`. `struct _snd_wavefront_midi` tracks MPU base, virtual/timer state, selected MPUs, modes, rawmidi substreams, timer, card pointer, and spinlocks. `struct _snd_wavefront` stores IRQ/base/resources, port offset macros, interrupt counters, debug flags, memory/version/status arrays, FX and MIDI flags, locks, waitqueue, MIDI state, and card pointer. Public declarations cover MIDI ops, virtual MIDI enable/disable, interrupt/start routines, device detect/start/command, synth hwdep ioctls/open/release, and FX detect/start/ioctls/open/release.

## Control flow
The driver detects hardware resources, starts the WaveFront synth, services interrupts, routes internal/external MPU MIDI through rawmidi ops, optionally uses timer-driven virtual MIDI, and exposes synth/FX hwdep ioctl interfaces for user control.

## State and persistence behavior
Driver state mirrors hardware resources and firmware/synthesis status at runtime: program/patch/sample slot states, installed RAM, version bytes, interrupt counters, MIDI substreams, and FX initialization. Hardware state may persist while powered, but the header defines no durable storage.

## Dependencies and integration points
It depends on ALSA MPU401, hwdep, rawmidi, WaveFront UAPI definitions, optional PnP, timers, spinlocks, waitqueues, and I/O port resources.

## Risks and test signals
Risks include raw I/O port alias mistakes, interrupt/timer races, virtual MIDI locking errors, stale sample/program status, PnP resource mismatch, and undocumented FX port behavior. Test signals include card detection, interrupt command completion, internal/external MPU I/O, virtual MIDI enable/disable, synth hwdep commands, FX detection, sample/program slot operations, and open/release concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/snd_wavefront.h -->
