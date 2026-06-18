# sources/distributed-fs/ceph-client/drivers/firmware/google/coreboot_table.c

Purpose: Implements a `coreboot` bus and platform driver that maps the firmware coreboot table and creates one Linux device per table entry for other Google firmware drivers to bind.

Important APIs/types/functions: `coreboot_table_header` models the LBIO header. Bus callbacks are `coreboot_bus_match()`, `coreboot_bus_probe()`, `coreboot_bus_remove()`, and `coreboot_bus_uevent()`. Public exports are `__coreboot_driver_register()` and `coreboot_driver_unregister()`. `coreboot_table_populate()` creates `coreboot_device` instances.

Control flow: Init registers the bus and platform driver. Probe obtains the memory resource from ACPI `GOOGCB00`/`BOOT0000` or DT `compatible = "coreboot"`, maps the header, validates signature `LBIO`, maps the full table, iterates entries, copies raw entry data into allocated device storage, names CBMEM entries specially, and registers devices. Remove unregisters all bus devices.

State and persistence behavior: State consists of registered bus devices and copied firmware table entries. Firmware memory is read-only from this driver and unmapped after enumeration.

Dependencies and integration points: Integrates ACPI, OF, platform resources, the Linux driver core, and downstream coreboot drivers for CBMEM, framebuffer, memconsole, and VPD. Uevents expose `MODALIAS=coreboot:t%08X` for module autoloading.

Risks and test signals: The implementation validates entry size but does not verify header/table checksums. A malformed table could stop enumeration or create incorrect devices. Test with ACPI and DT discovery, multiple entry types, module autoload via modalias, remove/unbind cleanup, and corrupt signature/short entry cases.
