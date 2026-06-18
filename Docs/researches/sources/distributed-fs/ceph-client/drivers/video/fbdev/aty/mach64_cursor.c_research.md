# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/mach64_cursor.c

## Purpose

`mach64_cursor.c` implements hardware cursor support for Mach64 CT/VT/GT/LT devices. It reserves one page at the end of framebuffer memory for a 64x64 two-bit cursor image, translates fbdev cursor requests into Mach64 cursor registers and image memory, and installs the cursor callback into `atyfb_ops`.

## Important APIs, Types, and Functions

The public entry point is `aty_init_cursor()`, which reduces `info->fix.smem_len`, maps or selects the cursor sprite memory, initializes `info->sprite`, and assigns `atyfb_cursor()` to `fb_ops->fb_cursor`. `atyfb_cursor()` handles enable/disable, position, color map, shape, and image updates. `cursor_bits_lookup[]` converts four 1-bpp source bits into packed two-bit hardware cursor pixels, and `comp()` applies masks for partial final bytes.

## Control Flow

Initialization subtracts `PAGE_SIZE` from usable framebuffer memory, places the cursor storage at the new end of VRAM, and handles platform differences: Sparc uses a special offset, big-endian systems ioremap a hardware address, and little-endian systems use `screen_base + smem_len`. The sprite is declared as IO pixmap memory with 16-byte scan and buffer alignment.

`atyfb_cursor()` first rejects Sparc mmap ownership conflicts and sleeping devices. It toggles `HWCURSOR_ENABLE` in `GEN_TEST_CNTL`. For position updates it subtracts the hotspot and current framebuffer pan offsets, converts negative positions into horizontal/vertical cursor offsets, doubles vertical coordinates in double-scan mode, then writes `CUR_OFFSET`, `CUR_HORZ_VERT_OFF`, and `CUR_HORZ_VERT_POSN`. For color updates it derives foreground/background colors from the fbdev colormap and writes `CUR_CLR0`/`CUR_CLR1`. For shape or image updates it clears the 1024-byte cursor bitmap to the transparent pattern `0xaa`, then walks source and mask bytes and emits packed two-bit cursor pixels for `ROP_XOR` or `ROP_COPY`, padding partial trailing pixels as transparent.

## State and Persistence Behavior

The cursor image persists in a reserved VRAM page for the life of the mode/device, and cursor enable, position, colors, and offsets persist in Mach64 cursor registers. The driver reduces available framebuffer memory so normal fbdev drawing does not overwrite the cursor image. There is no saved software copy of the cursor image in this file beyond fbdev-provided structures during update calls.

## Dependencies and Integration Points

This file depends on fbdev cursor structures, `info->sprite`, the base driver's CRTC state for double-scan detection, `info->var` offsets for panning compensation, and Mach64 cursor register definitions. It is only initialized by `aty_init()` for integrated CT-family devices when acceleration is not globally disabled.

## Risks and Edge Cases

The cursor storage reservation changes `smem_len`, so ordering with VRAM sizing and mode validation matters. Negative positions are handled through offsets, but very large cursors or hotspots outside expected fbdev bounds could stress the arithmetic. Only `ROP_XOR` and `ROP_COPY` are explicitly handled. The code clears a fixed 1024-byte cursor area and assumes 64x64 hardware format; larger fbdev cursor images would not fit correctly. On big-endian systems the ioremap must be released by the base cleanup path. Sparc mmap users block hardware cursor updates to avoid conflicting direct hardware access.

## Test Signals

Test cursor enable/disable, movement with panned displays, negative x/y positions, nonzero hotspots, double-scan modes, colormap changes, XOR and COPY cursors, widths not divisible by eight, repeated shape updates, and teardown on big-endian mappings. Also test with acceleration disabled to confirm cursor initialization is skipped.
