## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/audio.h

Purpose: This deprecated DVB MPEG-TS audio decoder UAPI describes legacy decoder control ioctls. It remains for compatibility but should not be used by new drivers.

Important APIs and types: Enums define audio source (`AUDIO_SOURCE_DEMUX` or memory), play state, and channel selection. `audio_mixer_t` stores left/right volumes. `audio_status_t` reports AV sync, mute, play state, source, channel, bypass mode, and mixer state. Capability bits include DTS, LPCM, MPEG audio layers, AAC, OGG, SDDS, and AC3. Ioctls cover stop, play, pause, continue, source selection, mute, AV sync, bypass, channel selection, status, capabilities, buffer clear, stream ID/type, mixer, and bilingual channel selection.

Control flow and state: Userspace configures source and format, starts playback, pauses/resumes/stops, adjusts mute/mixer/channel state, and queries status. Decoder state is maintained by the underlying DVB audio device and may be coupled to demux and video synchronization.

Persistence and dependencies: State is runtime-only in decoder hardware/driver. The header depends on `<linux/types.h>` and the shared DVB ioctl magic `'o'`.

Integration points: It connects to DVB demux output (`AUDIO_SOURCE_DEMUX`), memory-fed playback, AV synchronization with video decoders, and legacy set-top-box hardware.

Risks and test signals: Risks include deprecated API use in new code, ambiguous `_IO` arguments for setters, codec capability mismatch, audio/video sync drift, and hardware-specific bypass semantics. Tests should cover state transitions, status reflection, unsupported capability rejection, demux versus memory source switching, mute/mixer effects, and coexistence with video decoder ioctls.
