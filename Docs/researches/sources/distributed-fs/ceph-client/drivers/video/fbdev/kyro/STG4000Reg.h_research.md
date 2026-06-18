
# sources/distributed-fs/ceph-client/drivers/video/fbdev/kyro/STG4000Reg.h

Purpose: STG4000 register map and bit-manipulation support for the Kyro framebuffer driver.

Important content: defines `STG_WRITE_REG()` and `STG_READ_REG()` around `writel/readl`, bit helpers `SET_BIT`, `CLEAR_BIT`, and range-clearing macros, enums for LUT use, primary pixel formats, overlay blend modes, and overlay pixel formats, plus the large `STG4000REG` struct mapping device registers and reserved gaps from thread/core controls through TA/3D/SDRAM and DAC/overlay/video-port registers.

Control flow and integration: all STG4000 helper C files take a local parameter named `pSTGReg`, allowing the register macros to expand directly. `fbdev.c` maps PCI BAR1 to `STG4000REG __iomem *` and passes it into helper functions.

State and persistence: no software state, but this struct defines the persistent MMIO register address space used for resets, PLL programming, RAMDAC setup, VTG timing, overlay, stream control, SDRAM config, and interrupts.

Dependencies: kernel builds include `<asm/page.h>` and `<asm/io.h>` for MMIO access. The macros assume a visible variable `tmp` for clear operations, which is a non-obvious local naming contract in callers.

Risks: C bitfield-clearing macros loop over bit indexes and mutate `tmp` or `usTemp` by name, making them fragile and side-effect prone. The register struct must match hardware offsets exactly; padding errors corrupt all downstream accesses. `volatile` plus `__iomem` typing is old style and limits static checking.

Test signals: compile all helpers with sparse where possible, compare `offsetof(STG4000REG, member)` against hardware documentation for critical registers, and smoke-test mode set/overlay paths that cover DAC, VTG, PLL, and SDRAM fields.
