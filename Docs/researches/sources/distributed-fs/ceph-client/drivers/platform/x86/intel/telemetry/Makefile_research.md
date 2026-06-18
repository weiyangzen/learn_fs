# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Makefile

## Purpose

This Makefile builds the three legacy Intel telemetry modules.

## Important APIs, Types, And Functions

It maps `intel_telemetry_core-y` to `core.o`, `intel_telemetry_pltdrv-y` to `pltdrv.o`, and `intel_telemetry_debugfs-y` to `debugfs.o`, all gated by `CONFIG_INTEL_TELEMETRY`.

## Control Flow

Kbuild compiles each module object when telemetry is enabled.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

The split reflects API core, platform implementation, and debugfs presentation modules.

## Risks

The debugfs module depends on platform data being installed by the platform driver; load ordering matters at runtime even though all objects are selected by the same Kconfig.

## Test Signals

Build the option as module and built-in, inspect produced module names, and load modules in dependency order.
