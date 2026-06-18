# sources/distributed-fs/ceph-client/drivers/media/usb/usbtv/usbtv.h

Purpose: defines the shared USBTV007 driver contract used by the core, video, and audio source files. It centralizes endpoint numbers, vendor request/register constants, chunk geometry, TV standards, common structures, and cross-module function declarations.

Important APIs and types: constants include `USBTV_VIDEO_ENDP`, `USBTV_AUDIO_ENDP`, `USBTV_BASE`, request IDs, isochronous transfer sizing, image chunk sizing, and audio buffer sizing. Header macros decode proprietary video chunk headers: `USBTV_MAGIC_OK`, `USBTV_FRAME_ID`, `USBTV_ODD`, and `USBTV_CHUNK_NO`. Types include `struct usbtv_norm_params`, `struct usbtv_buf`, and the per-device `struct usbtv`. Declared functions are `usbtv_set_regs`, video lifecycle functions, and audio lifecycle/suspend/resume functions.

Control flow: this header itself has no executable flow, but it defines how the modules interact. `usbtv-core.c` owns allocation and calls video/audio init/free. `usbtv-video.c` uses endpoint/chunk/norm definitions for capture and frame assembly. `usbtv-audio.c` uses audio endpoint and buffer constants for PCM streaming. The function prototypes make these boundaries explicit.

State and persistence: `struct usbtv` is the central volatile state object. It embeds V4L2 device/control/video/vb2 state, buffer lists and frame assembly counters, current input/norm/geometry, isochronous URB pointers, ALSA card/substream state, audio stream flag/work item, audio URB pointer, and ALSA ring positions. It contains no persistent configuration.

Dependencies and integration points: includes USB, module, slab, V4L2 device/control/vb2 headers. The header is the integration point between Linux USB probing, V4L2 capture, vb2 memory management, and ALSA capture implemented by separate translation units.

Risks: because the shared struct carries both audio and video state, locking and lifetime assumptions are spread across files. Chunk macros assume big-endian 32-bit chunk words and specific bit layout. `USBTV_ODD` shifts a masked bit field by 15 after masking `0x0000f000`, which produces non-boolean values if multiple bits appear; consumers only test truthiness. Constant changes can alter buffer sizes and frame reconstruction math across modules.

Test signals: compile all three USBTV objects together, verify structure fields used by each translation unit match lifecycle assumptions, and exercise combined audio/video streaming, disconnect, and norm changes to validate shared state transitions.
