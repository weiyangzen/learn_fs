<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sfnt_info.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/sfnt_info.h

Purpose: preserves the ALSA Emux/AWE SoundFont patch ABI compatible with OSS-era AWE drivers, including patch headers, sample and voice records, preset mapping, and hwdep ioctls.

Important APIs and types: `soundfont_patch_info` is the 16-byte operation header for load/open/close/replace/map/probe/remove operations. `soundfont_open_parm`, `soundfont_voice_parm`, `soundfont_voice_info`, `soundfont_voice_rec_hdr`, `soundfont_sample_info`, and `soundfont_voice_map` define patch, voice, sample, and mapping records. `snd_emux_misc_mode` supports miscellaneous port modes. Ioctls include version, load patch, reset/remove samples, memory availability, and misc mode.

Control flow: userspace sends a patch header through `SNDRV_EMUX_IOCTL_LOAD_PATCH`; the driver interprets `type`, `len`, and trailing data as voice records, sample descriptors/data, open/close commands, or preset maps. Sample memory and voice mappings are then used by the Emux wavetable engine.

State and persistence: the header defines an in-memory driver patch database: loaded samples, instruments, voice parameters, mappings, locks, and memory accounting. SoundFont data is not persisted by the kernel; userspace reloads it after device reset.

Dependencies and integration points: depends on `sound/asound.h` for ALSA UAPI context and endian selection. It integrates with ALSA sequencer/synth, Emux wavetable drivers, and old OSS-compatible SoundFont loaders.

Risks and test signals: risks include endian-specific patch key encoding, variable trailing payload length validation, ioctl number collision on `0x84`, signed range semantics for key/velocity/pan, and legacy struct layout preservation. Test loading multi-voice banks, replacing/removing samples, malformed lengths, endian builds, and memory exhaustion paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/sfnt_info.h -->
