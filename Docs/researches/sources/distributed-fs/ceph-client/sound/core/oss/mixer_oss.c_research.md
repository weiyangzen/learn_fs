# sources/distributed-fs/ceph-client/sound/core/oss/mixer_oss.c

## Purpose
`mixer_oss.c` implements OSS mixer emulation on top of ALSA mixer controls. It registers legacy OSS mixer devices, answers OSS mixer ioctls, maps ALSA kcontrols into OSS mixer slots, exposes a proc remapping interface, and integrates with card registration/free notifications.

## Important APIs, Types, and Functions
File operations are `snd_mixer_oss_open()`, `snd_mixer_oss_release()`, and `snd_mixer_oss_ioctl()`. Core ioctl helpers include `snd_mixer_oss_info()`, `caps`, `devmask`, `stereodevs`, `recmask`, `get_recsrc`, `set_recsrc`, `get_volume`, and `set_volume`. Mapping state uses `struct slot`, `snd_mixer_oss_slot`, present-bit constants, and `snd_mixer_oss_assign_table`. ALSA-control mapping helpers include `snd_mixer_oss_build_test_all()`, `snd_mixer_oss_build_input()`, `snd_mixer_oss_get_volume1*()`, `snd_mixer_oss_put_volume1*()`, and capture-source helpers. Module/card lifecycle is handled by `snd_mixer_oss_notify_handler()`.

## Control Flow and State
Open resolves an OSS mixer minor to a card, checks `card->mixer_oss`, adds the file to the card file list, allocates per-open `snd_mixer_oss_file`, and pins the module. Ioctls dispatch OSS mixer info/version/mask/caps/recsrc operations and generic read/write volume commands based on the command bits. Volume values are exposed as 0-100 left/right bytes and converted to/from ALSA native ranges with `snd_mixer_oss_conv*()`. Mapping scans common ALSA names such as Master, PCM, Mic, Line, Capture, IEC958, and fallback names; for each OSS slot it records present ALSA control numids for global/playback/capture volume, switch, route, and capture-source enum items. Runtime get/put functions find controls by numid under `controls_rwsem`, call `info/get/put`, and notify on changes.

`reg_mutex` protects mixer slot state. `mask_recsrc`, `oss_recsrc`, and optional exclusive get/put recsrc callbacks track recording-source behavior. `/proc/asound/card*/oss_mixer` can read current assignments and write new mappings, dynamically replacing slot assignment tables. On card register, the module registers the OSS device, allocates and initializes `snd_mixer_oss`, populates slots, registers OSS info strings, and creates proc state. Disconnect unregisters the OSS device but leaves mixer memory until free; free removes proc and releases slots.

## Dependencies and Integration Points
It depends on OSS minor registration, ALSA card file tracking, control lookup and notification, proc info helpers, the global `snd_mixer_oss_notify_callback` exported by card init, and optional compat ioctl pointer conversion. It is the main user-visible compatibility bridge for legacy `/dev/mixer`.

## Risks and Test Signals
Risks include fragile name-based control mapping, recsrc semantics differences between exclusive enum and per-slot switches/routes, control removal races, proc remap validation, and lifetime during disconnect with open OSS mixer files. Tests should cover OSS ioctl masks and volume commands, 0-100 conversion edge cases, stereo/mono controls, capture source enum mapping, proc read/write remaps, card disconnect with open mixer, compat ioctls, and fallback table behavior on diverse control layouts.
