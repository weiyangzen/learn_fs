# sources/distributed-fs/ceph-client/drivers/regulator/pf530x-regulator.c

Purpose: provides an I2C regulator driver for NXP PF5300/PF5301/PF5302 single-buck PMICs. It registers the SW1 regulator, exposes voltage, bypass, status, and error flag operations, and validates the detected chip identity.

Important APIs/types/functions: `struct pf530x_chip` contains the device and regmap. `pf530x_get_status()` maps interrupt sense and PMIC state registers to regulator status values. `pf530x_get_error_flags()` maps over-voltage, under-voltage, current-limit, and thermal bits into regulator error flags. `pf530x_identify()` reads device ID, revision, EM revision, and program ID registers and logs decoded revision data.

Control flow: I2C probe allocates state, initializes an 8-bit regmap, identifies the chip, obtains OF regulator init data from the device node, builds a regulator config, and registers one regulator. Status calls first inspect fault sense bits, then read the PMIC state register to distinguish run, standby, and low-power-off states.

State and persistence: state is minimal and devm-managed. The driver does not cache voltage or enable state. The regmap uses `REGCACHE_MAPLE`; hardware register state persists according to PMIC behavior.

Dependencies and integration: depends on I2C, regmap, regulator core, and OF regulator helpers. Device tree compatible is `nxp,pf5300`; I2C IDs also list `pf5300`, `pf5301`, and `pf5302`.

Risks and test signals: `pf530x_identify()` returns `ret` after an unknown family even though `ret` is zero from a successful read, so unknown-family detection can incorrectly succeed. The OF table only lists `nxp,pf5300` despite I2C IDs for the family. Test chip identification for all device IDs and bad families, voltage selection, bypass, status mapping, and error flag reads.
