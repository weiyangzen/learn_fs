# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-format.h

Purpose: Local and remote MMAL elementary stream format structures used to describe audio, video, and subpicture streams in MMAL messages.

Important APIs, types, and functions: `struct mmal_audio_format` carries channel count, sample rate, bits per sample, and block alignment. `struct mmal_video_format` carries width, height, crop rectangle, frame rate, pixel aspect ratio, and color space. `struct mmal_subpicture_format` carries x/y offsets. `union mmal_es_specific_format` selects the type-specific structure. `struct mmal_es_format_local` uses real kernel pointers for type-specific data and extradata. `struct mmal_es_format` is the remote/wire representation using 32-bit pointer/handle fields.

Control flow: no executable flow; consumers convert between local pointer-rich structures and remote 32-bit firmware message representations.

State and persistence: no global state. Format instances persist as component/port configuration state in consumers.

Dependencies and integration points: includes `linux/math.h` for `struct s32_fract` and `mmal-msg-common.h` for `mmal_rect`. Integrates with MMAL port setup and V4L2 format negotiation.

Risks: confusing local and remote forms can leak kernel pointers or send invalid firmware addresses. Structure layout and field widths must match the VideoCore MMAL ABI. Extradata size/pointer handling is a common bounds and lifetime risk.

Test signals: compile-time layout checks, local-to-remote conversion tests, video crop/frame-rate/PAR negotiation tests, and codec extradata round trips.
