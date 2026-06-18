# sources/distributed-fs/ceph-client/drivers/base/auxiliary.c

## Purpose
Implements the auxiliary bus, a driver-core bus for logical subdevices split out of a parent device when platform/MFD buses are not appropriate. It provides device/driver matching, uevents, probe/remove/shutdown bridging, registration helpers, and managed device creation.

## Important APIs, Types, And Functions
- Bus callbacks: `auxiliary_match()`, `auxiliary_uevent()`, `auxiliary_bus_probe()`, `auxiliary_bus_remove()`, and `auxiliary_bus_shutdown()`.
- Device APIs: `auxiliary_device_init()`, `__auxiliary_device_add()`, `auxiliary_device_create()`, `auxiliary_device_destroy()`, `__devm_auxiliary_device_create()`, and `dev_is_auxiliary()`.
- Driver APIs: `__auxiliary_driver_register()` and `auxiliary_driver_unregister()`.
- `auxiliary_match_id()` compares an auxiliary device name prefix against a driver's ID table.

## Control Flow
The bus is registered from `auxiliary_bus_init()`. Parent drivers initialize an auxiliary device with parent/name/id/release, then add it using a module-name-derived device name. Auxiliary drivers register with an ID table and probe callback; matching compares the device name up to the last dot against ID table names. Probe attaches a PM domain with power-on flags before calling the auxiliary driver's probe.

## State And Persistence
Persistent state is normal driver-core bus/device/driver state plus per-device sysfs lock initialized in `auxiliary_device_init()`. Helper-created devices own copied OF node references and are freed by `auxiliary_device_release()`.

## Dependencies And Integration Points
Depends on the Linux device model, PM domains/runtime PM, module ownership, OF node reference handling, and public `linux/auxiliary_bus.h`. `base.h` declares `auxiliary_bus_init()` for driver-core startup.

## Risks And Edge Cases
Device names must include dots in the expected `modname.name.id` format; `auxiliary_uevent()` assumes a last dot exists. Driver ops-based extension is documented as race-prone compared with exported-symbol infrastructure. Failed `__auxiliary_device_add()` requires `auxiliary_device_uninit()`, not direct free, because release owns cleanup after initialization.

## Test Signals
Valid/invalid device init fields, match-name edge cases, module alias generation, PM-domain attach failure, driver register without probe/id table, helper create/destroy and devm cleanup, and probe/remove/shutdown callback ordering are important tests.
