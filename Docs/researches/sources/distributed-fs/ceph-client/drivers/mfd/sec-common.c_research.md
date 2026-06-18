# sources/distributed-fs/ceph-client/drivers/mfd/sec-common.c

### Purpose
`sec-common.c` is the shared Samsung SEC/S5M/S2M PMIC MFD core. It parses common DT properties, initializes IRQ handling, selects child MFD cells for each supported PMIC family, applies small device-specific configuration, exposes shutdown handling, and exports suspend/resume PM operations.

### Important APIs, Types, And Functions
Exported APIs are `sec_pmic_probe()`, `sec_pmic_shutdown()`, and `sec_pmic_pm_ops`. Static helpers include `sec_pmic_parse_dt_pdata()`, `sec_pmic_configure()`, `sec_pmic_dump_rev()`, `sec_pmic_suspend()`, and `sec_pmic_resume()`. Static MFD cell tables cover S5M8767, S2DOS05, S2MPA01, S2MPG10, S2MPG11, S2MPS11/13/14/15, and S2MPU02/05, including RTC, clock, GPIO, meter, and regulator children where supported.

### Control Flow
`sec_pmic_probe()` allocates `struct sec_pmic_dev`, stores device type, client, IRQ, and PMIC regmap, parses common DT flags, calls `sec_irq_init()`, marks runtime PM active, selects a child-cell table by device type, and adds MFD children using the regmap IRQ domain. It then applies S2MPS13 WRSTBI disable configuration if requested and dumps revision for direct-register PMICs. Shutdown checks `manual_poweroff` and, currently only for S2MPS11, clears PWRHOLD. Suspend optionally enables IRQ wake and disables the PMIC IRQ so RTC alarm handling does not race a suspended I2C controller; resume reverses that.

### State, Persistence, And Dependencies
Runtime state is `struct sec_pmic_dev`, parsed `struct sec_platform_data`, IRQ chip data, child devices, PM runtime active state, and wake IRQ status. Persistent hardware effects include optional S2MPS13 WRSTBI configuration and S2MPS11 PWRHOLD clearing on shutdown. Dependencies include regmap, MFD core, Samsung core/irq/PMIC headers, OF properties, runtime PM, and `sec_irq_init()` from `sec-irq.c`.

### Integration Points
`sec-i2c.c` and `sec-acpm.c` both call `sec_pmic_probe()` after creating a bus-specific PMIC regmap. `sec-irq.c` supplies the IRQ domain consumed by RTC/regulator/clock/GPIO children. The PM ops are used by both direct I2C and ACPM platform drivers.

### Risks
`sec_irq_init()` may return NULL for devices without IRQ support, but `sec_pmic_probe()` unconditionally calls `regmap_irq_get_domain(irq_data)`, so devices like S2DOS05 or no-IRQ configurations depend on regmap helper behavior or may be fragile. Suspend always disables `sec_pmic->irq`; if the IRQ is zero or already disabled, platform behavior needs care. Manual poweroff only supports S2MPS11 despite parsing the property generically. Child table names include shared historical names such as `s2mps14-rtc`, so renaming would affect child binding.

### Test Signals
Tests should probe every supported device type through both direct and ACPM paths where applicable, verifying selected children and IRQ domain behavior. DT tests should cover `samsung,s2mps11-acokb-ground` and `samsung,s2mps11-wrstbi-ground`. Suspend/resume tests should verify RTC alarm wake with I2C suspended. Shutdown tests should confirm S2MPS11 PWRHOLD clearing and warnings for unsupported manual poweroff devices.
