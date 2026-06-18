# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw.c

## Purpose

This is the OXFW970/971 FireWire driver entry point. It matches device IDs, names ALSA cards, detects hardware/firmware quirks, discovers streams, initializes ALSA devices, and handles bus reset/remove.

## Important APIs, types, and functions

`oxfw_probe()` constructs `struct snd_oxfw` and orchestrates submodule setup. `detect_quirks()` applies model-specific behavior for Griffin, LaCie, Stanton, Apogee, TASCAM FireOne, Loud/Mackie, and Oxford/Miglia devices. `name_card()` reads CSR strings and OXFW firmware ID. `oxfw_id_table[]` encodes supported devices and aliases.

## Control flow

Probe filters generic Loud matches by model string, allocates the card, initializes locks/wait queues, names the card, applies special Miglia quirks, discovers stream formats, applies further quirks, initializes streams and PCM/proc/MIDI/hwdep if audio I/O exists, and registers the card. Bus reset resets FCP, updates streams under the mutex, and re-registers SCS.1x async address when needed. Remove frees the ALSA card.

## State and persistence behavior

This file initializes long-lived `struct snd_oxfw` state: unit, card, quirks, stream-format caches, MIDI port counts, and optional `spec` private data for speakers or SCS.1x. It does not persist outside kernel runtime.

## Dependencies and integration points

It integrates FireWire driver core, ALSA card lifecycle, OXFW stream/PCM/MIDI/hwdep/proc modules, speaker controls, and SCS.1x transactions. Kbuild composes these pieces via the OXFW Makefile.

## Risks and test signals

Risks include quirk mis-detection, probe cleanup ordering, stream discovery failures preventing useful control-only devices, and generic Loud matching false positives. Tests should probe every ID path, firmware-id quirk behavior, bus reset, remove during active streams, and module aliases.
