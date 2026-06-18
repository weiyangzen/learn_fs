# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Makefile

## Purpose

This Makefile builds Intel uncore frequency control objects.

## Important APIs, Types, And Functions

`CONFIG_INTEL_UNCORE_FREQ_CONTROL` builds `intel-uncore-frequency.o` from `uncore-frequency.o` and `intel-uncore-frequency-common.o` from `uncore-frequency-common.o`. `CONFIG_INTEL_UNCORE_FREQ_CONTROL_TPMI` builds `intel-uncore-frequency-tpmi.o`.

## Control Flow

Kbuild compiles selected objects according to Kconfig.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

It separates the common sysfs layer, original backend, and TPMI backend.

## Risks

Runtime module ordering must ensure the common module's exported namespace is available to backends.

## Test Signals

Builds with base-only and TPMI configurations, module dependency resolution, and namespace import/export checks validate it.
