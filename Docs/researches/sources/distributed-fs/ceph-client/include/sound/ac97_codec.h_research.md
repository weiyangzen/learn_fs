# sources/distributed-fs/ceph-client/include/sound/ac97_codec.h

## Purpose
`ac97_codec.h` defines the legacy ALSA AC97 codec and bus API. It combines vendor-specific register constants, capability and quirk flags, bus operation callbacks, codec state, register cache layout, power-management hooks, mixer construction, hardware tuning, and PCM slot assignment interfaces.

## Important APIs, Types, and Functions
Core types are `struct snd_ac97_bus_ops`, `struct snd_ac97_bus`, `struct snd_ac97_template`, `struct snd_ac97`, `struct snd_ac97_build_ops`, `struct ac97_quirk`, and `struct ac97_pcm`. Public functions include `snd_ac97_bus()`, `snd_ac97_mixer()`, `snd_ac97_write()`, `snd_ac97_read()`, `snd_ac97_update_bits()`, `snd_ac97_reset()`, `snd_ac97_tune_hardware()`, `snd_ac97_set_rate()`, `snd_ac97_pcm_assign()`, `snd_ac97_pcm_open()`, and `snd_ac97_pcm_close()`. Inline predicates test audio, modem, AC97 revision, AMAP, and S/PDIF support.

## Control Flow
Low-level drivers create a bus with hardware callbacks, instantiate codecs with a template, then the AC97 core probes IDs, builds mixer controls, applies vendor quirks, maintains cached register values, and allocates PCM slots for playback/capture streams. PCM open selects rate/capability combinations and slot maps; close releases them.

## State and Persistence Behavior
`struct snd_ac97` persists runtime codec state: IDs, caps, flags, rates, S/PDIF status, cached registers, accessed bits, vendor-specific data, channel mode, optional power-save work, and the device object. State persists for the card lifetime and is restored through suspend/resume hooks, not across reboot.

## Dependencies and Integration Points
The header depends on Linux bitops/device/workqueue and ALSA PCM, control, and info APIs. It integrates low-level PCI/SoC audio bridges, mixer controls, proc info, PCM runtime rules, power management, and the AC97 device bus.

## Risks and Test Signals
Risks include stale register caches, vendor quirk regressions, broken double-rate slot allocation, concurrency around `reg_mutex` and `page_mutex`, and power-save state drift. Test signals include AC97 mixer enumeration, quirk table coverage, PCM open/close at standard and double rates, suspend/resume with cache restore, and codec reset failure paths.
