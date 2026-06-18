## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_base.h

Purpose: `matroxfb_base.h` is the core internal header for the Matrox fbdev driver family. It defines debug controls, MMIO helpers, timing/PLL/output/state structures, the main `matrox_fb_info` object, the low-level switch interface, extension-driver API, register constants, endian-dependent accelerator opmodes, lock macros, and exported base helpers.

Important APIs and types: key types are `vaddr_t`, `my_timming`, `matrox_pll_cache`, `matrox_pll_limits`, `matrox_pll_features`, `matrox_hw_state`, `matrox_accel_data`, `matrox_altout`, `matrox_bios`, `matrox_vsync`, `matrox_fb_info`, `matrox_switch`, and `matroxfb_driver`. Important inline helpers wrap `readb/writeb/readl/writel`, `mga_memcpy_toio()`, and virtual address arithmetic. Register constants cover drawing engine, VGA, DAC, interrupt, CRTC2, and PCI option registers.

Control flow: no full runtime flow, but macros and inlines define how all Matrox modules perform MMIO, wait for FIFO/idle, lock DAC/accelerator sections, and access `matrox_fb_info` from `fb_info`. `matrox_switch` formalizes the preinit/reset/init/restore lifecycle used by the base driver.

State and persistence: the header describes nearly all persistent per-device state. `matrox_fb_info` contains live fbdev state, hardware shadow registers, PCI device, vsync wait queues/counters, output routing, registered extension modules, video/MMIO mappings, feature limits, locks, chip/capability/devflag state, BIOS/PINS data, PLL caches, G450 register values, and a 16-entry pseudo-palette.

Dependencies and integration points: includes broad kernel subsystems: fbdev, PCI, console/selection, timers, spinlocks, I/O, unaligned access, and optional PowerMac `macmodes.h`. Every Matrox source in this subset includes it directly or indirectly, making it the internal ABI boundary.

Risks: because this header exposes hardware registers and full mutable state to all modules, invariants are convention-based. Some macros are busy-wait loops without timeouts (`mga_fifo`, `WaitTillIdle`). Optional spinlock protection is compile-time disabled by default. Endian opmode handling has TODOs for some bpp combinations. Layout changes to `matrox_fb_info` affect extension modules that store pointers and call back into base fbops.

Test signals: compile all Matrox config combinations on little- and big-endian targets, with and without Millennium/G/Mystique/I2C/MAVEN. Runtime tests should stress MMIO wrappers, acceleration idle waits, DAC locking under concurrent mode/palette/I2C activity, and extension-driver registration/removal. Static analysis should flag direct hardware access that bypasses required locks.
