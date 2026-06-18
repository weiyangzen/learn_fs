# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/telemetry/Kconfig

## Purpose

This Kconfig option enables the legacy Intel SoC telemetry driver stack for Apollo Lake and later-style SoC telemetry.

## Important APIs, Types, And Functions

`INTEL_TELEMETRY` is a tristate depending on `X86_64`, `MFD_INTEL_PMC_BXT`, and `INTEL_PUNIT_IPC`.

## Control Flow

Enabling the option builds the telemetry core, platform driver, and debugfs interface from the directory Makefile.

## State And Persistence

No runtime state; it controls build selection.

## Dependencies And Integration Points

It ensures PMC and P-unit IPC dependencies are present because platform telemetry setup needs PMC MMIO/debug data and P-unit mailbox commands.

## Risks

The dependency set is narrow; builds without Apollo Lake/Goldmont-compatible runtime hardware still compile but probe should reject unsupported CPUs. Debugfs interfaces are included whenever the option is enabled.

## Test Signals

Kconfig dependency resolution, module build as `m`, built-in build as `y`, and absence of unresolved telemetry/P-unit/PMC symbols validate this file.
