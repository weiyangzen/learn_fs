<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-buck.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/lp8788-buck.c

Purpose: LP8788 MFD child driver for four buck regulators, with dynamic voltage scaling support on BUCK1 and BUCK2.

Important APIs/types/functions: `struct lp8788_buck` stores parent pointer, regulator, DVS data, and DVS GPIOs. Helpers select active BUCK1/2 VOUT registers from GPIO or register DVS state; buck ops implement voltage, enable, startup time, and forced/auto PWM mode.

Control flow: probe validates platform ID, allocates per-buck data, initializes DVS mode for BUCK1/2, and registers the selected descriptor. If platform DVS data and GPIOs are present, DVS is configured for external pins; otherwise the driver selects I2C register DVS control.

State and persistence: DVS GPIO state and platform DVS pointers are runtime state. Voltage selectors, enable bits, DVS mode, startup timing, and PWM mode live in LP8788 registers.

Dependencies and integration: LP8788 MFD helpers (`lp8788_read_byte`, `lp8788_update_bits`), GPIO descriptors, platform children, regulator linear-range helpers.

Risks and test signals: GPIO request failure silently falls back to register DVS mode in `lp8788_init_dvs()`, which can mask board wiring errors. Read errors in DVS mode selection are not checked. Test BUCK1/2 DVS pin combinations, BUCK3/4 normal selector path, PWM mode, startup time, and invalid platform IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/lp8788-buck.c -->
