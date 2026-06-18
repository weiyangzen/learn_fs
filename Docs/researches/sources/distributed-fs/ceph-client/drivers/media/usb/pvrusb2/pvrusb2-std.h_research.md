# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/pvrusb2-std.h

Purpose: public declaration header for pvrusb2 video-standard string conversion helpers.

Important APIs, types, and functions: declares `pvr2_std_str_to_id()` to parse strings like `PAL-B/G;NTSC-M` into V4L2 standard masks, `pvr2_std_id_to_str()` to format a mask into parseable text, and `pvr2_std_get_usable()` to return standards supported by the conversion tables.

Control flow: callers use the parser for control writes and the formatter for control reads/logging. The header itself contains no executable logic.

State and persistence: no state is declared. Conversion tables live in `pvrusb2-std.c`.

Dependencies and integration points: includes `linux/videodev2.h` for `v4l2_std_id`. Used by hardware controls and any user-facing interface that wants symbolic standard masks.

Risks: callers must pass explicit buffer sizes because parser input is not necessarily NUL-terminated. Formatter return values should be treated as byte counts, not necessarily NUL-terminated string length.

Test signals: build callers; unit-style round trips through controls; sysfs writes using generated standard strings.
