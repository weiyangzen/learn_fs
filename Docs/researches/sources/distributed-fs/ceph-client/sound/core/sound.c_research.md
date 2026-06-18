# sources/distributed-fs/ceph-client/sound/core/sound.c

## Purpose
`sound.c` is the ALSA native core character-device registry. It registers the ALSA major, handles `/dev/snd/*` opens by minor lookup and fops replacement, supports module autoload for card/control/global devices, and provides device registration/unregistration for ALSA subsystems.

## Important APIs, Types, and Functions
- `snd_request_card()` requests `snd-card-N` modules for autoloadable cards.
- `snd_lookup_minor_data()` looks up registered minor private data and takes a card device reference.
- `snd_register_device()` assigns a native ALSA minor, sets device `devt`, calls `device_add()`, and stores a `snd_minor` registry entry.
- `snd_unregister_device()` removes a registered device and frees its minor entry.
- `snd_open()` is the major-device open trampoline that autoloads missing devices and replaces file ops with the real device operations.
- `snd_minor_info_init()` creates optional `/proc/asound/devices` style native-device reporting.
- `alsa_sound_init()` and `alsa_sound_exit()` register/unregister the major, info core, and debugfs root.

## Control Flow
Subsystem init stores module parameters in exported globals, registers the char major with `snd_fops`, initializes ALSA info, and creates debugfs if enabled. On open, `snd_open()` indexes `snd_minors[]` under `sound_mutex`; if absent and modules are enabled it temporarily drops the mutex and requests either a card module or global sequencer/timer module, then retries lookup. The open path grabs the real file operations, replaces fops, and invokes the real open.

Device registration allocates a `snd_minor`, finds a free static or dynamic minor, sets `device->devt`, calls `device_add()`, then publishes the registry entry. Unregistration finds the matching `struct device`, clears the registry entry, calls `device_del()`, and frees metadata.

## State and Persistence
Global runtime state includes `snd_major`, `snd_ecards_limit`, optional `sound_debugfs_root`, and `snd_minors[]` protected by `sound_mutex`. There is no persistent storage.

## Dependencies and Integration Points
Depends on Linux char device and device core, module loading, ALSA card refcount helpers, minor-number macros, ALSA info, controls, and debugfs. All native ALSA device classes register through this file.

## Risks
Open-time autoload deliberately drops `sound_mutex`; the subsequent minor entry can appear/disappear and must be rechecked. `snd_lookup_minor_data()` transfers a card reference expectation to callers. Static minor mapping must match ABI. `device_add()` occurs before publishing in `snd_minors[]`, so failure cleanup must free only unpublished state.

## Test Signals
Test static and dynamic minor allocation, duplicate minor failure, open fops replacement, autoload for card/control and global seq/timer minors, lookup reference behavior, unregister by device pointer, proc devices output, and module init/exit failure unwind.
