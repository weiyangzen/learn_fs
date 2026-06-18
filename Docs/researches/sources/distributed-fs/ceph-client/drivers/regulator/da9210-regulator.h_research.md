# sources/distributed-fs/ceph-client/drivers/regulator/da9210-regulator.h

Purpose: Provides DA9210-specific platform data and register/bit definitions for the DA9210 regulator driver.

Important APIs, types, and symbols: `struct da9210_pdata` carries legacy `regulator_init_data`. Register constants define page control, status/event/mask banks, GPIO control registers, buck control/current/voltage registers, interface settings, OTP/configuration registers, and paged address regions. Bit definitions cover event and mask bits for GPIOs, overcurrent, not-power-good, temperature warnings/critical events, voltage max events, buck enable, GPI routing, dynamic voltage control, current-limit selector, mode, startup/powerdown controls, voltage selector masks, and standalone configuration.

Control flow support: `da9210-regulator.c` uses `DA9210_REG_VBUCK_A`, `DA9210_VBUCK_MASK`, `DA9210_REG_BUCK_CONT`, `DA9210_BUCK_EN`, `DA9210_REG_BUCK_ILIM`, and `DA9210_BUCK_ILIM_MASK` in the regulator descriptor. It uses `EVENT_B` and `MASK_B` bit definitions in the IRQ path.

State and persistence: The header defines hardware state fields but keeps no runtime state. Page selection constants indicate the chip has wider logical address space than the simple operations used by the C driver.

Dependencies and integration points: This is a private header consumed by the DA9210 driver. Its platform data type connects older board files to regulator constraints, while OF users bypass it.

Risks and test signals: Confirm register constants against the DA9210 datasheet, especially event bits and current-limit masks. If future driver changes access page-2 or configuration registers, the regmap setup in the C file may need range configuration similar to DA9211.
