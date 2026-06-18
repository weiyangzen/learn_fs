# sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.h

Purpose: Provides the internal coreboot bus interface shared by Google firmware drivers.

Important APIs/types/functions: `coreboot_device` embeds a `struct device` plus a union of possible coreboot table entry payloads (`coreboot_table_entry`, `lb_cbmem_ref`, `lb_cbmem_entry`, `lb_framebuffer`, or raw bytes). `coreboot_driver` wraps probe/remove callbacks, a `device_driver`, and an ID table. `dev_to_coreboot_device()`, `coreboot_driver_register()`, `__coreboot_driver_register()`, `coreboot_driver_unregister()`, and `module_coreboot_driver()` form the driver API.

Control flow: No independent runtime flow. Drivers include this header, declare `coreboot_device_id` tables, and use `module_coreboot_driver()` to bind to devices created by `coreboot_table.c`.

State and persistence behavior: No state here. The union layout determines how downstream drivers interpret copied firmware table entries.

Dependencies and integration points: Depends on `<linux/coreboot.h>` and the device model. Used by CBMEM, framebuffer, memconsole-coreboot, and VPD drivers.

Risks and test signals: Because the union overlays raw firmware data, every consumer must match on tag before using a typed member and respect entry sizes. Test signals are compile coverage for all consumers and runtime binding to each supported coreboot tag.
