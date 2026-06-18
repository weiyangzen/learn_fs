# sources/distributed-fs/ceph-client/drivers/regulator/da9211-regulator.h

Purpose: Defines DA9211-family register addresses and masks used by the DA9211 regulator driver.

Important APIs, types, and symbols: The header declares page control, status/event/mask registers, GPIO control registers, buck control/configuration/current/voltage registers, interface register, `CONFIG_E`, and `DEVICE_ID`. Bit definitions include page selection, GPIO pin/type/mode options, event and mask bits for power-good, temperature, and overcurrent, buck enable/GPI routing, voltage selector routing, current-limit nibbles, buck mode values, phase selection, and `DA9211_SLAVE_SEL`.

Control flow support: The C driver uses `DA9211_REG_PAGE_CON`, page mask/shift, and max range to configure paged regmap access; it marks status/event registers volatile. It uses `DEVICE_ID` to detect supported chips, `CONFIG_E`/`SLAVE_SEL` to validate one- versus two-buck hardware configuration, buck control and voltage registers to build descriptors, and overcurrent event/mask bits for IRQ handling.

State and persistence: The header defines persistent PMIC configuration and volatile event/status fields but has no memory state. Register naming assumes BUCKA and BUCKB are adjacent in several areas, which the C driver uses through arithmetic offsets.

Dependencies and integration points: Private to the DA9211 regulator driver and tied to `dt-bindings/regulator/dlg,da9211-regulator.h` mode constants included by the C file.

Risks and test signals: Verify adjacent-register arithmetic remains valid for every supported chip alias. Event masks should be tested for both rails, and `SLAVE_SEL` interpretation should be validated on one-phase and two-phase board configurations.
