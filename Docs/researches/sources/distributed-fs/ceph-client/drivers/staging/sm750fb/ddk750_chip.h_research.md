# sources/distributed-fs/ceph-client/drivers/staging/sm750fb/ddk750_chip.h

Purpose: declares SM750 chip helper APIs, chip and clock enums, PLL/init structures, and MMIO read/write helpers.

Important APIs/types/functions: `DEFAULT_INPUT_CLOCK`, `SM750LE_REVISION_ID`, external `void __iomem *mmio750`, inline `peek32()`/`poke32()`, `enum logical_chip_type`, `enum clock_type`, `struct pll_value`, `struct initchip_param`, and prototypes for chip type, PLL, framebuffer memory, and hardware init functions.

Control flow: inline MMIO helpers add register offsets to `mmio750` and call `readl()`/`writel()`. Other declarations are implemented by `ddk750_chip.c`.

State and persistence: `mmio750` is an externally owned mapped MMIO base that must remain valid for every helper using `peek32()`/`poke32()`. Init parameters describe desired hardware state but are caller-owned.

Dependencies and integration: includes Linux I/O, ioport, and uaccess headers plus SM750 register definitions. Used by chip, power, display, mode, acceleration, and core framebuffer setup code.

Risks: no null or bounds checks on `mmio750`; calling helpers before mapping MMIO can fault. `struct initchip_param` uses small integer MHz fields and flag semantics that callers must fill correctly.

Test signals: compile users of all prototypes, validate MMIO base setup before calls, and test init parameters across zero/no-change and nonzero clock values.
