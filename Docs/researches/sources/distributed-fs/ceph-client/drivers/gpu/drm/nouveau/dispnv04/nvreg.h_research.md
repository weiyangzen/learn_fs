<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nvreg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nvreg.h

## Purpose
This header is the pre-NV50 display and graphics register map used by NV04 display helpers, encoders, TV, and overlay code.

## Important APIs, Types, and Functions
It defines MMIO block offsets/sizes, core register addresses, VGA sequencer/graphics/CRTC/attribute indices, RAMDAC PLL/FP/TV/TMDS registers, PTV TV encoder registers, PVIDEO overlay registers, PGRAPH registers, and numerous bitfield constants used by `MASK`, `XLATE`, `NVVAL`, and direct register writes.

## Control Flow
There is no executable control flow. The constants drive all MMIO and indexed register access in `hw.c`, `hw.h`, `overlay.c`, `tvnv04.c`, `tvnv17.c`, CRTC, DAC, and DFP files.

## State and Persistence Behavior
No software state is stored. The header names hardware state that is read into `nv04_mode_state`, programmed during modesets, or manipulated live by overlay/TV helpers.

## Dependencies and Integration Points
It is included by `hw.h` and display files that need raw register addresses. Values align Nouveau code with historical XFree86/VIDIX/Haiku register knowledge and NVIF MMIO access.

## Risks
Incorrect constants can cause writes to wrong MMIO locations and hardware hangs. Some names are inferred or duplicated, and several bitfields use `high:low` macro syntax that only works with Nouveau helper macros. Shared offsets such as NV04 PVIDEO versus NV10 PVIDEO require chipset-aware callers.

## Test Signals
Build coverage plus hardware smoke tests for modeset, palette, cursor, overlay, TV, flat-panel scaling, PLL programming, and suspend/resume provide validation. Static checks for duplicate or changed constants are also useful when syncing with upstream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv04/nvreg.h -->
