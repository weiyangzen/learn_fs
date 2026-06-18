# sources/distributed-fs/ceph-client/sound/synth/emux/emux_proc.c

## Purpose
This file provides a `/proc/asound` text diagnostics entry for EMUX wavetable synthesizers when ALSA procfs support is enabled.

## Important APIs, types, and functions
`snd_emux_proc_info_read` prints device name, sequencer ports, use count, max and allocated voices, memory size/availability/block count, and soundfont/instrument/sample lock counters. `snd_emux_proc_init` creates `wavetableD<device>` under the card proc root. `snd_emux_proc_free` removes it.

## Control flow
Registration calls `snd_emux_proc_init`, which creates a card entry and attaches the read callback. Reads take `emu->register_mutex`, then `emu->sflist->presets_mutex` while printing soundfont counters. Teardown frees the entry and clears `emu->proc`.

## State and persistence behavior
The proc entry stores only a pointer to `emu`; it exposes live in-memory counters and does not persist settings.

## Dependencies and integration points
It depends on ALSA info/proc APIs, EMUX core state, util memory headers, and soundfont list internals. `emux_voice.h` supplies inline no-op replacements when procfs is disabled.

## Risks and edge cases
Read-side locking must stay consistent with sequencer and soundfont mutation paths to avoid stale pointers. The optional debug block is disabled but references voice internals useful during troubleshooting. Entry creation failure is silently ignored.

## Test signals
Verify `wavetableD*` appears when procfs is enabled, prints correct port and memory counters after soundfont loads/unloads, handles no `memhdr` or no `sflist`, and disappears after EMUX free.
