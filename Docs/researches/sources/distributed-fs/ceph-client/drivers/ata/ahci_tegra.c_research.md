# sources/distributed-fs/ceph-client/drivers/ata/ahci_tegra.c

Purpose: NVIDIA Tegra AHCI driver for Tegra124/210/186 with powergate, reset, regulator, IPFS, backdoor capability/class-code, PHY tuning, and interrupt initialization.

Important APIs/types: `struct sata_pad_calibration`, `struct tegra_ahci_soc`, `struct tegra_ahci_priv`, `tegra_ahci_handle_quirks`, `tegra124_ahci_init`, `tegra_ahci_power_on`, `tegra_ahci_power_off`, `tegra_ahci_controller_init`, `tegra_ahci_host_stop`, `tegra_ahci_probe`.

Control flow: probe gets resources, maps SATA and optional AUX registers, obtains resets/clock/regulators, powers controller, programs FPCI/SATA enable, electrical/OOB/COMWAKE tuning, optional fuse pad calibration, emulated PCI config/class code, AHCI LPM backdoor bits, clock gating/IDDQ, DevSlp quirks, interrupt mask, and activates host. Host stop powers off.

State/persistence: MMIO bases, resets, SATA clock, regulators, SoC tables, powergate state, PHY tuning, class/capability registers, AUX DevSlp bits, and interrupt masks. LP0 suspend is explicitly not implemented.

Dependencies/integration: Tegra fuse/PMC APIs, regulators, resets, clocks, OF match data, `ahci_platform`, and libata host stop.

Risks/test signals: strict init order; SoC-specific required resets; fuse calibration affects link stability; backdoor capability edits change LPM/NCQ. Test powergate, link speed stability, interrupts, fuse-calibrated PHY, failed-activation deinit, and note lack of LP0 suspend.
