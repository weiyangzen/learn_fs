<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvmodesnv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvmodesnv17.c

## Purpose
This file provides on-chip NV17/NV4x TV norm tables, low-definition and component/HD timing data, filter coefficient generation, TV state save/load helpers, mode lists, and property/rescaler update routines.

## Important APIs, Types, and Functions
It exports `nv17_tv_norm_names`, `nv17_tv_norms`, `nv17_tv_modes`, `nv17_tv_state_save`, `nv17_tv_state_load`, `nv17_tv_update_properties`, `nv17_tv_update_rescaler`, and `nv17_ctv_update_rescaler`. Internal helpers save/load filter blocks and compute filter coefficients from overscan, flicker, and scaling ratios.

## Control Flow
Static norm tables provide either TV encoder byte arrays for PAL/NTSC-like modes or CTV PRAMDAC register arrays for HD/component modes. Save/load walks TV encoder indexed registers, horizontal/vertical filter tables, and selected PTV registers. Property update chooses PTV routing and TV encoder register values based on subconnector and pin mask, then live-loads saturation and hue fields. Rescaler update computes overscan and filter coefficients for low-definition modes, while CTV update adjusts FP valid ranges and scaling ratios in PRAMDAC registers.

## State and Persistence Behavior
The file reads and writes `struct nv17_tv_state`, including TV encoder bytes, hfilter/hfilter2/vfilter matrices, and PTV register shadows. It also mutates `nv04_display.mode_reg.crtc_reg[head]` for CTV scaling and FP timing state. Hardware state persists in PTV, TV encoder, and RAMDAC register blocks.

## Dependencies and Integration Points
It integrates with `tvnv17.c` encoder lifecycle, `tvnv17.h` structures and access macros, `hw.h` RAMDAC helpers, Nouveau CRTC indices, DRM display modes, and legacy TV connector properties.

## Risks
Much of the filter and CTV programming is empirical. Fixed-point filter math is complex and could overflow or produce invalid coefficients if property ranges change. Low-definition and component paths use different hardware blocks, so applying the wrong property path can write irrelevant registers. The state load pokes register `0x3e` to make settings latch, which is undocumented.

## Test Signals
Visual output validation across PAL, PAL-M/N/Nc, NTSC-M/J, 480i/p, 576i/p, 720p, and 1080i is important. Exercise overscan, flicker, saturation, hue, subconnector changes, save/restore, low-definition mode clocks, and component scaling on both interlaced and progressive output modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/tvmodesnv17.c -->
