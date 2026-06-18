# sources/distributed-fs/ceph-client/sound/firewire/tascam/tascam.c

## Purpose

This is the TASCAM FireWire driver entry point. It identifies supported models, initializes ALSA card state, connects transaction/stream/proc/PCM/MIDI/hwdep components, and registers the FireWire driver.

## Important APIs, types, and functions

`model_specs[]` defines FW-1884, FW-1082, and FW-1804 capabilities. `identify_model()` extracts an eight-byte model string from config ROM words and binds the matching spec. `snd_tscm_probe()` builds the card. `snd_tscm_update()` handles bus reset by re-registering async transactions and aborting streams. The ID table matches TASCAM vendor/specifier/version values.

## Control flow

Probe creates the ALSA card, initializes locks and wait queue, identifies the model, registers async MIDI transactions, initializes duplex streams, creates proc/PCM/MIDI/hwdep devices, and registers the card. Failures free the card and trigger cleanup. Remove blocks through `snd_card_free()` until ALSA users are gone.

## State and persistence behavior

This file initializes persistent runtime state in `struct snd_tscm`: card/unit refs, locks, model spec, transaction state, streams, and wait queue. It has no on-disk persistence.

## Dependencies and integration points

It binds Linux FireWire core to ALSA and all TASCAM submodules. Config ROM model parsing is central because the ID table alone does not distinguish all capabilities.

## Risks and test signals

Risks include fragile config-ROM string offsets, unsupported FE-8 behavior, probe cleanup order, and model spec mismatches. Tests should cover all three supported models, short config ROM rejection, bus reset, failed submodule creation, and module load/unload.
