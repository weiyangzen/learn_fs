# sources/distributed-fs/ceph-client/drivers/ata/ahci_dm816.c

Purpose: TI DaVinci DM816 AHCI driver that computes PHY PLL multiplier bits, programs two port PHY registers, and works around PMP/direct-drive soft reset detection.

Important functions: `ahci_dm816_get_mpy_bits`, `ahci_dm816_phy_init`, `ahci_dm816_softreset`, `ahci_dm816_probe`, and port ops overriding `.reset.softreset`.

Control flow: probe gets and enables resources, initializes PHY from the second clock rate, then activates the host. PHY init validates clock count and divisibility, looks up PLL multiplier, writes port 0 PLL/PHY config and port 1 PHY config. Soft reset retries with PMP zero after `-EBUSY`.

State/persistence: clock/resource handles in `ahci_host_priv` and hardware PHY registers; no driver-private runtime allocation.

Dependencies/integration: `ahci_platform`, libata reset helpers, clock framework, OF compatible `ti,dm816-ahci`, and generic PM.

Risks/test signals: missing/nonstandard refclk fails probe; fixed port 1 setup assumes platform defaults. Test two-clock probe, both-port link, direct-drive detection with PMP-capable config, and suspend/resume.
