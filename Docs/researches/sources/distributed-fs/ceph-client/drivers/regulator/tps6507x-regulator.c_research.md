# sources/distributed-fs/ceph-client/drivers/regulator/tps6507x-regulator.c

Purpose: Platform child regulator driver for the TPS6507x MFD, registering three DCDC regulators and two LDOs.

Important APIs/types/functions: `struct tps6507x_pmic` contains per-regulator descriptors, parent MFD pointer, per-rail `tps_info`, and an I/O mutex. Helpers wrap parent `read_dev`/`write_dev` and provide locked set/clear/read/write operations. Regulator ops manually implement enable, disable, is-enabled, get/set selector, and table listing.

Control flow: probe obtains the parent MFD and optional board init data, allocates PMIC state, initializes a mutex, builds five descriptors from `tps6507x_pmic_regs`, applies platform or OF `ti,defdcdc_default` selection for DCDC2/DCDC3 high/low default registers, and registers each regulator. Runtime ops compute register and mask by regulator ID, use `CON_CTRL1` enable bits, and write voltage selectors into the appropriate DCDC/LDO register.

State and persistence: state is in parent MFD registers. Driver state stores `defdcdc_default` choices and serializes register access with `io_lock`. The parent stores `tps6507x_dev->pmic`.

Dependencies and integration points: TPS6507x MFD callbacks, platform driver model, regulator core, OF regulator parsing, and legacy board data.

Risks: manual RMW must remain locked to avoid lost updates. `config.init_data = init_data` is not indexed in the loop, so legacy platform init data handling should be reviewed against regulator-core expectations. Selector values are ORed without shifting because masks are low-aligned for used fields.

Test signals: enable bit mapping, DCDC2/DCDC3 high-vs-low selection, OF parse callback, concurrent set/enable operations, and parent read/write failure propagation.
