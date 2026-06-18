## sources/distributed-fs/ceph-client/drivers/staging/sm750fb/sm750_accel.h

Purpose: this header defines the SM750 2D engine register offsets, fields, ROP constants, blit direction constants, and public acceleration prototypes.

Important definitions: `HW_ROP2_COPY` and `HW_ROP2_XOR` are fbdev ROP values used by the driver. `DE_BASE_ADDR_TYPE1` and `DE_PORT_ADDR_TYPE1` identify the SM718/750/502 drawing engine MMIO layout used by `hw_sm750_map()`. Registers include `DE_SOURCE`, `DE_DESTINATION`, `DE_DIMENSION`, `DE_CONTROL`, `DE_PITCH`, foreground/background colors, stretch format, color compare/masks, clipping, pattern registers, window widths, source/destination bases, alpha, wrap, and status.

Control flow and state: the header is declarative. Consumers use these constants to compose command register writes that transition the hardware drawing engine through idle, configured, and active states. The prototypes are implemented in `sm750_accel.c` and are installed into `struct lynx_accel`.

Dependencies and integration points: included by `sm750.c`, `sm750_hw.c`, and `sm750_accel.c`. It relies on Linux integer types and `BIT()`. It is tied to the private fbdev driver; no generic DRM acceleration interface is exposed.

Risks: direction constants define `TOP_TO_BOTTOM` and `LEFT_TO_RIGHT` as `0`, and reverse directions as `1`, which is compact but loses axis distinction outside local context. The header documents older chip base layouts that are not selected dynamically in this driver, so future reuse could choose wrong offsets. Field widths require callers to validate coordinates and pitches before masking truncates them.

Test signals: build coverage, 2D engine register dumps before/after operations, and output validation for fills, copies, and monochrome blits across bpp and pitch alignments. Static analysis should verify all command writes set the required status/command bits and clear incompatible fields when formats change.
