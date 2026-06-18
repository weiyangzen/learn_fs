# sources/distributed-fs/ceph-client/include/media/v4l2-image-sizes.h

Purpose: provides common image dimension macros for standard frame sizes used by V4L2 drivers and format tables.

Important APIs/types: defines width/height pairs for CIF, HD 720, HD 1080, QCIF, QQCIF, QQVGA, QVGA, SVGA, SXGA, VGA, UXGA, and XGA. There are no functions or stateful structures.

Control flow: drivers include this header and use the constants in frame-size enumeration, default format setup, bounds checking, or sensor mode tables.

State and persistence: stateless preprocessor constants only.

Dependencies and integration: no external includes beyond the guard. Integrates indirectly with format enumeration helpers and driver mode definitions.

Risks: constants are conventional sizes, not capability declarations; use in drivers without checking actual hardware mode tables can advertise unsupported resolutions. `SXGA_WIDTH` equals `HD_720_WIDTH` but has different height, so name-based assumptions can be misleading.

Test signals: compile-time use in mode tables, frame-size enumeration matching hardware modes, default format initialization, and documentation/tests that distinguish similarly wide formats.
