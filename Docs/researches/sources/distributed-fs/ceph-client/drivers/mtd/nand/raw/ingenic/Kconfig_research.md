# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Kconfig

Purpose: this Kconfig file declares build-time options for the Ingenic JZ47xx NAND controller and its companion ECC/BCH engines.

Important APIs, types, and functions: the user-visible root symbol is `MTD_NAND_JZ4780`, a tristate driver option depending on `MIPS || COMPILE_TEST` and `JZ4780_NEMC`. Inside that option, `MTD_NAND_INGENIC_ECC` is a hidden bool selected by the three ECC engines. User-visible ECC engine modules are `MTD_NAND_JZ4740_ECC`, `MTD_NAND_JZ4725B_BCH`, and `MTD_NAND_JZ4780_BCH`.

Control flow: selecting `MTD_NAND_JZ4780` enables the Ingenic NAND controller menu region. Selecting any hardware ECC engine selects the common `MTD_NAND_INGENIC_ECC` helper so `ingenic_ecc.c` is linked into the controller object. The SoC-specific ECC choices remain independent tristates, allowing ECC providers to be built as modules such as `jz4740-ecc`, `jz4725b-bch`, or `jz4780-bch`.

State and persistence: there is no runtime state. The persistent effect is kernel configuration: whether the NEMC-backed NAND controller and each ECC provider are built in, built as modules, or absent.

Dependencies and integration points: this file integrates the Ingenic drivers with Kbuild and with the broader raw NAND menu. The controller option depends on the external memory controller support (`JZ4780_NEMC`) because `ingenic_nand_drv.c` asserts banks through that API.

Risks: the menu is nested under `MTD_NAND_JZ4780`, even though the driver also has compatibles for JZ4740 and JZ4725B. That naming can be misleading for older SoC users. Hardware ECC support must be selected separately from the NAND controller, so DTs requesting an `ecc-engine` can still probe-defer or fail if the matching ECC provider is missing.

Test signals: configuration tests should verify that each ECC symbol selects `MTD_NAND_INGENIC_ECC`, that module names match help text, and that `ingenic_nand.o` links with or without the common ECC helper according to selected symbols.
