# sources/distributed-fs/ceph-client/drivers/hwspinlock/Makefile

## Purpose
This Makefile maps hardware spinlock Kconfig symbols to the core framework object and provider driver objects.

## Important APIs, Types, And Functions
There are no functions. Build targets are `hwspinlock_core.o`, `omap_hwspinlock.o`, `qcom_hwspinlock.o`, `sprd_hwspinlock.o`, `stm32_hwspinlock.o`, and `sun6i_hwspinlock.o`.

## Control Flow
Kbuild includes `hwspinlock_core.o` when `CONFIG_HWSPINLOCK` is enabled, and includes each provider object when the corresponding provider symbol is enabled.

## State And Persistence
This file only controls build outputs. It creates no runtime state.

## Dependencies And Integration Points
It directly consumes the symbols from `drivers/hwspinlock/Kconfig`. The provider objects depend on the exported registration/request APIs from `hwspinlock_core.o`.

## Risks
- If a provider is enabled without the core object, linking would fail; the Kconfig nesting prevents that.
- Adding a provider requires updating both Kconfig and this Makefile.

## Test Signals
Validate `obj-y`/`obj-m` output with representative configs, especially built-in core with modular providers and all providers disabled.
