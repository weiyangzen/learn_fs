<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/vga.h -->
# sources/distributed-fs/ceph-client/include/video/vga.h

## Purpose
This header provides standard VGA port/register constants, state save/restore declarations, and inline helpers for MMIO or I/O-port based VGA register access.

## Important APIs, Types, And Functions
- Constants define VGA framebuffer physical base/size, data/index ports, register counts, misc/CRTC/attribute/sequencer/graphics indices and masks, and state-save flags.
- `struct vgastate` describes a VGA state snapshot request: MMIO base, memory window, flags, depth, register counts, and opaque saved state.
- `save_vga()` and `restore_vga()` are exported state-management functions.
- Inline helpers cover raw MMIO/I/O reads and writes (`vga_mm_r`, `vga_io_r`, `vga_r`, `vga_w`), fast 16-bit writes on little-endian systems, and indexed CRTC, sequencer, graphics, and attribute controller access.

## Control Flow
Callers choose MMIO when `regbase` is non-NULL or I/O ports when available. Indexed helpers write the register index then read/write the data port, with optional combined 16-bit writes under `VGA_OUTW_WRITE`. State save/restore routines use `vgastate.flags` to capture mode, fonts, text, and colormap.

## State And Persistence
The VGA device retains register, palette, font, and framebuffer state. `vgastate.vidstate` points to saved software snapshots used across mode changes or driver handoff.

## Dependencies And Integration Points
It depends on Linux IO accessors, architecture VGA definitions, byte order, and optional `CONFIG_HAS_IOPORT`. It is shared by VGA-compatible framebuffer/DRM/console drivers.

## Risks And Edge Cases
I/O ports may be unavailable on some architectures, so MMIO fallback must be valid. Fast 16-bit index/data writes are little-endian only. Attribute controller access has flip-flop behavior in VGA hardware, so callers must follow VGA sequencing expectations. Register count defaults must match allocated snapshot sizes.

## Test Signals
Signals include successful save/restore around driver handoff, correct font and colormap preservation, working MMIO-only and I/O-port paths, valid indexed register reads/writes, and no corruption from fast-write mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/vga.h -->
