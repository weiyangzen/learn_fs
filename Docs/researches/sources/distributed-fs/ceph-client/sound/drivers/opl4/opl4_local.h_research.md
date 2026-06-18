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
