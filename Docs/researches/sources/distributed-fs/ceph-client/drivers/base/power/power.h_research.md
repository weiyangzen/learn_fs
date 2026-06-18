# sources/distributed-fs/ceph-client/drivers/base/power/power.h

## Purpose
Defines internal driver-core PM initialization helpers, wake-IRQ state, runtime PM declarations/stubs, sysfs/QoS hooks, system-sleep PM list declarations, and configuration-dependent no-op fallbacks.

## Important APIs, Types, And Functions
`device_pm_init_common()` initializes `dev->power.lock`, QoS pointer, and `early_init`. `pm_runtime_early_init()` sets runtime PM disable depth differently depending on `CONFIG_PM`. `struct wake_irq` tracks wake IRQ ownership flags, IRQ number, device, and name. The header declares runtime PM internals, wake IRQ helpers, PM sysfs helpers, PM QoS sysfs helpers, system-sleep list helpers, wakeup source sysfs hooks, and `device_pm_init()`.

## Control Flow
Device initialization calls `device_pm_init()`, which performs common initialization, system-sleep initialization, and runtime PM initialization. Compile-time gates turn runtime PM and system sleep functions into no-ops when disabled while keeping callers buildable.

## State And Persistence
State initialized here is embedded in `struct device::power`: locks, QoS pointer, runtime PM depth/status, wakeup pointers, PM list entry, and completion fields. Wake IRQ status bits track allocation, devres management, reverse ordering, and enabled state.

## Dependencies And Integration
Includes PM QoS and depends on `CONFIG_PM`/`CONFIG_PM_SLEEP` structure. It is consumed by driver-core device creation, platform bus PM, runtime PM, wake IRQ, wakeup, sysfs, and PM QoS modules.

## Risks And Test Signals
Risks include inconsistent stub semantics between PM-enabled and PM-disabled builds, missing initialization before other driver-core code touches `dev->power`, and wake IRQ status-bit misuse. Test signals are broad config matrix builds, device registration tests with PM disabled, wake IRQ setup/teardown tests, and runtime PM KUnit coverage.
