# sources/distributed-fs/ceph-client/sound/sound_core.c

## Purpose
Core sound class registration plus optional legacy OSS sound core. The common part creates the `sound` device class used by ALSA and OSS devices. The OSS part allocates legacy `SOUND_MAJOR` minors, creates `/dev/sound/*` devices, and dispatches opens to registered subdriver file operations or module autoload aliases.

## Important APIs, Types, and Functions
Exports `sound_class`. With `CONFIG_SOUND_OSS_CORE`, exports `register_sound_special_device()`, `register_sound_special()`, `register_sound_mixer()`, `register_sound_dsp()`, `unregister_sound_special()`, `unregister_sound_mixer()`, and `unregister_sound_dsp()`. Important internals are `struct sound_unit`, `sound_insert_unit()`, `sound_remove_unit()`, `__sound_insert_unit()`, `__sound_remove_unit()`, `__look_for_unit()`, and `soundcore_open()`.

## Control Flow, State, and Persistence
`init_soundcore()` initializes optional OSS core then registers `sound_class`; cleanup reverses that. OSS mode optionally preclaims all SOUND_MAJOR minors via `register_chrdev()` depending on `preclaim_oss`. Registered units are stored in ordered linked lists by minor-chain modulo 16 under `sound_loader_lock`. Device registration chooses a minor, optionally registers a one-minor char device when not preclaiming, and creates a class device. Open maps audio/dsp16 minors back to the DSP chain, looks up the registered unit, optionally requests legacy `sound-slot-*`, `sound-service-*`, and standard char-major modules, replaces file ops with the subdriver ops, and calls the subdriver open.

## Dependencies and Integration Points
Depends on Linux device class, chrdev, module autoloading, spinlocks, SOUND_MAJOR, and file-operation replacement APIs. It is the compatibility boundary used by OSS drivers and ALSA OSS emulation while sharing the common `sound` class with modern sound devices.

## Risks and Test Signals
Risks include legacy preclaim behavior blocking alternate OSS implementations, list/chrdev races handled by retry only in non-preclaim mode, device-create return ignored, minor-chain aliasing for dsp/audio/dspW, and reliance on subdriver module lifetime. Test signals are class registration at subsys init, `/dev/snd/*` devnode naming for non-SOUND_MAJOR devices, OSS mixer/DSP/special register/unregister, preclaim and non-preclaim open autoload behavior, and open dispatch to replacement fops.
