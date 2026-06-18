<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pxa2xx-flash.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/pxa2xx-flash.c

Purpose: platform map driver for NOR flash attached to Intel XScale PXA2xx systems.

Important APIs, types, and functions: `struct pxa2xx_flash_info` stores `mtd_info` and `map_info`. `pxa2xx_map_inval_cache()` invalidates cached flash mappings line by line. Lifecycle functions are `pxa2xx_flash_probe()`, `pxa2xx_flash_remove()`, and optional `pxa2xx_flash_shutdown()`.

Control flow: probe reads `flash_platform_data`, obtains memory resource 0, allocates state, fills map name/width/physical/size, ioremaps uncached and optionally cached aliases, installs cache invalidation and simple map methods, probes the platform-specified chip driver, sets parent device, parses/registers RedBoot/cmdline/static partitions, and stores driver data. Remove unregisters, destroys, unmaps both aliases, and frees state. Shutdown suspend/resume returns flash to read mode.

State and persistence: persistent state is NOR contents and partitions. Runtime state is map aliases and MTD pointer.

Dependencies and integration points: PXA flash platform data, MTD map probes, partition parsers, ARM cache maintenance instruction, and platform driver binding `pxa2xx-flash`.

Risks: probe assumes non-null platform data before dereferencing `flash->name` and `flash->width`. Cached mapping is optional but cache invalidation hook still references `map->cached`; callers must avoid invalidation when absent. Test signals are chip probe selection, cached/uncached alias behavior, partition parser output, cache invalidation after writes, and shutdown read-mode recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/pxa2xx-flash.c -->
