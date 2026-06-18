# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/Kconfig

Purpose: Defines Kconfig options for Solarflare/Xilinx SFC Ethernet drivers and related optional support.

Important APIs and flow: `NET_VENDOR_SOLARFLARE` gates the vendor menu. `SFC` is a PCI tristate driver for SFC9100 and EF100-family devices; it depends on optional PTP support and selects MDIO, CRC32, and devlink. Optional booleans add MTD flash/EEPROM exposure, firmware-managed hwmon, SR-IOV support with INET and PCI_IOV, and MCDI logging. The file also sources Falcon and Siena subdriver Kconfig files.

State and dependencies: These symbols drive the `sfc/Makefile`, feature compilation inside many SFC sources, and subdirectory inclusion. The MTD/HWMON dependency expressions avoid built-in driver to module dependency inversions.

Risks and test signals: Config dependency drift can create link failures or hide valid feature combinations. Build matrix tests should cover SFC built-in/module, optional MTD/HWMON/SRIOV/MCDI logging on/off, PTP optional configurations, and Falcon/Siena source inclusion.
