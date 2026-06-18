<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tgafb.h -->
# sources/distributed-fs/ceph-client/include/video/tgafb.h

## Purpose
This header defines DEC 21030 TGA framebuffer hardware constants, RAMDAC register programming helpers, and driver-private display state.

## Important APIs, Types, And Functions
- `TGA_TYPE_8PLANE`, `TGA_TYPE_24PLANE`, and `TGA_TYPE_24PLUSZ` classify framebuffer variants.
- Offsets define ROM, registers, 8-plane/24-plane/24+Z framebuffer bases, TGA control registers, copy engines, clock and RAMDAC access.
- Timing masks define horizontal/vertical register composition.
- RAMDAC constants cover BT485, BT463, and BT459 register/address spaces.
- `struct tga_par` stores device pointer, mapped memory/register/framebuffer bases, type/revision, blank state, mode timing, PLL frequency, bpp, sync-on-green, and palette.
- Inline helpers `TGA_WRITE_REG`, `TGA_READ_REG`, `BT485_WRITE`, `BT463_LOAD_ADDR`, `BT463_WRITE`, `BT459_LOAD_ADDR`, and `BT459_WRITE` perform MMIO/RAMDAC accesses.

## Control Flow
The driver maps TGA memory, selects the framebuffer offset and RAMDAC path by `tga_type`, computes timing/PLL registers, writes display and RAMDAC registers through the inline helpers, and uses valid/blank/cursor bits to control output.

## State And Persistence
Persistent state is in `tga_par`, MMIO registers, RAMDAC palettes/cursor registers, and framebuffer memory. `vesa_blanked` caches current blanking mode while actual blank/video/cursor state is hardware-resident.

## Dependencies And Integration Points
It integrates with fbdev, Linux device infrastructure, MMIO `readl`/`writel`, DEC TGA hardware, and RAMDAC-specific mode/palette/cursor setup.

## Risks And Edge Cases
Wrong RAMDAC path or framebuffer offset for a TGA type will write the wrong device region. Timing masks split active/back/front/sync fields and require exact composition. Inline MMIO helpers have no locking, so callers must serialize register access where needed.

## Test Signals
Expected signals include correct variant detection, stable 8-plane and 24-plane modes, working palette/cursor writes for BT485/BT463/BT459, valid blank/unblank state, and successful copy/fill paths where implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/tgafb.h -->
