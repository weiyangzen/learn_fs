# sources/distributed-fs/ceph-client/include/sound/pcm_oss.h

Source read summary: 75 lines, ALSA PCM OSS emulation data structures.

Purpose: defines per-runtime, per-substream, and per-stream state used to emulate legacy OSS PCM behavior on top of ALSA PCM.

Important APIs, types, and functions: structures track OSS buffer fragments, format/rate/channels, plugin/conversion state, mmap flags, trigger flags, bytes counters, period calculations, and OSS setup callbacks. These structs are embedded in `snd_pcm_runtime`, `snd_pcm_substream`, and `snd_pcm_str` when `CONFIG_SND_PCM_OSS` is enabled.

Control flow: OSS open/ioctl/read/write paths translate legacy parameters into ALSA hw/sw params, maintain fragment accounting, and use plugin/conversion helpers before forwarding to PCM transfers.

State and persistence behavior: state is open-stream emulation bookkeeping only. Audio data remains in PCM buffers and OSS parameters are not persisted after close.

Dependencies and integration points: used conditionally by `pcm.h` and ALSA OSS emulation implementation. It bridges `/dev/dsp` style applications to native PCM.

Risks and edge cases: fragment math, mmap compatibility, trigger semantics, format conversion, and full-duplex behavior differ from native ALSA and can regress old applications.

Test signals: OSS ioctl compatibility, fragment size/count behavior, mmap/read/write playback and capture, format/rate/channel conversion, trigger start/stop, and builds with OSS disabled.
