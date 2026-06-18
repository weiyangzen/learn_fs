# sources/distributed-fs/ceph-client/drivers/ata/ahci_brcm.c

Purpose: Broadcom STB/NSP/BCM7216 AHCI platform driver adding top-control endian setup, PHY/reset handling, ALPM tuning, and IDENTIFY recovery around generic `ahci_platform`.

Important APIs/types: `struct brcm_ahci_priv`, `brcm_sata_init`, `brcm_sata_phy_enable`, `brcm_sata_phy_disable`, `brcm_sata_alpm_init`, `brcm_ahci_read_id`, `brcm_ahci_probe`, `brcm_ahci_suspend`, `brcm_ahci_resume`, and custom `.host_stop`/`.read_id` port ops.

Control flow: probe matches OF version, maps `top-ctrl`, gets optional resets, obtains AHCI resources, sets Broadcom flags/quirks, resets hardware, enables clocks/regulators, configures endian mode before AHCI MMIO access, reads port mask, enables PHYs, tunes ALPM, enables platform PHYs, and activates the host. Suspend/resume explicitly sequence PHYs, resets, clocks, regulators, and host resume.

State/persistence: private version, port mask, top-control MMIO, quirk bits, reset handles, endian registers, PHY power bits, ALPM timeouts, and resource enable counts. `brcm_ahci_read_id` may temporarily disable host interrupts, reset clock/PHY paths, recalibrate PHYs, and retry IDENTIFY.

Dependencies/integration: OF compatibles, reset framework, generic PHY APIs, `ahci_platform`, libata read-ID flow, and libahci resources.

Risks/test signals: endian setup ordering is critical, resume avoids double-counting resources, and read-ID recovery can leave resources imbalanced if unwound incorrectly. Test endian-correct I/O, IDENTIFY retry, suspend/resume, ALPM wake, and Broadcom registration logs.
