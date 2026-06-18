# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_viu.h

## Purpose
Defines Meson VIU OSD register bit fields and declares VIU initialization, OSD1 reset, and AFBC routing helpers.

## Important APIs, types, and functions
- OSD block configuration macros cover Mali source enable, canvas select, endianness, block modes, RGB/YUV output, color matrix encodings, and Mali AFBC color modes.
- OSD control macros cover enable bits, linear address mode, global alpha shift, AFBCD data path, alpha replacement, and pending status.
- Declares `meson_viu_osd1_reset()`, G12A/GXM AFBC enable/disable functions, and `meson_viu_init()`.

## Control flow
No runtime control flow exists in the header. Plane code and VIU implementation code include these constants to compose register values.

## State and persistence
No state is stored. Constants describe hardware register values that persist after writes performed by implementation and plane code.

## Dependencies and integration points
Depends on `BIT()` from kernel headers via includers and on `struct meson_drm` declarations from the broader Meson driver. It is coupled to `meson_viu.c`, Meson plane programming, and AFBCD support.

## Risks
These macros encode hardware ABI. Incorrect block mode, channel matrix, or AFBCD path bit values will cause wrong colors, broken scanout, or missing AFBC output.

## Test signals
Build coverage for macro use, plus runtime plane-format tests for RGB565/RGB888/XRGB8888 and AFBC formats that exercise these register values.
