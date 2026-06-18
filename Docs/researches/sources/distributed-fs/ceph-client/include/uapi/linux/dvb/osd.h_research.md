## sources/distributed-fs/ceph-client/include/uapi/linux/dvb/osd.h

Purpose: This deprecated DVB on-screen-display UAPI defines commands for old decoder hardware OSD planes, palettes, drawing primitives, text, windows, and capability queries. New drivers should not adopt it.

Important APIs and types: `OSD_Command` enumerates close/open/show/hide/clear/fill, palette and transparency changes, pixel/row/block operations, line drawing, query, test, text, window selection/move, and raw window open. `osd_cmd_t` carries command, coordinates, color/inc fields, and a userspace data pointer. `osd_raw_window_t` names bitmap, YCrCb, video-size, and cursor raw window modes. `osd_cap_t` reports capabilities such as memory size. Ioctls are `OSD_SEND_CMD` and `OSD_GET_CAPABILITY`.

Control flow and state: Applications open an OSD window with geometry and bit depth, populate palette/graphics, show or hide it, perform drawing commands, then close it. The hardware maintains window buffers, current window selection, palette, transparency, and visibility.

Persistence and dependencies: All state is runtime device state. The header depends on `<linux/compiler.h>` for `__user` pointer annotation.

Integration points: OSD overlays video decoder output in legacy DVB adapters and set-top-box designs. It may interact with video plane sizing and decoder display mode.

Risks and test signals: Risks include deprecated API exposure, unsafe userspace pointers, coordinate clipping, palette opacity interpretation, hardware memory exhaustion, and command-specific overloading of integer fields. Tests should cover open/close error codes, clipping, palette ranges, data pointer copy sizes for rows/blocks/text, multi-window behavior, capability reporting, and hide/show interactions with video output.
