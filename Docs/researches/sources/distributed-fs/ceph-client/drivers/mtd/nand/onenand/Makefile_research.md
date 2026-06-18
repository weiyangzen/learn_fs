# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Makefile

Purpose: builds the OneNAND core and optional board/controller-specific glue drivers.

Important APIs and types: `obj-$(CONFIG_MTD_ONENAND) += onenand.o` builds the core aggregate, while `obj-$(CONFIG_MTD_ONENAND_GENERIC)`, `obj-$(CONFIG_MTD_ONENAND_OMAP2)`, and `obj-$(CONFIG_MTD_ONENAND_SAMSUNG)` include `generic.o`, `onenand_omap2.o`, and `onenand_samsung.o`. `onenand-objs = onenand_base.o onenand_bbt.o` composes the core object.

Control flow: the Makefile follows Kconfig selection directly. Enabling base OneNAND compiles base operations and OneNAND bad-block-table support; platform glue is independent and conditional.

State and persistence: no runtime state. Build outputs determine which OneNAND platform drivers and core symbols are present.

Dependencies and integration points: tied to `onenand/Kconfig`, core OneNAND APIs in `<linux/mtd/onenand.h>`, and platform drivers that register MTD devices.

Risks and test signals: risks are mostly build integration failures: missing core object pieces, glue objects built without core dependencies, or module link errors. Test signals are successful builds for built-in and module variants of `MTD_ONENAND`, plus each optional glue driver.
