# sources/distributed-fs/ceph-client/drivers/ata/ahci_da850.c

Purpose: TI DaVinci DA850 AHCI driver that initializes SATA PHY from functional/reference clocks and handles reset/PMP quirks.

Important functions: `da850_sata_init`, `ahci_da850_calculate_mpy`, `ahci_da850_softreset`, `ahci_da850_hardreset`, `ahci_da850_probe`, and custom port ops overriding soft/hard reset.

Control flow: probe gets resources, ensures `fck` and `refclk`, computes PLL multiplier, enables resources, maps the second memory resource as power-down register, programs PHY, and activates the host. Soft reset retries with PMP zero on `-EBUSY`; hard reset retries up to `HARDRESET_RETRIES`.

State/persistence: state is in clocks, the power-down register, PHY control register, AHCI resources, and port operation hooks.

Dependencies/integration: DT compatible `ti,da850-ahci`, clock framework, platform memory resources, `ahci_platform`, and libahci reset helpers.

Risks/test signals: invalid refclk fails probe; missing second memory resource fails probe; reset retries can mask marginal PHY behavior. Test multiplier calculation, direct disk/PMP detection, repeated hard-reset stability, and generic PM.
