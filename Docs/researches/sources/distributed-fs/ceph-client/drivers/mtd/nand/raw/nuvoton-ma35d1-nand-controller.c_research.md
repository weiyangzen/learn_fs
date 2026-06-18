# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nuvoton-ma35d1-nand-controller.c

Purpose: this is the Nuvoton MA35D1 NAND controller driver. It implements an `exec_op` raw NAND controller with DMA-backed full-page transfers, hardware BCH ECC for 2K/4K/8K pages, redundant-area management, IRQ completion, and Device Tree child-chip registration.

Important APIs, types, and functions: `struct ma35_nand_info` holds controller state, MMIO registers, clock, IRQ, completion, shared DMA buffer, and chip list. `struct ma35_nand_chip` embeds `nand_chip` and chip-select metadata. Key functions are `ma35_nand_attach_chip()`, `ma35_nfc_exec_op()`, `ma35_nand_do_read()`, `ma35_nand_do_write()`, `ma35_nfi_ecc_check()`, `ma35_nfi_correct()`, and the HWECC page/subpage/OOB callbacks.

Control flow: probe allocates the controller, maps registers, enables `nand_gate`, requests the IRQ, globally resets/enables NAND hardware, disables write protect, and scans child nodes. Each child validates `reg` chip selects, prevents duplicate CS assignment, sets the flash node and OOB layout, runs `nand_scan()`, and registers MTD. Attach rejects 16-bit bus, programs page-size bits, wires ON_HOST ECC callbacks when selected, configures BCH strength 8/12/24, parity byte counts, redundant-area size, and DMA/subpage options.

State and persistence: persistent driver state includes the child chip list, assigned chip-select bitmap, completion object, and shared page buffer. Hardware state includes NANDCTL page/ECC/DMA bits, redundant-area registers, DMA source address, interrupt status/enables, and ECC result/address/data registers. Remove unregisters all MTDs and cleans NAND chips; devm handles MMIO/clock/IRQ allocations.

Dependencies and integration points: the driver uses raw NAND controller ops, MTD OOB layout APIs, DMA mapping, platform IRQs, completions, common clocks, OF child nodes, and MA35 NFI registers. It integrates with NAND core page helpers for command sequencing and uses controller-specific redundant-area registers for OOB/ECC bytes.

Risks: full-page DMA is required for page-sized transfers, with one-second timeout handling. ECC correction mutates both data and redundant-area registers based on hardware error addresses; parity offset math must match BCH mode. Prefix-empty redundant-area detection treats pages as erased. The probe error path manually disables a devm-enabled clock, which is worth reviewing in lifecycle tests.

Test signals: validate 2K/4K/8K page setup, BCH8/12/24 parity totals, DMA read/write completions and timeouts, ECC corrected/uncorrectable paths, subpage write masks, OOB layout and redundant-area reads, empty-page detection, wait-ready polling via `INT_RB0`, duplicate/invalid chip selects, and remove cleanup.
