# sources/distributed-fs/ceph-client/drivers/sbus/char/Kconfig

Purpose: declares miscellaneous Linux/SPARC driver configuration symbols for PROM, flash, microcontroller, BBC I2C/environment control, envctrl, 7-segment display, and Oracle DAX devices.

Important APIs/types/functions: symbols are `SUN_OPENPROMIO`, `OBP_FLASH`, `TADPOLE_TS102_UCTRL`, `BBC_I2C`, `ENVCTRL`, `DISPLAY7SEG`, and `ORACLE_DAX`. Several depend on `SPARC64`, `PCI`, or both; `ORACLE_DAX` defaults to module.

Control flow: build configuration selects which source files in `drivers/sbus/char/Makefile` are built as built-ins, modules, or excluded. Help text documents the exposed device files and hardware families.

State and persistence: no runtime state, but chosen symbols affect kernel image/module composition and device ABI availability.

Dependencies and integration: integrates with SPARC platform support and the child Makefile. Config dependencies prevent some drivers from appearing on non-SPARC64 or non-PCI builds.

Risks and test signals: dependency mistakes can expose drivers on unsupported platforms or hide required legacy devices. Test `allyesconfig` and targeted SPARC64 configs, module builds for each tristate, and dependency visibility for non-PCI or non-SPARC64 combinations.
