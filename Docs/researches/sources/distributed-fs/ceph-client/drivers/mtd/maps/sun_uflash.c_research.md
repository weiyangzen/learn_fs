# sources/distributed-fs/ceph-client/drivers/mtd/maps/sun_uflash.c

Purpose: OpenFirmware/platform driver for user-programmable Sun EBus flashprom devices. It intentionally binds only flash nodes with a `user` property and avoids OBP flash, maps the resource, probes CFI, and registers a whole-device MTD.

Important APIs/types/functions: `struct uflash_dev`, `uflash_map_templ`, `uflash_probe()`, `uflash_devinit()`, `uflash_remove()`, OF match name `"flashprom"`. It depends on OF properties (`user`, `model`), platform resources, `of_ioremap()`/`of_iounmap()`, `simple_map_init()`, `do_map_probe("cfi_probe")`, and `mtd_device_register()`.

Control flow: platform probe checks the OF node for `user`, then rejects devices with `resource[1].flags` as unsupported non-CFI flash. It allocates per-device state, copies the map template, sizes it from resource 0, uses the model as map name when present, maps the resource, probes CFI, registers the MTD, and stores driver data. Remove unregisters/destroys the MTD, unmaps the resource, and frees state.

State and persistence: state is per platform device, not global. Flash content persists; no partitions are parsed here. Model-derived names affect sysfs and MTD naming.

Risks and test signals: the `resource[1]` access assumes platform resources are populated as expected. Unsupported non-CFI hardware is hard rejected. Tests should cover absent `user`, non-CFI marker, missing model fallback, failed map/probe cleanup, registration success, and remove idempotence.
