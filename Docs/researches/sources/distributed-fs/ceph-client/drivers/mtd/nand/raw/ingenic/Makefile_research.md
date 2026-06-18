# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Makefile

Purpose: this Makefile maps the Ingenic raw NAND Kconfig symbols to build products.

Important APIs, types, and functions: `obj-$(CONFIG_MTD_NAND_JZ4780) += ingenic_nand.o` builds the main controller object. `ingenic_nand-y` always includes `ingenic_nand_drv.o`, while `ingenic_nand-$(CONFIG_MTD_NAND_INGENIC_ECC)` conditionally folds in `ingenic_ecc.o`. The SoC ECC providers are separate module objects: `jz4740_ecc.o`, `jz4725b_bch.o`, and `jz4780_bch.o`.

Control flow: Kbuild creates a composite `ingenic_nand.o` for the controller. If hardware ECC support is enabled, the common ECC provider API is compiled into that composite. Each SoC ECC implementation is built according to its own tristate, which lets the ECC provider modules register separately and be resolved through DT phandles at runtime.

State and persistence: there is no runtime state. Build state is reflected in which object files are linked into the kernel or emitted as modules.

Dependencies and integration points: this file must stay consistent with `Kconfig` and with symbol usage in `ingenic_nand_drv.c`, `ingenic_ecc.c`, and the three provider files. The composite object arrangement matters because `ingenic_nand_drv.c` calls `of_ingenic_ecc_get()` through either real functions or header stubs.

Risks: if `CONFIG_MTD_NAND_INGENIC_ECC` is disabled but a board expects hardware ECC, the header stubs return `-ENODEV` and the NAND controller probe fails when it requires `ecc-engine`. If a SoC ECC module is not loaded early enough, `of_ingenic_ecc_get()` reports `-EPROBE_DEFER` until the provider probes.

Test signals: build tests should cover all built-in/module combinations: NAND without ECC helper, NAND with each ECC provider built in, and NAND with ECC providers as modules.
