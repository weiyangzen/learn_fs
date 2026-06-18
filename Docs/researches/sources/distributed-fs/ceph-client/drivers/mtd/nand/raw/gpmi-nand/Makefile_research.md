# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/gpmi-nand/Makefile

## Purpose
Builds the i.MX/Freescale GPMI NAND controller driver object when `CONFIG_MTD_NAND_GPMI_NAND` is enabled.

## APIs, Flow, And State
The file exposes one Kbuild rule: `obj-$(CONFIG_MTD_NAND_GPMI_NAND) += gpmi-nand.o`. Kbuild turns the configuration symbol into either inclusion in the built-in object list, module object list, or no build. It has no runtime state and no persistence beyond build outputs.

## Dependencies And Integration Points
Depends on the surrounding kernel Kbuild system and the `CONFIG_MTD_NAND_GPMI_NAND` Kconfig symbol. It integrates the `gpmi-nand.c` compilation unit with headers in the same directory (`gpmi-nand.h`, `gpmi-regs.h`, `bch-regs.h`).

## Risks
The rule is intentionally minimal. The main risk is name drift if the C file or Kconfig symbol changes; the driver would silently stop building or fail Kbuild resolution.

## Test Signals
Build tests should confirm that enabling `CONFIG_MTD_NAND_GPMI_NAND=y` or `=m` compiles `gpmi-nand.o` and links/registers the `gpmi-nand` platform driver, while disabling the symbol omits it.
