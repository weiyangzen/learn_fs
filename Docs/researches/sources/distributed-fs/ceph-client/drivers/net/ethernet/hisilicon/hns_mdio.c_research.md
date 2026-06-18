# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns_mdio.c

Implements the Hisilicon HNS MDIO platform driver. It registers a `mii_bus` with Clause 22 and Clause 45 read/write callbacks, supports DT and ACPI probing, maps the MDIO MMIO resource, and sequences controller reset/clock through syscon or ACPI `_RST`.

Important functions are `hns_mdio_probe()`, `hns_mdio_remove()`, `hns_mdio_read_c22()`, `hns_mdio_write_c22()`, `hns_mdio_read_c45()`, `hns_mdio_write_c45()`, `hns_mdio_reset()`, `hns_mdio_wait_ready()`, and `mdio_sc_cfg_reg_write()`. C45 operations perform address and data phases with readiness polling; C22 operations issue a single command after the controller start bit clears.

State is in `struct hns_mdio_device`: MDIO register base, optional syscon regmap, and reset/clock register offsets. Dependencies include Linux MDIO/PHY, OF/ACPI, platform resources, syscon/regmap, and devm allocation. Risks are CPU-heavy busy waits, missing syscon causing reset failure, ACPI masking auto-probe, and command sequencing assumptions. Test DT/ACPI probe, PHY discovery, C22/C45 accesses, reset success/failure, and timeout behavior.
