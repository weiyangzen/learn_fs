# sources/distributed-fs/ceph-client/drivers/mfd/sec-acpm.c

### Purpose
`sec-acpm.c` is the Samsung S2MPG10/S2MPG11 PMIC bus driver for systems where PMIC register access goes through Exynos ACPM firmware instead of direct I2C. It builds firmware-backed regmaps for common, PMIC, RTC, and meter access types, then calls the shared Samsung SEC PMIC MFD core.

### Important APIs, Types, And Functions
Key functions are `sec_pmic_acpm_probe()`, `sec_pmic_acpm_shutdown()`, `sec_pmic_acpm_regmap_init()`, and regmap bus callbacks `sec_pmic_acpm_bus_write()`, `sec_pmic_acpm_bus_read()`, and `sec_pmic_acpm_bus_reg_update_bits()`. `struct sec_pmic_acpm_platform_data` identifies the device type, ACPM channel, Speedy channel, and regmap configs. The file defines detailed regmap access tables for S2MPG10 and S2MPG11 common, PMIC, RTC, and meter register spaces.

### Control Flow
Probe reads platform data from OF match, obtains the ACPM handle from the parent node, gets platform IRQ 0, allocates a shared bus context, and initializes the common regmap with device attachment. It then creates the PMIC regmap without attachment, optional RTC regmap, and meter regmap. Each regmap uses the custom ACPM regmap bus; reads/writes validate register/value lengths and call ACPM PMIC operations with the configured access type and Speedy channel. Finally, probe calls `sec_pmic_probe()` with the PMIC regmap and IRQ and optionally initializes wakeup if `wakeup-source` is present.

### State, Persistence, And Dependencies
Runtime state includes ACPM handle, channel IDs, Speedy channel, small bus contexts, regmap caches, SEC PMIC core state, and optional wakeup state. Persistent effects are all PMIC register writes routed through ACPM and interrupt/wakeup configuration in the core. Regmaps use `REGCACHE_FLAT` and carefully mark interrupt registers precious, read-only data, nonvolatile masks, volatile meter data, and RTC time/update fields. Dependencies include Exynos ACPM protocol, platform devices, regmap custom bus, MFD SEC core, Samsung S2MPG headers, device properties, and PM ops exported by `sec-common.c`.

### Integration Points
The common regmap is later found by `sec-irq.c` as `"common"` for S2MPG chained interrupt setup. The PMIC regmap is passed to the shared MFD core. The RTC and meter regmaps are attached by name for child drivers. S2MPG10 registers an RTC child through the core; S2MPG11 omits RTC config and child support in this driver.

### Risks
ACPM bulk transfer size is capped at eight data bytes, so callers requiring larger raw transfers must split them. The PMIC regmap is not attached to the device by name, which is intentional for core passing but may surprise code expecting `dev_get_regmap(dev, "pmic")`. Correctness depends on ACPM firmware implementing `bulk_read`, `bulk_write`, and `update_reg` semantics. Access-table mistakes can block valid child accesses or cache volatile firmware-backed status. Missing parent ACPM node or IRQ aborts probe.

### Test Signals
Tests should cover S2MPG10 and S2MPG11 probe, ACPM handle deferral/failure, common/RTC/meter named regmap lookup, PMIC core child creation, chained S2MPG IRQ setup, and wakeup-source behavior. Regmap tests should validate read/write/readonly/precious/volatile policy and raw transfer size limits. Firmware-integration tests should compare ACPM register reads/writes against expected PMIC state.
