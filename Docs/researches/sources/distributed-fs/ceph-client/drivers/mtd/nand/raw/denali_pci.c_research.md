# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/denali_pci.c

Purpose: this PCI wrapper binds Intel CE4100 and Moorestown Denali/Spectra NAND PCI functions to the shared Denali core. It enables PCI resources, maps controller and host windows, supplies fixed clock rates and PCI ECC capabilities, initializes the core, and registers one NAND chip spanning all detected Denali banks.

Important APIs, types, and functions: `denali_pci_ids` matches Intel device IDs `0x0701` and `0x0809` with wrapper-specific BAR layout handling. `NAND_ECC_CAPS_SINGLE(denali_pci_ecc_caps, denali_calc_ecc_bytes, 512, 8, 15)` supplies supported ECC choices. The lifecycle functions are `denali_pci_probe()` and `denali_pci_remove()`.

Control flow: probe allocates a `denali_controller`, enables the PCI device with managed PCI helpers, selects CSR and host memory windows according to CE4100 versus other layout, enables bus mastering, sets IRQ, ECC caps, and fixed `clk_rate = 50 MHz` / `clk_x_rate = 200 MHz`, requests all PCI regions, maps CSR and host regions, and calls `denali_init()`. It then allocates a `denali_chip` with `nsels = denali->nbanks`, requests maximum ECC strength in the chip user configuration, assigns every bank number in order, and calls `denali_chip_init()`. Remove fetches the controller from PCI drvdata and calls `denali_remove()`.

State and persistence: all wrapper allocations and mappings are devm/pcim-managed. Runtime state lives in the embedded Denali controller and the single allocated `denali_chip`. The wrapper hard-codes clock rates rather than discovering them from PCI config or firmware. PCI bus mastering remains enabled while bound.

Dependencies and integration points: the wrapper depends on PCI core managed enable/resource APIs, Intel PCI IDs, MMIO mapping, the Denali core API, and raw NAND ECC configuration. Unlike the DT wrapper, it does not use reset or clock frameworks and does not parse child topology; every hardware bank becomes a select of one NAND chip object.

Risks: CE4100 BAR handling sets `mem_len` from resource 1 while `mem_base` comes from resource 0, which is unusual and should be validated against hardware documentation. Fixed clock rates must match actual controller integration or SDR timing setup will be wrong. The wrapper registers all banks as one chip with multiple selects; platforms with different physical topology would need a different mapping. No suspend/resume support is provided. DMA capability is whatever the core detects from `FEATURES` plus wrapper caps; PCI-specific DMA constraints are limited to generic mask setup in the core.

Test signals: validate probe on both PCI IDs, BAR layout mapping for CE4100 and Moorestown, IRQ delivery through the shared Denali ISR, bank count detection, one MTD spanning all selects, maximum ECC strength choice, page read/write with DMA and PIO fallback, timing setup using the fixed 50/200 MHz rates, and remove cleanup through `denali_remove()`.
