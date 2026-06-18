<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.c

## Purpose
Implements the MediaTek MT6311 I2C regulator driver for one VDVFS buck and one VBIASN LDO.

## Important APIs, Types, And Functions
`mt6311_regulators[]` defines a linear buck and enable-only LDO using `MT6311_BUCK()` and `MT6311_LDO()`. Buck ops use generic regmap voltage, enable, and transition-time helpers. LDO ops only expose enable, disable, and is_enabled. Probe is `mt6311_i2c_probe()`.

## Control Flow
Probe initializes an 8-bit regmap with MAPLE cache, reads `MT6311_SWCID`, accepts only E1/E2/E3 chip IDs, and registers both regulators with the shared regmap. All runtime operations are descriptor-driven by regulator-regmap helpers.

## State And Persistence
The driver does not allocate private state. Voltage and enable state lives in MT6311 registers. Regmap cache mirrors register values during the I2C device lifetime.

## Dependencies And Integration Points
Depends on I2C, regmap, regulator core, OF regulator support, `linux/regulator/mt6311.h`, and local register definitions in `mt6311-regulator.h`. OF compatible is `mediatek,mt6311-regulator`.

## Risks And Test Signals
Risks include unsupported chip ID handling, cache coherency for hardware-updated registers, LDO lacking voltage/status callbacks, and register/mask drift from the companion header. Test by probing all supported chip revisions, reading VDVFS voltage selector, setting voltage across the 600 mV to 1.39375 V range, toggling VDVFS and VBIASN, and validating DT regulator matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/mt6311-regulator.c -->
