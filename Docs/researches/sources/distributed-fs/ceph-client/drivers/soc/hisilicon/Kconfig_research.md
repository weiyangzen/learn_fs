
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Kconfig

## Purpose
Defines Hisilicon SoC driver menu and the Kunpeng HCCS driver option.

## Important APIs, Types, and Functions
No runtime APIs. `config KUNPENG_HCCS` is tristate, depends on ACPI, PCC, and ARM64 or compile testing, and describes HCCS health/port/lane power features.

## Control Flow
The symbol gates compilation of `kunpeng_hccs.o`.

## State and Persistence
No runtime state; configuration state is stored in kernel config.

## Dependencies and Integration Points
Requires `ARCH_HISI || COMPILE_TEST` for the menu and integrates with ACPI PCC infrastructure.

## Risks
Correct runtime operation depends on ACPI/PCC firmware support despite compile-test availability.

## Test Signals
Kconfig visibility with dependencies, module and built-in builds, and compile-test on non-HISI architectures.
