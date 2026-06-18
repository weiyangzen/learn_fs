## sources/distributed-fs/ceph-client/drivers/dma/dw/pci.c

Purpose: PCI bus glue for classic DesignWare AHB DMA and Intel iDMA32 variants.

Important APIs/types/functions: `dw_pci_probe()`, `dw_pci_remove()`, system sleep callbacks, PCI ID table mapping Intel device IDs to `dw_dma_chip_pdata`, `idma32_chip_pdata`, or `xbar_chip_pdata`, and `module_pci_driver()`.

Control flow: probe enables the PCI device, maps BAR0, sets bus master/MWI, configures a 32-bit DMA mask, duplicates match data, allocates `dw_dma_chip`, fills device/id/register/IRQ/pdata fields, invokes the selected variant probe, stores driver data, and registers ACPI DMA lookup. Remove unregisters ACPI lookup and calls variant remove. Suspend/resume disable/enable the core through shared helpers.

State and persistence: per-device match-data copy holds the chip pointer and variant metadata. Mapped PCI BAR and IRQ remain owned during driver binding.

Dependencies and integration: integrates PCI, ACPI DMA helpers, shared core, and variant-specific pdata for Intel SoCs.

Risks and test signals: wrong PCI ID mapping selects wrong register variant or master IDs; 32-bit DMA mask limits clients; suspend/resume assumes registers are accessible. Test all listed Intel IDs, ACPI client lookup, DMA transfer after resume, remove cleanup, and BAR/IRQ failure paths.
