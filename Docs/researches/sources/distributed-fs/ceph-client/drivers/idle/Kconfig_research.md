# sources/distributed-fs/ceph-client/drivers/idle/Kconfig

## Purpose

`drivers/idle/Kconfig` exposes the `INTEL_IDLE` kernel configuration option for the Intel-specific cpuidle driver.

## Important APIs, Types, and Functions

- `config INTEL_IDLE` is a boolean option titled "Cpuidle Driver for Intel Processors".
- It depends on `CPU_IDLE`, `X86`, and `CPU_SUP_INTEL`.
- Help text explains that `intel_idle` uses native Intel hardware idle knowledge and can coexist with `acpi_idle` for unsupported processors.

## Control Flow

Kconfig evaluates dependencies during kernel configuration. When enabled, the Makefile in the same directory builds `intel_idle.o`.

## State and Persistence Behavior

The file defines build-time configuration state only. It does not create runtime state.

## Dependencies and Integration Points

It integrates with the kernel Kconfig system, cpuidle subsystem, x86 architecture selection, and Intel CPU support option. The resulting symbol controls compilation in `drivers/idle/Makefile`.

## Risks and Edge Cases

Incorrect dependencies could expose Intel-specific code on unsupported architectures or hide it on valid systems. Since `acpi_idle` can also be configured, runtime driver selection remains outside this file.

## Test Signals

Configuration tests should verify `INTEL_IDLE` is visible only when all dependencies are enabled and that enabling it causes `intel_idle.o` to be built.
