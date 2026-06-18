# sources/distributed-fs/ceph-client/drivers/mfd/sec-i2c.c

### Purpose
`sec-i2c.c` is the direct I2C bus driver for Samsung SEC/S5M/S2M PMICs. It selects a device-specific regmap configuration from OF match data, initializes the PMIC regmap over I2C, and delegates common MFD, IRQ, child, PM, and shutdown behavior to `sec-common.c`.

### Important APIs, Types, And Functions
The main functions are `sec_pmic_i2c_probe()` and `sec_pmic_i2c_shutdown()`. `struct sec_pmic_i2c_platform_data` carries a regmap config and SEC device type. Volatile helpers `s2mpa01_volatile()`, `s2mps11_volatile()`, and `s2mpu02_volatile()` keep interrupt mask registers cacheable while treating most other registers as volatile. Static platform data entries cover S2DOS05, S2MPA01, S2MPS11/13/14/15, S2MPU02/05, and S5M8767.

### Control Flow
Probe gets match data, initializes an I2C regmap using the matched config, and calls `sec_pmic_probe()` with the device type, `client->irq`, PMIC regmap, and I2C client pointer. Shutdown calls the shared `sec_pmic_shutdown()`. The I2C driver uses shared sleep PM ops from `sec_pmic_pm_ops`.

### State, Persistence, And Dependencies
Runtime state is managed by the common core after probe; this file owns only the device-managed regmap initialization path. Persistent hardware effects are performed by the common core and child drivers. Regmap configs use `REGCACHE_FLAT` for most larger PMICs, with interrupt mask registers considered nonvolatile/cacheable and most status/control registers volatile. Dependencies include I2C, regmap, device match data, Samsung PMIC headers, and `sec-core.h`.

### Integration Points
This file is the direct-register counterpart to `sec-acpm.c`. It maps OF compatibles to common SEC device types consumed by `sec_pmic_probe()` and `sec_irq_init()`. Child drivers use the PMIC regmap and IRQ domain set up by the shared core.

### Risks
Devices with simple configs such as S2DOS05 and S2MPU05 have no explicit max register or volatile policy here, so child behavior depends on default regmap semantics. Missing or zero `client->irq` is passed through to common IRQ setup, which warns for most devices but may interact poorly with unconditional IRQ-domain use in the core. Volatile helper reuse across S2MPS13/14/15 assumes compatible interrupt-mask layouts.

### Test Signals
Probe tests should cover every OF compatible, regmap init failure, shared core failure, and shutdown. Regcache tests should verify interrupt mask registers remain cacheable while interrupt/status reads are fresh. Suspend/resume tests should use the shared PM ops with RTC alarm wake on direct I2C systems.
