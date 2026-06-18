## sources/distributed-fs/ceph-client/include/linux/mfd/da9055/pdata.h

Purpose: This header defines legacy platform data for DA9055 PMIC board integrations.

Important APIs, types, and constants: `DA9055_MAX_REGULATORS` is 8. `enum gpio_select` represents unavailable, GPIO1, or GPIO2 hardware control selection. `struct da9055_pdata` contains an optional board init callback, IRQ/GPIO bases, regulator init-data pointers, a reset-mode RTC enable flag, and `reg_ren`/`reg_rsel` arrays describing GPIO-controlled regulator enable/state and A/B voltage set selection.

Control flow: Board data is passed to the MFD core, which may call `init()`, configure base IDs, initialize regulators with supplied constraints, enable RTC reset-mode behavior, and pass GPIO control mappings to regulator code.

State and persistence: This is static board configuration. It influences hardware regulator mode and RTC behavior but stores no dynamic hardware state.

Dependencies and integration points: Forward-declares `struct da9055` and references regulator init data. Integrates with DA9055 MFD, regulator, GPIO, IRQ, and RTC code.

Risks: `reg_ren` and `reg_rsel` are pointers and need arrays sized to regulator descriptors; mismatched lengths can cause invalid reads in consumers. GPIO selection values are hardware-specific and can alter regulator state unexpectedly.

Test signals: Platform-data compile and probe tests, regulator init-data index validation, RTC reset-enable behavior, GPIO-controlled regulator enable/set selection, and init callback error handling.
