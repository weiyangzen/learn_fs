# sources/distributed-fs/ceph-client/drivers/ata/ahci_qoriq.c

Purpose: Freescale/NXP QorIQ AHCI driver programming PHY, transaction, AXI/coherency, and ECC-disable registers with an LS1021A hard-reset erratum workaround.

Important APIs/types: `enum ahci_qoriq_type`, `struct ahci_qoriq_priv`, `ecc_initialized`, `ahci_qoriq_hardreset`, `ahci_qoriq_phy_init`, `ahci_qoriq_probe`, and `ahci_qoriq_resume`.

Control flow: probe gets resources, determines SoC type from OF/ACPI, maps optional `sata-ecc`, records DMA coherency, enables resources, runs PHY init, and activates. PHY init writes SoC constants and ECC disable bits; resume repeats init before host resume. Hard reset saves/restores `PORT_CMD` and `PORT_IRQ_STAT` on LS1021A.

State/persistence: SoC type, ECC address, DMA coherency flag, global ECC initialization guard, ECC/PHY/transaction/AXI registers, and reset-saved port state.

Dependencies/integration: OF/ACPI, platform resources, `ahci_platform`, libata reset helpers, DMA attributes, PM runtime.

Risks/test signals: global `ecc_initialized` affects multi-controller ordering; missing ECC resource can fail SoCs requiring it. Test ECC setup once, DMA-coherent AXI config, LS1021A reset, resume, and NCQ.
