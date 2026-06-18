# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-common.h

Purpose: Common MMAL data structures and constants shared by the BCM2835 V4L2/MMAL bridge.

Important APIs, types, and functions: `MMAL_FOURCC()` constructs little-endian FourCC values; `MMAL_MAGIC` identifies MMAL messages; `MMAL_TIME_UNKNOWN` marks unknown timestamps. `struct mmal_fmt` maps V4L2 pixel formats to MMAL encodings, flags, depths, component selection, planar Y bits-per-pixel, and padding behavior. `struct mmal_buffer` embeds `vb2_v4l2_buffer` first, adds list linkage, allocated buffer pointer/size, MMAL message context, payload length, MMAL flags, DTS, and PTS. `struct mmal_colourfx` carries color-effect enable and U/V values.

Control flow: this header defines data contracts only; consumers allocate and populate these structures in MMAL/V4L2 implementation code.

State and persistence: no global state. Buffer instances persist for their vb2/MMAL lifecycle and carry timestamps/flags between V4L2 and MMAL callbacks.

Dependencies and integration points: relies on Linux integer types, `BIT_ULL`, V4L2/videobuf2 types included by users, list heads, and MMAL message context definitions. It is used by MMAL VCHIQ and likely camera/video code.

Risks: `struct mmal_buffer` requires the V4L2 buffer to remain first for container casts; reordering would break callers. FourCC construction assumes byte ordering matching MMAL protocol expectations. Padding-removal fields must agree with GPU behavior and V4L2 bytesperline handling.

Test signals: compile all MMAL consumers, verify container casts from `vb2_v4l2_buffer`, check format table mappings, and exercise timestamp/flag propagation through buffer completion.
