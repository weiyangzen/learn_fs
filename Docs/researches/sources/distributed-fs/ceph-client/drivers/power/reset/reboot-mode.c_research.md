# sources/distributed-fs/ceph-client/drivers/power/reset/reboot-mode.c

## Purpose
generic reboot-mode core framework.

## Important APIs, Types, and Functions
`struct mode_info`, reboot notifier, sysfs class/device helpers, property parser, `reboot_mode_register()`, `reboot_mode_unregister()`, and devm wrappers.

## Control Flow
providers register a `reboot_mode_driver` with a write callback; the core parses DT properties named for reboot modes into a list, registers a reboot notifier, exposes a class device, and on reboot command match writes the corresponding magic or normal magic.

## State and Persistence Behavior
mode list and class device persist until unregister; selected magic is not stored here, but delegated to provider write callbacks such as syscon or nvmem.

## Dependencies and Integration Points
reboot notifier chain, device class/sysfs, OF properties, devres, provider drivers.

## Risks and Edge Cases
mode-name parsing depends on DT property names; unregister must remove notifier and class device; write callback errors late in reboot may not stop reboot; list lifetime is per provider.

## Test Signals
register/unregister/devm paths, DT mode parsing, sysfs class device creation, reboot command matching, duplicate providers, and write failure injection.
