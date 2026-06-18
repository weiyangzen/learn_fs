# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/speed_select_if/Kconfig

## Purpose

This Kconfig fragment defines build options for Intel Speed Select Technology interface drivers.

## Important APIs, Types, And Functions

`INTEL_SPEED_SELECT_INTERFACE` is the user-visible tristate. `INTEL_SPEED_SELECT_TPMI` is an internal tristate selected when `INTEL_TPMI` is enabled. The menu depends on `PCI` and `X86_64 || COMPILE_TEST`.

## Control Flow

Selecting the interface builds the common char-device layer plus MMIO, PCI mailbox, MSR mailbox, and, when TPMI is configured, TPMI Speed Select modules.

## State And Persistence

Kconfig has no runtime state; it controls build inclusion.

## Dependencies And Integration Points

The option integrates with the platform/x86 Intel build, PCI, TPMI, and userspace tooling that expects `/dev/isst_interface`.

## Risks

The TPMI suboption is hidden and selected only through `INTEL_TPMI`; disabling TPMI removes the newer backend even when the main interface is enabled. The help text describes non-architectural Xeon server features, so enabling on unsupported hardware should rely on runtime CPU/device checks.

## Test Signals

Configuration tests should verify module objects built for `m`, built-in behavior for `y`, and TPMI object inclusion only when `INTEL_TPMI` is available.
