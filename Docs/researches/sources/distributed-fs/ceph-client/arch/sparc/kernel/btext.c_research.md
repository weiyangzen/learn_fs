<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/btext.c -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/btext.c

Purpose: Early boot framebuffer text console for PROM display devices.

Important APIs and control flow: `btext_find_display()` checks PROM stdout for `device_type = display`, initializes framebuffer geometry/address from PROM properties, clears the screen, and registers a boot console. Drawing uses `font_sun_8x16`; `btext_drawchar()` handles control characters, wraparound, and line clearing; `draw_byte_32`, `draw_byte_16`, and `draw_byte_8` expand font bits into framebuffer pixels. Scrolling code exists but is disabled by `NO_SCROLL`, so output wraps to the top.

State, dependencies, and risks: state is static console cursor, display dimensions, depth, row bytes, rectangle, and framebuffer base stored in `.data`. Dependencies include PROM properties `width`, `height`, `depth`, `linebytes`, and `address`, direct framebuffer access, console registration, and font data. Risks include only supporting PROM address property rather than PCI `reg`, no locking, unsupported depths silently drawing nothing, and wraparound erasing old lines. Test signals are early console output on display-backed PROM stdout, 8/16/32-bit framebuffer rendering, line wrap behavior, and fallback when stdout is not a display.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/btext.c -->
