# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/Kconfig

Purpose: declares OneNAND support and board/controller-specific OneNAND driver options under the NAND menu.

Important APIs and types: symbols include `MTD_ONENAND`, `MTD_ONENAND_VERIFY_WRITE`, `MTD_ONENAND_GENERIC`, `MTD_ONENAND_OMAP2`, `MTD_ONENAND_SAMSUNG`, `MTD_ONENAND_OTP`, and `MTD_ONENAND_2X_PROGRAM`.

Control flow: `MTD_ONENAND` is a `menuconfig` gated by `HAS_IOMEM`; all suboptions are visible only when it is enabled. Generic platform-device support is optional. OMAP2/OMAP3 support requires OF and OMAP GPMC, Samsung support is limited to matching SoCs or compile testing, OTP toggles one-time-programmable support, and 2X program enables a special two-plane programming mode for chips that support it.

State and persistence: no runtime state. The symbols control whether OneNAND core, glue drivers, OTP paths, write verification, and 2X program behavior are compiled.

Dependencies and integration points: maps to `onenand/Makefile`, OneNAND core files, generic platform glue, OMAP/Samsung controller drivers, and MTD partition/device registration at runtime.

Risks and test signals: risks include exposing SoC-specific drivers under wrong architecture constraints or enabling behavioral features without matching chip support. Build tests should cover OneNAND disabled, core only, generic driver as module, OMAP/Samsung compile-test builds, OTP enabled, verify-write enabled, and 2X program enabled.
