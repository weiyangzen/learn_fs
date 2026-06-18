# sources/distributed-fs/ceph-client/drivers/acpi/dptf/Kconfig

## Purpose
Defines Kconfig options for Intel Dynamic Platform and Thermal Framework ACPI participants under `drivers/acpi/dptf`.

## Important APIs, Types, And Functions
`menuconfig ACPI_DPTF` enables the DPTF menu and depends on `X86`. `config DPTF_POWER` builds the platform power participant driver, defaulting to module. `config DPTF_PCH_FIVR` builds the PCH FIVR participant driver, also defaulting to module.

## Control Flow
Kconfig selection controls which objects the DPTF Makefile builds. `ACPI_DPTF` must be enabled before either child option is visible. The help text describes the participant responsibilities and module names.

## State And Persistence
This file contributes build-time configuration only. The selected values are persisted in the kernel `.config`, not in runtime state.

## Dependencies And Integration Points
Depends on the kernel Kconfig system and x86 ACPI platforms. It integrates with `drivers/acpi/dptf/Makefile`, which maps `CONFIG_DPTF_POWER` and `CONFIG_DPTF_PCH_FIVR` to object files.

## Risks
Defaulting both participant drivers to modules can change distribution build contents when `ACPI_DPTF` is enabled. The `X86` dependency prevents accidental exposure on unsupported architectures but also excludes any future non-x86 DPTF use until adjusted.

## Test Signals
Signals are Kconfig visibility under x86, correct module names in generated config/help, and expected object inclusion for built-in, module, and disabled combinations.
