# sources/distributed-fs/ceph-client/include/linux/pmbus.h

Purpose: provides board/platform data and quirk flags for PMBus hardware-monitoring and regulator support.

Important APIs and types: `struct pmbus_platform_data` carries device-specific `flags`, `num_regulators`, and regulator init data. Flags include skip status checks, write-protected devices, missing CAPABILITY or WRITE_PROTECT registers, controller reset via status read after failed checks, coefficient-command direct-mode setup, and OPERATION/VOUT protection quirks.

Control flow: board or device registration passes platform data to the PMBus core; the PMBus driver interprets flags during register detection, write-protection checks, direct-mode coefficient setup, and regulator registration.

State and persistence: no runtime state is stored here beyond platform data supplied at probe. Persistent behavior comes from board wiring and chip quirks.

Dependencies and integration points: depends on `linux/bits.h` and regulator init data declarations used by PMBus hwmon/regulator drivers.

Risks and test signals: risks include wrong quirk flags causing false register detection, unsafe writes to protected chips, missing regulator init data, and direct-mode coefficient errors. Test probe on affected PMBus chips, register-detection failures, write-protection behavior, regulator registration, and hwmon readings under quirk combinations.
