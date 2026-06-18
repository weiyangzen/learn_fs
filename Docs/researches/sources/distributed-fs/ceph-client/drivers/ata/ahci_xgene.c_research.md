# sources/distributed-fs/ceph-client/drivers/ata/ahci_xgene.c

Purpose: APM X-Gene AHCI driver for v1/v2 controllers with IP RAM release, mux selection, PHY/channel setup, coherency/error registers, broken edge IRQ handling, PMP/FBS errata, IDENTIFY/SMART engine restart, and DEVSLP masking.

Important APIs/types: `struct xgene_ahci_context`, `xgene_ahci_init_memram`, `xgene_ahci_restart_engine`, `xgene_ahci_qc_issue`, `xgene_ahci_read_id`, `xgene_ahci_set_phy_cfg`, `xgene_ahci_hardreset`, `xgene_ahci_softreset`, `xgene_ahci_pmp_softreset`, `xgene_ahci_irq_intr`, `xgene_ahci_hw_init`, `xgene_ahci_mux_select`, `xgene_ahci_probe`.

Control flow: probe gets AHCI and extra core/diag/AXI/optional mux MMIO, determines version from OF/ACPI, selects SATA mux, optionally skips already-initialized RAM, otherwise toggles clocks, enables resources, releases RAM, configures PHY channels, sets interrupts/coherency, applies v1/v2 flags and IRQ handler, and activates. v1 has custom reset/QC/read-ID paths; v2 adds broken-edge IRQ handling and FBS.

State/persistence: last command/class per channel, MMIO bases, diagnostic RAM state, PHY registers, AXI coherency/error masks, mux selection, FBS.DEV, saved port command/list/FIS registers, and interrupt clear ordering.

Dependencies/integration: OF/ACPI, `ahci_platform`, libata command/reset/classification, AHCI FBS/PMP structures.

Risks/test signals: errata-sensitive command, reset, and IRQ ordering; `xgene_ahci_hw_init` return is not checked at its call site; ACPI CID affects version behavior. Test v1/v2 probe, mux, RAM readiness, PMP detection, IDENTIFY/SMART stress, broken-edge IRQ delivery, DEVSLP masking, and link-down hard-reset retries.
