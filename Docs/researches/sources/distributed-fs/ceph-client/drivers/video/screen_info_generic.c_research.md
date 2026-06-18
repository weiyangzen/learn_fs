# sources/distributed-fs/ceph-client/drivers/video/screen_info_generic.c

Purpose: generic helpers for interpreting `struct screen_info` firmware display data. It derives I/O/memory resources consumed by text/framebuffer devices and translates linear framebuffer color metadata into a generic pixel format.

Important APIs, types, and functions: exported `screen_info_resources`, `__screen_info_lfb_bits_per_pixel`, and `screen_info_pixel_format`. Internal helpers initialize named `struct resource` objects and identify EGA/VGA graphics modes.

Control flow: `screen_info_resources` switches on `screen_info_video_type` and emits resource descriptors for MDA, CGA, EGA mono/color, VGA color, and linear framebuffer EFI/VESA types, subject to caller array length. Unsupported platform-specific types return `-EINVAL`. Pixel-format handling computes effective bits-per-pixel from depth and channel/reserved bit extents, fills indexed formats for depth <=8, and fills direct channel offsets for linear framebuffers.

State and persistence: no state; operates on caller-provided `screen_info`, resources, and pixel-format structures.

Dependencies and integration points: used by sysfb/simplefb/simpledrm and firmware framebuffer arbitration paths. Depends on `linux/screen_info.h`, `ioport`, and `<video/pixel_format.h>`.

Risks: support is intentionally limited to common text and linear framebuffer types. Resource computation trusts firmware-provided base/size helpers. The bpp derivation handles historical inconsistencies but may still reject values above `U8_MAX`.

Test signals: unit tests or boot checks for each supported video type, resource array truncation behavior, zero LFB base/size handling, XRGB1555/RGB565/XRGB8888 bpp derivation, indexed 8-bpp format, and unsupported types returning `-EINVAL`.
