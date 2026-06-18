# sources/distributed-fs/ceph-client/drivers/mtd/nand/Makefile

Purpose: maps NAND Kconfig selections to build objects for the generic NAND core, optional ECC engines, Qualcomm shared code, and NAND family subdirectories.

Important APIs and types: `nandcore-objs := core.o bbt.o` builds the base framework. Conditional additions include `ecc.o`, `ecc-sw-hamming.o`, `ecc-sw-bch.o`, and `ecc-mxic.o` into `nandcore`, while MediaTek and Realtek hardware ECC are separate objects. Subdirectories `onenand/`, `raw/`, and `spi/` are always visited through `obj-y`.

Control flow: `obj-$(CONFIG_MTD_NAND_CORE) += nandcore.o` gates the generic framework. `nandcore-$(CONFIG_...)` composes built-in framework pieces based on ECC options. Separate platform-driver ECC engines are emitted as their own modules/objects. `qpic_common.o` is shared by SPI QPIC SNAND and raw Qualcomm NAND configs.

State and persistence: no runtime state. Build products determine which exported NAND symbols and platform drivers are present.

Dependencies and integration points: tied to symbols declared in `drivers/mtd/nand/Kconfig` and subdirectory Kconfigs. The object grouping matters because software ECC helpers and generic ECC code become part of `nandcore`, while on-host platform engines can probe independently.

Risks and test signals: risks include unresolved symbols if ECC helper objects are excluded incorrectly, duplicate inclusion of shared QPIC code, or missing subdirectory traversal. Test signals are successful builds for core-only, software BCH/Hamming, MXIC as core-integrated support, MediaTek/Realtek module builds, and combinations of QPIC configs.
