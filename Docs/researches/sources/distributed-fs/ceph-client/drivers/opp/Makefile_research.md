# sources/distributed-fs/ceph-client/drivers/opp/Makefile

## Purpose
Selects OPP subsystem object files and debug flags for Kbuild.

## Important APIs, types, and functions
Builds `core.o` and `cpu.o` unconditionally in this directory. Builds `of.o` with `CONFIG_OF`, `debugfs.o` with `CONFIG_DEBUG_FS`, and `ti-opp-supply.o` with `CONFIG_ARM_TI_CPUFREQ`. Adds `-DDEBUG` when `CONFIG_DEBUG_DRIVER` is enabled.

## Control flow
No runtime control flow. Kbuild expands configuration-conditioned object lists and flags.

## State and persistence behavior
Controls build artifacts only, which determine runtime availability of OF OPP parsing, debugfs support, and TI OPP supply support.

## Dependencies and integration points
Integrates with OPP Kconfig, Kbuild, OF, debugfs, and ARM TI cpufreq support.

## Risks and edge cases
Wrong object selection can silently remove features or build unsupported code. Unconditional core/cpu object inclusion assumes the directory is only entered when OPP framework support is intended.

## Test signals
Build matrix coverage over OF, debugfs, debug-driver, and ARM TI cpufreq configurations is the main validation signal.
