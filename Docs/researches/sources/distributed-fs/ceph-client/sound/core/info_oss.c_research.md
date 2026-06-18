# sources/distributed-fs/ceph-client/sound/core/info_oss.c

## Purpose
`info_oss.c` implements OSS-compatible `/proc/asound/oss/sndstat` reporting. It stores per-card OSS device description strings and prints an emulated legacy sound-driver status page.

## Important APIs, Types, and Functions
`snd_oss_info_register()` registers or clears a string for a device class and card number. `snd_sndstat_show_strings()` prints all registered strings for one OSS category. `snd_sndstat_proc_read()` builds the sndstat text, including kernel identity, installed driver text, card config, and Audio/Synth/Midi/Timers/Mixers sections. `snd_info_minor_register()` creates the `sndstat` proc entry below `snd_oss_root`.

## Control Flow and State
Global state is `snd_sndstat_strings[SNDRV_CARDS][SNDRV_OSS_INFO_DEV_COUNT]`, protected by the `strings` mutex. Registering with a non-NULL string duplicates it; registering NULL frees the existing string and clears the slot. The proc reader takes the mutex while enumerating each category.

## Dependencies and Integration Points
It depends on the proc info framework from `info.c`, OSS emulation device categories, `snd_card_info_read_oss()` from card init, and `init_utsname()` for kernel details. OSS mixer and other OSS layers call `snd_oss_info_register()` to populate categories.

## Risks and Test Signals
Risks include stale strings if device unregister paths fail to clear entries and memory leaks on replacement if overwrite semantics change. Tests should register/unregister strings for each category, read `/proc/asound/oss/sndstat`, verify empty categories print the disabled message, and run concurrent register/read operations.
