# sources/distributed-fs/ceph-client/drivers/mtd/nand/Kconfig

Purpose: defines the top-level NAND Kconfig menu and selects the generic NAND core, NAND family submenus, and ECC engine options.

Important APIs and types: configuration symbols include `MTD_NAND_CORE`, `MTD_NAND_ECC`, `MTD_NAND_ECC_SW_HAMMING`, `MTD_NAND_ECC_SW_HAMMING_SMC`, `MTD_NAND_ECC_SW_BCH`, `MTD_NAND_ECC_MXIC`, `MTD_NAND_ECC_MEDIATEK`, and `MTD_NAND_ECC_REALTEK`. It sources OneNAND, raw NAND, and SPI-NAND Kconfig trees.

Control flow: enabling a NAND family can select or depend on `MTD_NAND_CORE`. ECC symbols select `MTD_NAND_ECC`, which in turn selects core support. Software Hamming defaults on with raw NAND, while BCH and hardware engines are opt-in. Hardware engines constrain builds with `HAS_IOMEM`, SoC architecture predicates, `HAS_DMA` for Realtek, or `COMPILE_TEST`.

State and persistence: this file has no runtime state. Its persistent effect is build-time feature selection that controls which NAND framework and ECC drivers are compiled.

Dependencies and integration points: integrates the generic NAND build with `drivers/mtd/nand/onenand`, `raw`, and `spi`. It maps directly to object inclusion in the sibling Makefile and indirectly to device-tree compatible drivers at runtime.

Risks and test signals: regressions appear as missing objects, invalid dependencies, or unusable ECC choices. Build tests should cover allnoconfig fragments for software-only NAND, raw NAND default Hamming, each hardware ECC under `COMPILE_TEST`, Realtek with DMA availability, and SmartMedia byte-order Hamming only when Hamming is enabled.
