<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc_regs.h

## Purpose
`vs_crtc_regs.h` defines display timing, sync, gamma/dither, current-location, and display IRQ register offsets for VeriSilicon DC CRTCs.

## Important APIs, Types, and Functions
Key macros are `VSDC_DISP_HSIZE`, `VSDC_DISP_VSIZE`, `VSDC_DISP_HSYNC`, `VSDC_DISP_VSYNC`, field masks and builders for display/total/start/end values, sync enable/polarity bits, dither defaults, gamma registers, and display IRQ status/enable offsets.

## Control Flow
`vs_crtc_mode_set_nofb()` writes size and sync registers using these macros; future gamma/dither support would use the remaining definitions.

## State and Persistence Behavior
These macros describe persistent MMIO register state. The file itself has no runtime storage.

## Dependencies and Integration Points
It depends on Linux bit macros and is consumed by `vs_crtc.c`. Offsets must be within the regmap range configured by `vs_dc.c`.

## Risks
Incorrect shifts or masks corrupt display timings. Dither/gamma definitions are currently unused, so future users must verify default values and commit semantics.

## Test Signals
Mode-set register traces and hardware output timing measurements should verify encoded horizontal/vertical fields and sync polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc_regs.h -->
