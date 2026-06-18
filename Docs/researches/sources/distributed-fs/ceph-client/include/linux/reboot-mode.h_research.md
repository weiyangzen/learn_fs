# sources/distributed-fs/ceph-client/include/linux/reboot-mode.h

## Purpose

This header declares the reboot-mode framework interface. Drivers can register a small object that writes a platform-specific magic value before reboot so firmware, bootloaders, or PMIC logic can distinguish normal, recovery, bootloader, panic, or other reboot reasons.

## Important APIs, Types, and Functions

`struct reboot_mode_driver` contains a `struct device *`, list node, `write()` callback taking an unsigned magic value, and a `notifier_block` used to observe reboot notifications. Registration APIs are `reboot_mode_register()`, `reboot_mode_unregister()`, `devm_reboot_mode_register()`, and `devm_reboot_mode_unregister()`.

## Control Flow

A platform driver initializes the structure and registers it. During reboot notification, the core selects the configured magic value and invokes the driver's `write()` callback. The devm variants bind unregister cleanup to device lifetime.

## State and Persistence Behavior

Kernel state is the registered driver list and notifier entry. Persistent state is platform-specific and written by the callback, often into a retained register, SRAM cell, PMIC register, or similar storage that survives reset.

## Dependencies and Integration Points

The structure references `struct device`, `struct list_head`, and `struct notifier_block`; those are expected to be available through the including context or other headers. It integrates with reboot notifiers and platform/firmware reboot reason mechanisms.

## Risks

The callback usually runs late in reboot, so it must be reliable and avoid sleeping or complex dependencies if its underlying bus is no longer available. Writing the wrong magic can boot the wrong mode. Forgetting devm or explicit unregister can leave stale notifier/list entries on driver removal.

## Test Signals

Tests should validate registration/unregistration, devm cleanup, each configured reboot mode's magic write, behavior during panic/restart paths if supported, and persistence across an actual reset on the target platform.
