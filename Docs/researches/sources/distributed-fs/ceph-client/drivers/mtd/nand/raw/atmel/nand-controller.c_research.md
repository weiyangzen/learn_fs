# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/nand-controller.c

Purpose: Atmel/Microchip raw NAND controller driver for older SMC-attached NAND and newer HSMC/NFC controllers, including legacy Device Tree bindings. It connects Linux raw NAND `exec_op`, MTD registration, SMC timing setup, optional DMA, ready/busy handling, and the PMECC hardware ECC engine.

Important APIs/types/functions: core state is split among `struct atmel_nand_controller`, `struct atmel_smc_nand_controller`, `struct atmel_hsmc_nand_controller`, `struct atmel_nand`, and `struct atmel_nand_cs`. Capability tables select offsets, DMA support, legacy parsing, and operation sets. Main callbacks are `atmel_nand_attach_chip`, `atmel_nand_setup_interface`, `atmel_nand_exec_op`, `atmel_smc_nand_exec_op`, `atmel_hsmc_nand_exec_op`, and PMECC read/write helpers.

Control flow: probe resolves controller caps, upgrades legacy matches when old properties imply a different controller, initializes PMECC/DMA/clocks/regmaps, then adds child NAND chips. SMC operations write command/address/data directly through memory windows. HSMC operations parse NAND subops into NFC command/address/data transfers, use NFC SRAM for optimized page access, and wait by IRQ or polling.

State and persistence: persistent state includes active CS, cached HSMC config, per-CS SMC timing, PMECC users, DMA channel, and MTD registrations. Suspend/resume resets PMECC and all NAND targets but does not persist flash data.

Dependencies/integration: raw NAND/MTD, GPIO, DMA engine, regmap/syscon, clocks, Atmel SMC/HSMC helpers, OF parsing, genalloc SRAM, and `pmecc.h`.

Risks/test signals: timing calculation, legacy binding compatibility, DMA fallback, HSMC interrupt/error handling, native R/B, raw-vs-ECC PMECC paths. Test with probe on SMC/HSMC SoCs, read/write/erase, raw OOB, ECC injection, suspend/resume, DMA disabled, and GPIO/native R/B DT variants.
