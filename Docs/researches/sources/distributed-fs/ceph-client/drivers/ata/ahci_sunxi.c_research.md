# sources/distributed-fs/ceph-client/drivers/ata/ahci_sunxi.c

Purpose: Allwinner sunxi AHCI driver performing undocumented PHY bring-up/calibration, custom DMA transaction setup, and conservative feature flags.

Important APIs/functions: `enable_pmp` module param, register bit helpers, `ahci_sunxi_phy_init`, `ahci_sunxi_start_engine`, `ahci_sunxi_probe`, `ahci_sunxi_resume`.

Control flow: probe gets reset-capable resources, installs custom `start_engine`, enables resources, initializes/calibrates PHY with timeouts, sets 32-bit/no-MSI/NCQ flags, disables PMP unless requested, and activates. Resume repeats resource enable and PHY init.

State/persistence: host flags, start-engine callback, PHY/RWCR/P0DMACR registers, resource state, and `enable_pmp` module setting.

Dependencies/integration: OF compatibles `allwinner,sun4i-a10-ahci` and `allwinner,sun8i-r40-ahci`, `ahci_platform`, libahci engine callback, reset/resources, and libata flags.

Risks/test signals: magic PHY values and tight timeouts; enabling PMP may break direct disks; DMA settings inferred from related hardware. Test PHY success, direct disk default, PMP when enabled, NCQ, and resume.
