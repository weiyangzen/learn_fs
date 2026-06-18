# sources/distributed-fs/ceph-client/drivers/eisa/eisa-bus.c

## Purpose
`eisa-bus.c` implements the Linux EISA bus type, sysfs exposure, root registration, slot probing, resource reservation, driver matching, module alias generation, and legacy `EISA_bus` export.

## Important APIs, types, and functions
The exported integration points are `eisa_bus_type`, `eisa_driver_register()`, `eisa_driver_unregister()`, and `eisa_root_register()`. Internally, `decode_eisa_sig()` reads slot signatures, `eisa_init_device()` fills `struct eisa_device`, `eisa_request_resources()` reserves per-slot IO windows, `eisa_register_device()` registers sysfs attributes, and `eisa_probe()` scans slot 0 plus configured card slots. Module parameters `enable_dev[]` and `disable_dev[]` force per-bus/slot state.

## Control flow
`postcore_initcall(eisa_init)` registers the bus. Root providers call `eisa_root_register()`, which reserves the root IO range under a global EISA root resource, assigns a bus number, and probes. Probing tries slot 0 mainboard first and may continue when `force_probe` is set. For each slot, it reserves resources, decodes the vendor signature, reads the enabled bit, applies forced enable/disable, names the device, registers it on the EISA bus, and creates `signature`, `enabled`, and `modalias` sysfs files.

## State and persistence behavior
Runtime state consists of registered device objects, reserved IO resources, the monotonic `eisa_bus_count`, forced-device module parameter arrays, and the exported `EISA_bus` integer for legacy drivers. Device state is in memory only and disappears on reboot.

## Dependencies and integration points
The file depends on IO port accessors (`inb`, optional `outb` VLB priming), resource management, Linux driver core, sysfs device attributes, `include/linux/eisa.h`, and optional generated `devlist.h`. Drivers match by EISA signature and receive modalias strings through uevents.

## Risks and edge cases
Slot probing uses direct IO and can be unsafe on non-EISA or incorrectly forced systems. Resource reservation failures skip devices and can abort mainboard probing unless forced. Forced enable/disable parameters override hardware state and may bind drivers to disabled hardware. Device-name lookup is freed after init, so names must be copied. Attribute creation failures must unwind registered devices and resources.

## Test signals
Boot on real or emulated EISA hardware, forced-probe paths, `enable_dev`/`disable_dev` parameters, sysfs attribute content, modalias-based module loading, resource conflict handling, driver match for enabled-only devices, and `CONFIG_EISA_NAMES` on/off builds.
