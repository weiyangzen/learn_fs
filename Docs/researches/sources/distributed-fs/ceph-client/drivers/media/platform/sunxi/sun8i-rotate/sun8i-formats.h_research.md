# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-rotate/sun8i-formats.h

Purpose: declares rotate-driver pixel-format metadata and lookup/enumeration helpers.

Important APIs and types: defines `ROTATE_FLAG_YUV`, `ROTATE_FLAG_OUTPUT`, `struct rotate_format`, `rotate_find_format`, and `rotate_enum_fmt`.

Control flow: the rotate implementation uses lookup to validate formats, compute pitches/plane offsets, and program hardware format codes. Enumeration uses the output flag to restrict capture formats.

State and persistence: no mutable state; format data lives in the C file's static table.

Dependencies and integration points: includes `linux/videodev2.h` for FourCC definitions. It is the private API between `sun8i_formats.c` and `sun8i_rotate.c`.

Risks: flags encode policy as well as hardware capability; incorrect flags can expose unsupported capture formats or hide valid ones.

Test signals: format enumeration through V4L2 ioctls and static compile coverage for table/helper signatures.
