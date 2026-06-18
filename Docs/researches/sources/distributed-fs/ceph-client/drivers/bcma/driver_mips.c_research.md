# sources/distributed-fs/ceph-client/drivers/bcma/driver_mips.c

Purpose: this file initializes the BCMA Broadcom MIPS core support, including IRQ routing, CPU clock reporting, boot flash detection for NVRAM, serial setup, and chip-specific interrupt quirks.

Important APIs, types, and functions: exported APIs are `bcma_core_mips_irq`, `bcma_cpu_clock`, `bcma_core_mips_early_init`, and `bcma_core_mips_init`. Internal helpers include quirk detectors for BCM47162A0 and BCM5357B0, `bcma_core_mips_irqflag`, `bcma_core_mips_set_irq`, `bcma_core_mips_set_irq_name`, IRQ dump/print helpers, `bcma_boot_dev`, `bcma_core_mips_nvram_init`, and `bcma_fix_i2s_irqflag`. `enum bcma_boot_dev` classifies ROM, parallel, serial, NAND, and unknown boot sources.

Control flow: IRQ lookup reads or synthesizes an OOB IRQ flag, maps it through MIPS74K interrupt mask registers, and returns logical states for assigned, disabled, or unsupported. IRQ assignment clears old masks, evicts an existing user of a target IRQ to IRQ0 when needed, writes the new mask, and updates `dev->irq` to Linux IRQ number `irq + 2`. Early init initializes ChipCommon serial ports and NVRAM source based on boot device. Full init applies the I2S IRQ fixup, then routes IRQs for known chip families or falls back to `bcma_core_irq` and logs an unknown-device error.

State and persistence: state is in `mcore->early_setup_done`, `mcore->setup_done`, each `core->irq`, MIPS interrupt mask registers, OOB selector registers, and NVRAM initialization state when `CONFIG_BCM47XX` is enabled.

Dependencies and integration points: it depends on ChipCommon PMU clock helpers, BCMA core lookup, ChipCommon serial init, BCM47xx NVRAM initialization, public chip/core IDs, and MIPS interrupt register definitions.

Risks: IRQ routing is chip-table-driven and can break devices if a core ID/unit mapping is wrong. Some DMP register reads hang on known revisions, so quirk guards must be preserved. Unknown chip fallback logs an error and may still produce usable but suboptimal IRQs. NVRAM source detection depends on boot flash state and compile-time BCM47XX support.

Test signals: serial port availability, NVRAM load success, correct per-core IRQs, absence of interrupt storms, and debug IRQ dumps on supported chips are primary signals. Hardware tests should include the listed BCM4716/4748/5356/47162/53572/5357/4749/4706 families.
