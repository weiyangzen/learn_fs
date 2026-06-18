# sources/distributed-fs/ceph-client/drivers/video/fbdev/savage/savagefb.h

Purpose: shared private header for the S3 Savage fbdev driver. It defines PCI IDs, chipset group helpers, MMIO/BCI constants, display-type tags, timing/register snapshots, the driver's private state, VGA/MMIO accessors, optional acceleration stubs, and cross-file function prototypes.

Important APIs/types/functions: `savage_chipset` classifies hardware families. `struct xtimings` holds derived mode timing. `struct savage_reg` stores VGA, S3 extended, streams, and MIU register snapshots for mode programming and restore. `struct savagefb_i2c_chan` stores the optional DDC adapter. `struct savagefb_par` is the persistent per-device state used by all Savage source files. Inline helpers such as `savage_in/out*`, `vga_in/out*`, `VGArCR`, `VGAwCR`, `VGAenablePalette`, and `VerticalRetraceWait` centralize register access.

Control flow: this header does not own a runtime sequence, but its inline helpers are the primitive operations used by probe, mode setting, acceleration, blanking, and I2C. `BCI_SEND` advances `par->bci_ptr` while writing command words, so acceleration control flow depends on resetting `bci_ptr` before command emission.

State and persistence: `struct savagefb_par` persists PCI device pointer, chipset, DDC channel, current/saved/initial register snapshots, VGA state for open/release restore, open count, PM state, display type, clocks, mapped video/MMIO resources, BCI command buffer pointers, wait callbacks, panel dimensions, software palette cache, current depth, and virtual width.

Dependencies and integration: included by `savagefb_driver.c`, `savagefb-i2c.c`, and `savagefb_accel.c`. It depends on Linux I2C, mutex, VGA, fbdev EDID support, MMIO accessors, and Kconfig symbols `CONFIG_FB_SAVAGE_ACCEL` and `SAVAGEFB_DEBUG`.

Risks: macros perform unguarded MMIO writes and some, like `BCI_SEND`, have side effects. `vga_in32` returns `u8` despite using `savage_in32`, which is suspicious if ever used for 32-bit data. Busy-wait loops in `VerticalRetraceWait` and wait callbacks can hang on broken hardware. The header couples optional modules tightly to the exact private structure layout.

Test signals: compile all Savage configurations, run mode setting and acceleration paths that exercise BCI macros, I2C paths that use `struct savagefb_i2c_chan`, PM/open-release restore using register snapshots, and static analysis for inline type mismatches.
