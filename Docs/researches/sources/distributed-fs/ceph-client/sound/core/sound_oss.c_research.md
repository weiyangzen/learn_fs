# sources/distributed-fs/ceph-client/sound/core/sound_oss.c

## Purpose
`sound_oss.c` implements the ALSA OSS-compatibility minor registry. It maps OSS device types to legacy OSS minor numbers, registers/unregisters sound special devices, exposes lookup with card references, and provides optional proc reporting.

## Important APIs, Types, and Functions
- `snd_lookup_oss_minor_data()` returns registered OSS private data for a minor/type and takes a card device reference.
- `snd_oss_kernel_minor()` maps OSS device type/card/device to the legacy minor number.
- `snd_register_oss_device()` allocates a `snd_minor`, stores it in `snd_oss_minors[]`, registers the primary sound special device, and for PCM/MIDI registers alternate OSS aliases.
- `snd_unregister_oss_device()` clears primary/alias registry entries, unregisters sound special devices, and frees the metadata.
- `snd_minor_info_oss_init()` creates optional proc reporting of OSS devices.

## Control Flow
Registration first computes the kernel minor, silently ignores cards outside the OSS device-card range, allocates metadata, stores the primary minor under `sound_oss_mutex`, determines any alias minor (`audio`, `dmmidi`, or `dmmidi1`), and calls `register_sound_special_device()` for primary and alias. On registration failure it unregisters any successful special devices, clears the registry, and frees metadata.

Unregistration computes the same primary and alias minors, clears registry entries while holding the mutex, then calls `unregister_sound_special()` outside the mutex because unregister can trigger card release paths.

## State and Persistence
Global runtime state is `snd_oss_minors[256]` protected by `sound_oss_mutex`. Entries may be shared by a primary minor and alias minor. No persistent storage exists.

## Dependencies and Integration Points
Depends on ALSA core/card structures, OSS minor macros, Linux sound special device registration, and proc info. OSS PCM, mixer, MIDI, sequencer, and sndstat compatibility layers register through this file.

## Risks
Primary and alias minors share one `snd_minor`, so cleanup must avoid double-free. The registry entry is assigned before special-device registration completes, so failure paths must clear it. Lookup returns private data with an implied card reference contract. Minor mapping is ABI-sensitive.

## Test Signals
Test every OSS device type mapping, invalid card/device rejection, alias registration for PCM/MIDI, partial registration failure unwind, unregister outside-lock behavior, lookup type filtering/refcounting, high card number silent ignore, and proc devices output.
