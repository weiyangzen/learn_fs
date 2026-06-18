# sources/distributed-fs/ceph-client/sound/firewire/motu/motu.c

## Purpose

This is the MOTU FireWire ALSA driver entry point. It matches supported MOTU models, allocates and names ALSA cards, wires together transaction, streaming, proc, PCM, MIDI, hwdep, and DSP parser components, and registers the FireWire driver.

## Important APIs, types, and functions

`motu_probe()` is the central constructor. `motu_card_free()` is the card private cleanup hook. `motu_bus_update()` re-registers async message addresses after bus reset. `motu_id_table[]` maps MOTU version IDs to `snd_motu_spec` objects. `snd_motu_clock_rates[]` is the shared six-entry rate table used across protocol and PCM logic.

## Control flow

Probe creates the card, initializes `struct snd_motu`, names the card from config ROM data, registers async transactions, initializes duplex streams, creates proc/PCM/MIDI/hwdep devices, optionally creates register-DSP or command-DSP parser state, and finally registers the card. Any failure releases the card, which invokes cleanup. Remove only calls `snd_card_free()` so ALSA character devices can drain before final teardown.

## State and persistence behavior

The file establishes long-lived `struct snd_motu` state: unit reference, spec pointer, locks, wait queue, card pointer, and model flags. It does not persist data outside kernel runtime.

## Dependencies and integration points

It binds Linux FireWire core to ALSA. It depends on all MOTU submodules declared in `motu.h`, and the device ID table selects protocol behavior indirectly via model specs.

## Risks and test signals

Risks include probe-order cleanup regressions, missing MIDI creation for flag combinations, and model ID/spec mismatches. Test signals are probe/remove for every ID, failed intermediate allocations, bus reset, card naming from config ROM, and module load/unload.
