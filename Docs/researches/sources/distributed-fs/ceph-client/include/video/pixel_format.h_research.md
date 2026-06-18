# sources/distributed-fs/ceph-client/include/video/pixel_format.h

## Purpose
`pixel_format.h` provides a small generic pixel-format descriptor and comparison helpers for indexed and RGB bitfield formats.

## Important APIs, Types, and Functions
`struct pixel_format` stores bits per pixel, an indexed flag, and either index bitfield metadata or alpha/red/green/blue bitfields. Predefined initializer macros include `PIXEL_FORMAT_C8`, `XRGB1555`, `RGB565`, `RGB888`, `XRGB8888`, `XBGR8888`, and `XRGB2101010`. `pixel_format_cmp()` performs lexicographic comparison of descriptor fields, and `pixel_format_equal()` wraps it for equality.

## Control Flow
Callers construct or use predefined descriptors, then compare them to select compatible formats, sort formats, or test exact equality. For indexed formats only the index field is compared; for non-indexed formats alpha/red/green/blue fields are compared in order.

## State and Persistence Behavior
There is no runtime state beyond caller-owned descriptors. The predefined macros are compile-time initializers.

## Dependencies and Integration Points
It integrates display/fb helper code that needs format matching independent of DRM fourcc or fbdev var structures. It expects `bool` to be available from including headers.

## Risks and Test Signals
Risks include comparing non-normalized descriptors, missing alpha semantics for X formats, callers assuming `memcmp()` byte layout instead of documented ordering, and unmasked initializer values. Test signals include equality and ordering unit tests across indexed/RGB formats, compile coverage for static initializers, and conversion tests from fbdev/DRM format descriptions.
