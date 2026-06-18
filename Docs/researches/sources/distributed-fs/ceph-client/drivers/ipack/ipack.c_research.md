# sources/distributed-fs/ceph-client/drivers/ipack/ipack.c

Purpose: Implements the Linux IndustryPack bus core. It registers the `ipack` bus type, matches devices by ID ROM metadata, exposes sysfs/modalias data, registers carrier buses and IPACK drivers, initializes devices, and parses ID PROM formats.

Important APIs/types/functions: `ipack_bus_register()`, `ipack_bus_unregister()`, `ipack_driver_register()`, `ipack_device_init()`, `ipack_device_add()`, `ipack_device_del()`, `ipack_device_read_id()`, `ipack_parse_id1()`, `ipack_parse_id2()`, `ipack_match_id()`, `ipack_bus_type`, and exported get/put helpers.

Control flow: Bus init registers `ipack_bus_type`. Carriers allocate a bus number, create `ipack_device`s, and call `ipack_device_init()`. Device init names the device, initializes it, forces 8 MHz for ID reads, resets timeouts, maps ID space, detects format 1 or VITA 4 format 2 PROMs, copies the ID bytes, validates CRC, and optionally switches to 32 MHz. Driver match compares format/vendor/device against the driver's ID table.

State and persistence: Global bus numbers are allocated through `ida`. Device state persists in embedded `struct device`, copied ID buffer, parsed ID fields, speed flags, CRC status, regions, and carrier bus pointer. Device release frees the copied ID then calls the carrier-provided release callback.

Dependencies/integration: Depends on Linux driver core, IDA, MMIO `ioremap`/`ioread`, IPACK public structs/macros, module aliases, and carrier-provided bus operations.

Risks and test signals: Test malformed/short ID PROMs, CRC mismatch warnings, format 1/2 modaliases, release callback correctness, bus unregister while children exist, clock-rate failures during init, and the `modalias_show()` string spelling versus uevent modalias.
