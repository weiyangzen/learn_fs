# sources/distributed-fs/ceph-client/drivers/iio/amplifiers/Makefile

## Purpose
This Makefile maps IIO amplifier Kconfig symbols to the corresponding object files.

## Important APIs, Types, And Functions
The object rules are `ad8366.o` for `CONFIG_AD8366`, `ada4250.o` for `CONFIG_ADA4250`, `adl8113.o` for `CONFIG_ADL8113`, and `hmc425a.o` for `CONFIG_HMC425`.

## Control Flow
Kbuild expands each `obj-$()` expression according to the selected tristate symbol and either links the object into the kernel, builds it as a module, or omits it.

## State And Persistence
The file has no runtime state; it persists the build graph for amplifier drivers.

## Dependencies And Integration Points
It integrates with `drivers/iio/amplifiers/Kconfig` and kbuild. The alphabetical-order comment provides a local maintenance convention.

## Risks And Test Signals
Risks are stale object names, missing objects for Kconfig symbols, or accidental ordering churn. Test signals are module builds for each symbol and checking that module names match help text and driver aliases.
