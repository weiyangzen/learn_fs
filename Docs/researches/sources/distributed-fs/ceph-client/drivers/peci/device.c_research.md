# sources/distributed-fs/ceph-client/drivers/peci/device.c

Purpose: Handles PECI target detection, `struct peci_device` creation/destruction, CPU identity discovery, and PECI client-driver registration wrappers.

Important APIs and functions: `peci_device_create()` validates an address, skips existing children, pings the target, allocates a PECI device, initializes CPU information, names the device, and adds it to the bus. `peci_device_destroy()` unregisters devices once despite concurrent sysfs/controller removal. `__peci_driver_register()` and `peci_driver_unregister()` export PECI client driver registration. Helpers include `peci_get_cpu_id()`, `peci_get_revision()`, `peci_device_info_init()`, and x86 signature decoding helpers.

Control flow: Controller scanning calls `peci_device_create()` for each valid slot. Detection uses a zero-length PECI ping under `controller->bus_lock`; `-EIO` and `-ETIMEDOUT` mean absent or temporarily unavailable and are ignored. For responding targets, the code reads CPU ID via RdPkgConfig and DIB revision via GetDIB, computes x86 vendor-family-model, stores PECI revision and socket ID, then exposes the child device.

State and persistence: Created devices persist as children of the controller until sysfs remove or controller removal. `device->deleted` is protected by a global mutex to avoid double unregister. Device info stores derived CPU VFM, PECI revision, and socket ID. There is no persistent scan cache beyond existing child devices.

Dependencies and integration points: Depends on PECI request helpers, Linux device core, bitfield helpers, `peci-cpu.h` constants, and the PECI bus type in `core.c`. `sysfs.c` uses `peci_device_destroy()`, and `cpu.c` consumes initialized `device->info`.

Risks: Detection requires both CPU ID and nonzero DIB; targets that ping but cannot answer these reads are not registered. Existing-device detection returns success when an address is already present, so rescans are idempotent but do not refresh CPU info. The global deletion mutex protects double-delete, not other device state.

Test signals: Address validation, duplicate rescan behavior, absent target handling, nonzero DIB requirement, device names like `0-30`, sysfs remove races with controller removal, and client-driver registration failures without probe/id table.
