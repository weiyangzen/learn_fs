# sources/distributed-fs/ceph-client/drivers/ata/ahci_platform.c

Purpose: generic AHCI platform driver for DT/ACPI AHCI controllers that need standard resources and optional resets without SoC-specific programming.

Important objects/functions: `ahci_probe`, `ahci_port_info`, `ahci_port_info_nolpm`, `ahci_platform_sht`, OF matches (`generic-ahci`, legacy compatibles, Hisilicon, Octeon child), ACPI matches, PM and shutdown hooks.

Control flow: probe gets resources with resets, enables resources, applies Hisilicon `NO_FBS | NO_NCQ`, chooses match-provided/default port info, and activates. Failure disables resources; remove/shutdown/PM delegate to generic helpers.

State/persistence: `ahci_host_priv` owns MMIO/resources/flags; ACPI `APMC0D33` selects no-LPM port info.

Dependencies/integration: platform bus, OF/ACPI, `ahci_platform`, libata, SCSI host template, and PCI class-code ACPI matching.

Risks/test signals: generic fallback can bind controllers needing SoC-specific sequencing; Hisilicon quirk changes features. Test generic DT/ACPI probe, reset handling, link discovery, no-LPM on `APMC0D33`, and cleanup on activation failure.
