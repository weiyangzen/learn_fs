# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.c

Purpose: shared Broadcom raw NAND controller core supporting controller revisions v2.1 through v7.3, multiple chip-selects, hardware ECC, OOB layouts, flash-cache PIO, FLASH_DMA, EDU DMA, optional SoC-specific hooks, write protection, and suspend/resume restoration.

Important APIs/types/functions: central state is `struct brcmnand_controller`, `struct brcmnand_host`, `struct brcmnand_cfg`, and `struct brcm_nand_dma_desc`. Public exports are `brcmnand_probe`, `brcmnand_remove`, and `brcmnand_pm_ops`. NAND callbacks are `brcmnand_attach_chip` and `brcmnand_exec_op`. Major helpers cover revision setup, register access, CS offsets, ECC/OOB layout, DMA/EDU, low-level ops, legacy native-command ops, read/write/OOB/raw paths, and PM save/restore.

Control flow: `brcmnand_probe` validates OF, allocates controller state, enables optional non-MMIO access, maps registers/cache, enables the clock, initializes revision capabilities, chooses modern low-level vs legacy instruction handlers, configures FLASH_DMA or EDU, disables auto device ID/XOR, configures WP, requests IRQs, then initializes each `brcm,nandcs` child or platform-data chip-select. Chip initialization assigns ECC operations, forces READID to 8-bit mode, scans NAND, and registers MTD.

Read/write flow: reads prefer DMA/EDU when available and legal; otherwise they issue page-read commands per 512B flash-cache sector and read OOB registers. ECC address/counter registers detect correctable and uncorrectable errors, with erased-page verification on older revisions. Writes disable WP, clear OOB registers, prefer DMA/EDU when possible, otherwise fill flash cache and issue program commands per sector, then restore WP.

State and persistence: controller state includes revision-derived maps, feature flags, DMA/EDU resources, completions, flash-cache buffer for parameter reads, host list, instruction handlers, WP policy, and PM-saved registers. Host state includes CS id and hardware config such as geometry, ECC, timing, ACC_CONTROL, and config registers. Suspend saves CS config, select/xor/threshold, and DMA/EDU mode; resume restores them, re-enables SoC interrupts, and resets chips.

Dependencies/integration: raw NAND/MTD APIs, OF/platform data, clk, DMA mapping, IRQs/completions, static keys, and `brcmnand.h`. Glue drivers provide `struct brcmnand_soc` hooks for IRQs, register IO, data-bus preparation, or custom cache reads.

Risks/test signals: revision-specific offsets, ECC level/sector encoding, OOB layout math, endianness in flash cache/descriptors, DMA/EDU completion and errors, panic-write fallback, WP policy, and legacy vs low-level `exec_op` coverage. Test all revision families, READID/parameter pages, ECC and raw page/OOB I/O, ECC injection, erased-page bitflips, DMA/PIO fallback, suspend/resume, multi-CS, WP transitions, and BBT behavior.
