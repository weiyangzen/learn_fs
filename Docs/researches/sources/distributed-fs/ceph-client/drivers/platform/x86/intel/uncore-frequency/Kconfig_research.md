# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/Kconfig

## Purpose

This Kconfig fragment defines Intel uncore frequency control driver options.

## Important APIs, Types, And Functions

`INTEL_UNCORE_FREQ_CONTROL` is the user-visible tristate and selects `INTEL_UNCORE_FREQ_CONTROL_TPMI` when `INTEL_TPMI` is enabled. The menu depends on `X86_64 || COMPILE_TEST`.

## Control Flow

Enabling the option builds the legacy/main uncore frequency module, common sysfs module, and TPMI backend when available.

## State And Persistence

No runtime state.

## Dependencies And Integration Points

The option integrates with platform/x86 Intel uncore frequency sysfs and TPMI backend support.

## Risks

The prompt has a spelling typo in "Frquency". TPMI backend inclusion depends on `INTEL_TPMI`; unsupported systems rely on runtime probe checks.

## Test Signals

Kconfig selection with and without TPMI, module builds, and dependency-free COMPILE_TEST builds are expected signals.
