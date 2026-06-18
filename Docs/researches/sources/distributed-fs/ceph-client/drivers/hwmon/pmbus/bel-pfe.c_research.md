# sources/distributed-fs/ceph-client/drivers/hwmon/pmbus/bel-pfe.c

Purpose: PMBus driver for BEL PFE1100 and PFE3000 power supplies.

Important APIs/types/functions: `pfe_driver_info[]` contains static PMBus descriptors for `pfe1100` and `pfe3000`. `pfe_plat_data` sets `PMBUS_SKIP_STATUS_CHECK` to tolerate devices that report communication errors for `VOUT_MODE`. `pfe_pmbus_probe()` stores platform data, resets PFE3000 to page zero, and calls `pmbus_do_probe()`.

Control flow: I2C ID matching passes the model enum. Probe applies the PMBus platform flag before core probing. PFE3000 receives an explicit `PMBUS_PAGE` write to avoid probe failure from an unexpected current page. The PMBus core creates attributes for one PFE1100 page or seven PFE3000 pages with per-page capability masks.

State and persistence: no private allocated state. Probe writes page zero on PFE3000 and assigns `client->dev.platform_data` to a static structure.

Dependencies and integration: depends on PMBus core and I2C. Multi-page PFE3000 integration relies on PMBus core page management.

Risks: writing `client->dev.platform_data` mutates device state before probe. `PMBUS_SKIP_STATUS_CHECK` is necessary but broad; it can hide real status read problems during probing. PFE3000 page reset assumes page command is safe and accepted.

Test signals: PFE1100 and PFE3000 probe, status-check skipping around `VOUT_MODE`, page-zero reset before probe, expected attributes on pages 0/1/2/4/5/6, and module unload.
