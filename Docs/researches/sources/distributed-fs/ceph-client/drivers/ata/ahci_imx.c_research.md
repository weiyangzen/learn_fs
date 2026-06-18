# sources/distributed-fs/ceph-client/drivers/ata/ahci_imx.c

Purpose: Freescale/NXP i.MX AHCI driver for i.MX53/6Q/6QP/8QM handling clocks, GPR PHY tuning, i.MX8 calibration PHYs, temperature reporting, no-device powerdown, and custom reset/error handling.

Important APIs/types: `struct imx_ahci_priv`, PHY CR helpers, `imx_sata_phy_reset`, `__sata_ahci_read_temperature`, `imx8_sata_enable`, `imx_sata_enable`, `imx_sata_disable`, `ahci_imx_error_handler`, `ahci_imx_softreset`, `imx_ahci_parse_props`, `imx_ahci_probe`, and PM hooks.

Control flow: probe matches SoC type, gets SATA/ref clocks, parses i.MX6 GPR13 PHY tuning or i.MX8 PHYs, gets resources, enables SATA clock, optionally registers i.MX53 hwmon/thermal, powers/configures PHY, forces HWINIT bits and port 0, programs TIMER1MS from AHB clock, and activates. Error handling powers down non-i.MX8 links after first no-device result unless hotplug module param is enabled.

State/persistence: private clocks, GPR regmap, PHY handles, SoC type, first-time/no-device flags, computed PHY params, hwmon/thermal state, `hotplug` module parameter, GPR/HOST register edits, and PHY PDDQ state.

Dependencies/integration: `ahci_platform`, libata, syscon/regmap, i.MX GPR headers, clocks, generic PHY, hwmon, thermal, DT properties, and module params.

Risks/test signals: no-device powerdown prevents later hotplug by default; PHY handshakes have short timeouts; temperature reads rewrite PHY test registers. Test SoC link bring-up, hotplug parameter behavior, hwmon/thermal reads, DT validation, and suspend/resume.
