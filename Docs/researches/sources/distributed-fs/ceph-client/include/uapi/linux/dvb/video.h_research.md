## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/video.h

Purpose: This deprecated DVB MPEG-TS video decoder UAPI controls legacy video decoder playback, still pictures, display format, events, status, PTS/frame counters, and extended commands.

Important APIs and types: Enums define aspect ratio, display format, source, and play state. `struct video_command` supports play/stop/freeze/continue with flags, PTS, speed, format, and raw extension data. `struct video_event` reports size, frame rate, decoder stopped, and vsync events. `struct video_status`, `struct video_still_picture`, `video_attributes_t`, and capability bits describe decoder state, still iframe injection, MPEG stream attributes, and supported features. Ioctls cover playback control, source/display/blank settings, status/event reads, still picture, speed controls, capabilities, buffer clear, stream type/format, size, PTS, frame count, and try/apply command.

Control flow and state: Userspace selects source, configures display behavior, starts playback, handles events, freezes/stops/continues, and queries timestamps and frame counters. `VIDEO_TRY_COMMAND` lets userspace validate a command before applying with `VIDEO_COMMAND`.

Persistence and dependencies: State is runtime decoder hardware/driver state. The header depends on `<linux/types.h>` and `<time.h>` outside kernel builds. User pointers appear in still-picture submission.

Integration points: It consumes demux or memory-fed streams and coordinates with audio AV sync, OSD overlays, and DVB frontend/demux pipelines.

Risks and test signals: Risks include deprecated API usage, userspace pointer copy bugs, timestamp width/meaning differences, event timestamp Y2038 note, speed control variance, and coupling to audio sync. Tests should cover play/stop/freeze/continue state, command validation, PTS/frame-count monotonicity, event delivery for size/vsync/stop, still picture bounds, and unsupported capability handling.
