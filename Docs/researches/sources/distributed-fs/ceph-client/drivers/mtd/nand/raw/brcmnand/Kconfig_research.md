# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Kconfig

Purpose: declares the Broadcom NAND controller core and SoC glue options for BCM63xx, BCMA, BCMBCA, BRCMSTB, and iProc platforms.

Important APIs/types/functions: `MTD_NAND_BRCMNAND` is the core tristate and depends on supported architectures or `COMPILE_TEST` plus `HAS_IOMEM`. Child tristates are `MTD_NAND_BRCMNAND_BCM63XX`, `_BCMA`, `_BCMBCA`, `_BRCMSTB`, and `_IPROC`.

Control flow: build-time only. Selected symbols decide which platform glue drivers are compiled and can call `brcmnand_probe`.

State and persistence: no runtime state; choices persist in kernel `.config`.

Dependencies/integration: BCMA glue depends on `BCMA_NFLASH` and `BCMA`; other glue options default to platform architecture symbols.

Risks/test signals: missing dependencies and incorrect defaults. Test all module/built-in combinations, especially core-only and each glue plus core.
