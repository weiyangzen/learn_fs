# sources/distributed-fs/ceph-client/drivers/video/fbdev/vga16fb.c

## Purpose
`vga16fb.c` is an fbdev driver for legacy EGA/VGA 16-color graphics modes supplied by sysfb. It programs VGA sequencer, CRTC, graphics, attribute, DAC, and planar memory behavior directly, and supplies custom drawing paths for VGA planar framebuffers.

## Important APIs, Types, And Functions
`struct vga16fb_par` stores saved VGA state, a `vgastate`, refcount, blanking flags, mode flags, VGA/EGA distinction, misc/clock/palette state, and computed CRTC registers. The fbdev interface is `vga16fb_ops`, including open/release state save/restore, check/set mode, palette, pan, blank, fillrect, copyarea, imageblit, mmap, and destroy. Key helpers include low-level VGA register access wrappers, `vga16fb_check_var()`, `vga16fb_set_par()`, `vga16fb_update_fix()`, `vga16fb_clock_chip()`, `vga16fb_probe()`, and custom planar blitters.

## Control Flow
Probe is driven by `ega-framebuffer` or `vga-framebuffer` platform IDs and accepts only EGA/VGA graphics modes `0x0d`, `0x0e`, `0x10`, or `0x12`. It reserves/maps VGA memory, allocates `fb_info`, configures VGA/EGA palette depth, validates the default mode, acquires the aperture, registers the framebuffer, and stores driver data. A mode set computes CRTC register bytes in `check_var()`, then `set_par()` writes misc output, sequencer, CRTC, graphics controller, and attribute controller registers in the required reset/unreset sequence. Drawing operations switch VGA write modes, set/reset, masks, and data rotate registers to implement fills, copies, and image expansion.

## State And Persistence
The driver saves VGA fonts, mode, and cmap on first open and restores them on last release. Runtime state includes CRTC arrays, blanked palette/vesa flags, mode flags, and hardware registers. Framebuffer memory is the fixed VGA aperture. No disk state is used.

## Dependencies And Integration Points
It depends on sysfb platform devices, VGA I/O helpers from `<video/vga.h>`, aperture ownership, raw I/O port access, fbdev cfb fallback helpers, and legacy VGA memory mapping. It integrates with fbcon and other fbdev users, but comments note that VGA regions are shared with vgacon/others rather than fully exclusive.

## Risks
VGA planar programming is register-order-sensitive and hardware-clone-sensitive. Some clipping paths assume widths aligned to multiples of 8, reflected in pixmap capabilities. Resource sharing with vgacon is incomplete. Save/restore relies on balanced open/release refcounts. The driver rejects many modern or firmware modes, and direct port I/O makes it architecture/platform constrained.

## Test Signals
Signals include probe rejection for unsupported `screen_info`, successful 640x480/4 registration, `fbset` mode validation boundaries, correct palette programming on EGA and VGA, blank/unblank restoring sync registers, custom fill/copy/imageblit rendering in planar modes, state restoration after last close, and clean unregister with memory unmap/release.
