
# sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Kconfig

## Purpose
Defines the Fujitsu SoC driver menu and the `A64FX_DIAG` build option.

## Important APIs, Types, and Functions
No runtime APIs. `config A64FX_DIAG` is a bool option requiring `ARM64` and `ACPI`, with help text describing diagnostic interrupt support for kernel dumps via BMC requests.

## Control Flow
Kconfig selection controls whether `a64fx-diag.o` is built by the Makefile.

## State and Persistence
No runtime state. Build configuration persists in the kernel config.

## Dependencies and Integration Points
Integrates with `drivers/soc/fujitsu/Makefile` through `CONFIG_A64FX_DIAG`.

## Risks
The option is bool-only, so it cannot be built as a module unless changed. It enables a driver whose interrupt handler intentionally panics/NMIs the kernel.

## Test Signals
Kconfig visibility on ARM64+ACPI, hidden state when dependencies are absent, and successful build of `a64fx-diag.o` when enabled.
