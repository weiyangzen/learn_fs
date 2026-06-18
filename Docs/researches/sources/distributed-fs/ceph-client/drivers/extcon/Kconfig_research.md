# sources/distributed-fs/ceph-client/drivers/extcon/Kconfig

## Purpose
This Kconfig file defines the External Connector (extcon) subsystem option and all extcon provider driver symbols in this directory.

## Important APIs, types, and functions
The main symbol is `EXTCON`, with driver symbols such as `EXTCON_ADC_JACK`, `EXTCON_AXP288`, `EXTCON_FSA9480`, `EXTCON_GPIO`, Intel PMIC/ACPI variants, ON Semiconductor LC824206XA, Maxim MUIC drivers, USB GPIO, USB-C, Qualcomm, Richtek, Silicon Mitus, and Realtek Type-C entries. It selects dependencies such as `REGMAP_I2C`, `IRQ_DOMAIN`, and `USB_ROLE_SWITCH` where required.

## Control flow
`EXTCON` gates all provider drivers. Each child config encodes hardware bus dependencies and optional subsystem integrations. The resulting symbols drive the sibling Makefile object list.

## State and persistence behavior
This file has build-time state only. Runtime behavior is determined by which providers are compiled or built as modules.

## Dependencies and integration points
It integrates with I2C, GPIO, MFD PMICs, ACPI, power-supply, USB role-switch, Type-C, and architecture symbols. It is the policy layer that prevents impossible builds for hardware-specific extcon providers.

## Risks and edge cases
Incorrect dependencies can produce build failures or hidden runtime probe failures. Some entries allow `COMPILE_TEST`, so driver code must remain portable even without target hardware. USB role switch and Type-C dependencies are written to allow builds with or without those optional frameworks.

## Test signals
Run Kconfig/build matrices for each symbol as built-in and module where possible, with dependencies disabled/enabled, and compile-test cross-architecture coverage for drivers allowing it.
