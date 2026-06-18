<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.h

## Purpose
This header exposes the pre-NV50 display hardware helper API and defines inline register accessors and bitfield helpers for CRTC, RAMDAC, VGA, PRMVIO, TMDS, cursor, and pitch operations.

## Important APIs, Types, and Functions
It declares the exported functions implemented in `hw.c` and `nouveau_calc_arb`. Inline APIs include `NVReadCRTC`, `NVWriteCRTC`, `NVReadRAMDAC`, `NVWriteRAMDAC`, `nv_read_tmds`, `nv_write_tmds`, VGA CRTC/attribute/PRMVIO accessors, `NVVgaSeqReset`, `NVVgaProtect`, `nv_heads_tied`, CRTC lock helpers, `NVLockVgaCrtcs`, `nv_cursor_width`, `nv_fix_nv40_hw_cursor`, `nv_set_crtc_base`, `nv_show_cursor`, and `nv_pitch_align`.

## Control Flow
The inline functions translate head numbers to register-window offsets, maintain VGA attribute controller enable state, switch PRMVIO addressing only where NV4x exposes per-head ranges, and update CRTC shadow/lock bits. Cursor helpers update saved mode state and kick NV40 cursor position when needed. Pitch alignment computes chipset-dependent width alignment from bits per pixel.

## State and Persistence Behavior
The header mutates hardware registers and `nv04_display(dev)->mode_reg` through inline helpers. It does not own storage except through the referenced display state, but callers rely on the helpers to keep software register snapshots and actual hardware in sync.

## Dependencies and Integration Points
It includes `disp.h`, `nvreg.h`, PLL BIOS declarations, and uses `nouveau_drm(dev)->client.device.object` for NVIF MMIO. It is the common hardware access layer for NV04 CRTC, DFP, DAC, TV, overlay, and mode-state code.

## Risks
Because much of the API is inline, incorrect use can bypass required head ownership or lock/protect sequencing. Bitfield macros rely on the local `high:low` macro idiom and are not type-safe. PRMVIO per-head behavior differs before NV4x, and callers must call `NVSetOwner` where required. Cursor visibility changes touch saved state and hardware, so missed synchronization can produce stale cursor state.

## Test Signals
Compile coverage catches register macro drift. Runtime signals include CRTC register access on both heads, palette state preservation, cursor show/hide and base changes on NV04/NV10/NV40, pitch alignment for common bpp values, TMDS indirect register reads/writes, and lock/unlock correctness around modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/hw.h -->
