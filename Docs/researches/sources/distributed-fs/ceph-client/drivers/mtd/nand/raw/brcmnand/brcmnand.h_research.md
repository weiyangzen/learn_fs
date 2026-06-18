# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.h

Purpose: exported interface between Broadcom NAND platform glue drivers and the shared `brcmnand.c` core.

Important APIs/types/functions: `struct brcmnand_soc` provides optional hooks for controller-ready IRQ ack/enable, data-bus prepare/unprepare, custom data-bus reads, and custom register IO. `struct brcmnand_io_ops` defines non-MMIO `read_reg`/`write_reg`. Inline helpers wrap SoC hooks and endian-safe `brcmnand_readl`/`brcmnand_writel`. Exported core API is `brcmnand_probe`, `brcmnand_remove`, and `brcmnand_pm_ops`.

Control flow: glue drivers populate `brcmnand_soc` and pass it to `brcmnand_probe`. The core calls hooks during IRQ handling, data/parameter access, flash-cache reads, and non-MMIO register access.

State and persistence: no header storage, but hook structs define persistent glue state. `BRCMNAND_NON_MMIO_FC_ADDR` is a sentinel offset for non-MMIO flash-cache access.

Dependencies/integration: Linux types and IO helpers; included by all brcmnand core/glue files.

Risks/test signals: incomplete IO ops, endian mismatch on MIPS big-endian systems, and misuse of the flash-cache sentinel. Test each glue driver, BCMA non-MMIO path, big-endian MIPS access, and PM ops.
