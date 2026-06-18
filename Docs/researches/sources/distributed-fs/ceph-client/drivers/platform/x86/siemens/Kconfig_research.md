# sources/distributed-fs/ceph-client/drivers/platform/x86/siemens/Kconfig

Purpose: This Kconfig file defines build options for Siemens SIMATIC IPC x86 platform support. It separates the central identification/class driver from CMOS battery monitoring implementations for multiple GPIO backends.

Important APIs, types, and functions: The key config symbols are `SIEMENS_SIMATIC_IPC`, `SIEMENS_SIMATIC_IPC_BATT`, `SIEMENS_SIMATIC_IPC_BATT_APOLLOLAKE`, `SIEMENS_SIMATIC_IPC_BATT_ELKHARTLAKE`, and `SIEMENS_SIMATIC_IPC_BATT_F7188X`. Dependency expressions tie battery monitoring to `HWMON`, the class driver, and appropriate pinctrl/GPIO drivers.

Control flow: The class driver can be built independently. Battery core defaults to the class-driver choice, and per-platform battery drivers default to battery core while adding hardware-provider dependencies.

State and persistence: Kconfig state controls which modules or built-ins exist; it does not manage runtime state.

Dependencies and integration points: It integrates with the top-level platform/x86 Kconfig, hwmon, Broxton/Elkhart Lake/Alder Lake pinctrl, and Nuvoton `GPIO_F7188X`.

Risks and edge cases: Defaulting subdrivers to parent symbols can enable multiple backend modules when dependencies are present. Dependency choices must match the platform-device names selected by `simatic-ipc.c`; otherwise the central driver can instantiate a child for a module that is unavailable.

Test signals: Build test all `y/m/n` combinations, especially `SIEMENS_SIMATIC_IPC_BATT=m` with backend modules and missing pinctrl dependencies. Confirm generated modules have names promised in help text.
