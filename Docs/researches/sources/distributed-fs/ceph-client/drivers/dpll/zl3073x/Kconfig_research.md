# sources/distributed-fs/ceph-client/drivers/dpll/zl3073x/Kconfig

## Purpose
This Kconfig file defines build options for the Microchip Azurite/ZL3073x DPLL/PTP/SyncE driver family.

## Important symbols
`ZL3073X` builds the common core and selects `DPLL`, `NET_DEVLINK`, and `REGMAP`. `ZL3073X_I2C` builds the I2C transport and selects `REGMAP_I2C` plus the core. `ZL3073X_SPI` builds the SPI transport and selects `REGMAP_SPI` plus the core.

## Control flow and integration
There is no runtime control flow. The options determine whether `zl3073x.o`, `zl3073x_i2c.o`, and `zl3073x_spi.o` are compiled and which framework dependencies are available.

## State, risks, and tests
No state is stored. Risks are dependency omissions, especially `NET`/devlink/DPLL/regmap selections, or transport options enabling without core support. Build tests should cover built-in and module configurations for core-only, I2C, SPI, and `COMPILE_TEST`.
