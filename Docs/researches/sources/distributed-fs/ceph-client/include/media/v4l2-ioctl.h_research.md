# sources/distributed-fs/ceph-client/include/media/v4l2-ioctl.h

Purpose: declares the V4L2 ioctl dispatch contract, driver callback vtable, debug flags, analog-standard helpers, compat translation helpers, and core `video_ioctl2()` / `video_usercopy()` entry points.

Important APIs/types: `struct v4l2_ioctl_ops` is the central callback table for capabilities, format enum/get/set/try across video/VBI/SDR/meta and single/multiplane paths, buffer operations, streaming, standards, input/output, controls, audio, tuner, selection/crop, JPEG compression, encoder/decoder commands, stream parameters, sliced VBI, log status, hardware seek, advanced debug, frame sizes/intervals, DV timings, EDID, event subscribe/unsubscribe, and private default ioctls. Debug flags include `V4L2_DEV_DEBUG_IOCTL`, `_ARG`, `_FOP`, `_STREAMING`, `_POLL`, and `_CTRL`.

Control flow: driver file operations normally point `unlocked_ioctl` at `video_ioctl2()`. The core copies ioctl payloads through `video_usercopy()`, maps commands to typed callbacks in `v4l2_ioctl_ops`, applies core checks such as priority and valid-ioctl filtering, and lets `vidioc_default` handle private commands. Compat paths translate 32-bit userspace commands and arrays through `v4l2_compat_*` helpers.

State and persistence: this header defines dispatch contracts, not long-lived objects. Runtime state lives in `video_device` (`ioctl_ops`, `valid_ioctls`, `dev_debug`, locks), filehandles, controls, queues, and user buffers. `v4l2_event_time32` and `v4l2_buffer_time32` preserve old 32-bit time ABI layouts.

Dependencies and integration: includes poll/fs/mutex/sched signal/compiler/videodev2. Integrates with `v4l2-dev.h`, `v4l2-fh.h`, control helpers, mem2mem ioctl helpers, vb2 queues, DV timing helpers, events, and compat syscall support.

Risks: callback tables with missing try/set pairs can expose inconsistent behavior; incorrect command translation can corrupt compat ABI; drivers must not trust userspace pointers after usercopy; private ioctls need priority validation via `valid_prio`; and legacy time32 structs must remain ABI-compatible.

Test signals: ioctl coverage for every populated callback, invalid ioctl masking, priority-denied mutations, 32-bit compat query/qbuf/dqbuf/event paths, debug logging flags, private ioctl fallback, standard enumeration helpers, and fuzzing of usercopy sizes and array arguments.
