<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/vga.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/vga.c

## Purpose

`vga.c` provides legacy VGA indexed register access helpers and VGA owner/lock control across pre-NV50 and NV50+ register layouts.

## Important APIs, Types, And Functions

`nvkm_rdport()` and `nvkm_wrport()` translate VGA port numbers to MMIO addresses, considering head selection and card generation. `nvkm_rdvgas()/wrvgas()`, `nvkm_rdvgag()/wrvgag()`, and `nvkm_rdvgac()/wrvgac()` access sequencer, graphics, and CRTC indexed registers. `nvkm_rdvgai()` and `nvkm_wrvgai()` dispatch based on index port. `nvkm_lockvgac()` locks or unlocks CRTC extended registers. `nvkm_rdvgaowner()` and `nvkm_wrvgaowner()` manage CR44-style VGA ownership across heads.

## Control Flow

Callers select a head and VGA port/index. The helper routes accesses through NV50 unified MMIO or legacy PRMVIO/PRMCIO ranges. Owner helpers are used around legacy VGA init/save/restore so the intended head owns shared 8-bit VGA I/O registers.

## State And Persistence Behavior

No software state is stored. The functions directly read and write VGA hardware registers, including lock state and CR44 owner state. `nvkm_lockvgac()` returns the previous lock state.

## Dependencies And Integration Points

The file depends on `subdev/vga.h`, `nvkm_device` MMIO helpers, card type/chipset detection, and legacy display init paths that require VGA register access.

## Risks And Edge Cases

Pre-NV40 head B PRMVIO access may require CR44 owner selection. NV11 has tied-head and lockup workarounds, including special CR reads/writes. Invalid ports return zero or no-op rather than errors. Lock/unlock register differs on NV50+.

## Test Signals

Signals include correct VGA state save/restore, no lockups on NV11, correct head-specific CRTC access on dual-head legacy chips, and stable text/VGA mode behavior around modesets and driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/vga.c -->
