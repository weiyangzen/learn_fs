# sources/distributed-fs/ceph-client/drivers/video/fbdev/aty/atyfb.h

## Purpose
`atyfb.h` provides shared core definitions for the ATI Mach64 fbdev driver family. It defines mode, PLL, DAC, acceleration, interrupt, and device-private data structures plus inline MMIO accessors used by Mach64 implementation files.

## Important APIs, types, and functions
Major types are `struct crtc`, `struct aty_interrupt`, `struct pll_info`, `PLL_BLOCK_MACH64`, `struct pll_514`, `struct pll_18818`, `struct pll_ct`, `union aty_pll`, and `struct atyfb_par`. Feature flags are exposed as `M64F_*` bits with `M64_HAS(feature)`. Register accessors are `aty_ld_le32()`, `aty_st_le32()`, `aty_st_le16()`, `aty_ld_8()`, and `aty_st_8()`. Operation tables are `struct aty_dac_ops` and `struct aty_pll_ops`. Acceleration helpers include inline `wait_for_fifo()` and `wait_for_idle()` plus external `aty_reset_engine()`, `aty_init_engine()`, `atyfb_copyarea()`, `atyfb_fillrect()`, and `atyfb_imageblit()`.

## Control flow
This header has no top-level execution. Included implementation files populate `struct atyfb_par`, call DAC/PLL operation tables to translate and program modes, use accessors for register I/O, and use FIFO/idle wait helpers before accelerated commands.

## State and persistence behavior
The state layout in `struct atyfb_par` persists per framebuffer instance: pseudo palette, hardware palette, selected DAC/PLL ops, MMIO base, CRTC/PLL state, timing limits, feature flags, memory and bus metadata, acceleration flags, sleep/blank flags, resource ranges, PCI device, optional SPARC mapping state, optional LCD BIOS data, IRQ state, write-combining cookie, and saved CRTC/PLL for power management.

## Dependencies and integration points
The header depends on Linux I/O, spinlock, waitqueue, PCI, fbdev types via includers, ATI register definitions, and architecture-specific Atari or generic I/O primitives. It declares external DAC, PLL, LCD, cursor, and acceleration symbols implemented in sibling Mach64 files.

## Risks and edge cases
The inline register accessors apply a register-index adjustment for values above `0x400`, which must match the hardware aperture layout. The `aty_st_le16()` generic path uses `writel()` with a 16-bit value, which is intentional or historical but surprising. FIFO wait loops spin without timeout, so a wedged engine can hang callers. The private state is large and conditionally compiled, so feature additions must preserve layout expectations across configs.

## Test signals
Compile Mach64 variants with Atari, SPARC, generic LCD, cursor, acceleration, and PM options. Runtime signals include successful register I/O, mode programming through DAC/PLL ops, accelerated fill/copy/image operations, interrupt-driven vblank state, suspend/resume restoring saved CRTC/PLL, and no hangs in FIFO/idle waits under acceleration stress.
