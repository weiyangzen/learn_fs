<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.h

## Purpose

This header defines VPIF register offsets, bit masks, inline MMIO helpers, channel enable/interrupt helpers, capture/display buffer-address programming helpers, raw ancillary-data toggles, timing structures, and exported common function prototypes.

## Important APIs, types, and functions

- `regr()` and `regw()` access the exported `vpif_base`.
- Channel helpers enable/disable channels 0-3, configure frame interrupts, assert interrupt-on-both-fields, set video buffer addresses, set VBI/HBI addresses, toggle raw VANC/HANC, and enable display clipping.
- `vpif_intr_status()` reads and clears per-channel interrupt status.
- `struct vpif_channel_config_params` describes timing, muxing, field mode, SD/HD identity, VBI support, and DV timings.
- `struct vpif_vbi_params`, `struct vpif_video_params`, and `struct vpif_params` carry runtime channel parameters for common programming.

## Control flow

The inline helpers are called by capture/display start, stop, ISR, and address scheduling paths. Address helper selection depends on channel number and mux mode; interrupt helpers wrap shared register updates in `vpif_lock`.

## State and persistence behavior

The header declares the shared MMIO base and lock but owns no memory itself. It defines structures that capture/display drivers persist in channel objects while the device is loaded. Register writes directly update hardware state and are not persistent.

## Dependencies and integration points

It depends on Linux I/O helpers, V4L2 IDs, and `media/davinci/vpif_types.h` for platform data and interface types. It is the contract among `vpif.c`, `vpif_capture.c`, and `vpif_display.c`.

## Risks and edge cases

Most MMIO helpers are inline read-modify-write operations; only interrupt enable helpers lock, so callers must avoid concurrent unsafe updates. Two-channel Y/C non-mux helpers intentionally write chroma addresses into the adjacent channel. The interrupt disable helpers write to `VPIF_INTEN_SET` after clearing `VPIF_INTEN`, which is hardware-specific and should be regression-tested.

## Test signals

Compile coverage plus streaming tests that exercise all four channels, muxed and non-muxed modes, top/bottom field address programming, interrupt clearing, VBI/HBI toggles, and clipping controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/ti/davinci/vpif.h -->
