# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle_mixer.c

## Purpose
`msnd_pinnacle_mixer.c` implements ALSA mixer controls for MultiSound Pinnacle and shared Classic-compatible controls. It maps ALSA kcontrols to mixer-level arrays in `struct snd_msnd`, writes scaled values into DSP SMA fields, and sends auxiliary DSP commands for hardware potentiometer and capture-source changes.

## Important APIs, Types, and Functions
- Public functions: `snd_msndmix_new`, `snd_msndmix_setup`, and `snd_msndmix_force_recsrc`.
- Capture selector callbacks: `snd_msndmix_info_mux`, `snd_msndmix_get_mux`, `snd_msndmix_put_mux`, and `snd_msndmix_set_mux`.
- Volume callbacks: `snd_msndmix_volume_info`, `snd_msndmix_volume_get`, `snd_msndmix_volume_put`, and internal `snd_msndmix_set`.
- Update macros `update_volm`, `update_potm`, and `update_pot` write SMA fields and send `HDEX_AUX_REQ` when hardware pots must be applied.

## Control Flow
`snd_msndmix_new` initializes `mixer_lock`, sets the mixer name, and registers master, PCM, aux, line, mic, monitor, and capture-source controls. `put` handlers convert user 0-100 values to 8-bit pot and 16-bit DSP levels, update cached `left_levels`/`right_levels`, and write the appropriate SMA fields. Master changes cascade to PCM, monitor, aux, and synth values because several controls are master-scaled. Capture-source changes send an auxiliary request selecting analog, MASS/synth, or SPDIF if digital input exists.

## State and Persistence
Mixer state is cached in `left_levels`, `right_levels`, and `recsrc` in `struct snd_msnd`. `snd_msndmix_setup` replays cached state into the SMA after DSP initialization or reset. There is no disk persistence.

## Dependencies and Integration Points
The mixer depends on ALSA control APIs, common DSP command helpers from `msnd.c`, state from `msnd.h`, and Pinnacle SMA offsets from `msnd_pinnacle.h`. It is called by board attach and reset/resume code.

## Risks and Test Signals
Risks include modulo-based volume normalization (`% 101`) silently wrapping invalid userspace values, Classic paths rejecting mic volume but still registering the mic control, and capture-source values depending on `F_HAVEDIGITAL`. Test signals include mixer control enumeration with and without digital daughterboard, ALSA control change return values, correct master-scaled volume writes after reset, and hardware response to line/mic/aux pot commands.
