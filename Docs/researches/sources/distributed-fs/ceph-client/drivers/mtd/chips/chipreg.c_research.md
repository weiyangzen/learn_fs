## sources/distributed-fs/ceph-client/drivers/mtd/chips/chipreg.c

Purpose: supplies the small registry that map drivers use to discover and invoke MTD chip drivers by name. It hides module lookup/loading and provides the shared `do_map_probe()` and `map_destroy()` lifecycle helpers.

Important APIs, types, and functions: `register_mtd_chip_driver()` and `unregister_mtd_chip_driver()` maintain the global list. `do_map_probe()` finds or requests a named module and calls its `.probe`. `map_destroy()` calls the selected chip driver `.destroy`, drops the module reference held by the mapped device, and frees `mtd_info`.

Control flow: chip drivers register at module init under `chip_drvs_lock`. A board/map driver calls `do_map_probe("cfi_probe", map)` or similar; the registry tries the current list, then `request_module(name)`, then probes. On success, the probe usually sets `map->fldrv` and takes its own module reference; `do_map_probe()` releases the temporary probe-driver reference.

State and persistence: global state is only `chip_drvs_list` protected by a spinlock. Per-device lifetime is represented by `map->fldrv` and module refcounts, not by this file.

Dependencies and integration points: used by CFI/JEDEC/map_ram/map_rom/map_absent drivers and platform map drivers. It depends on kernel module loading and the `struct mtd_chip_driver` contract from `linux/mtd/map.h`.

Risks: callers must unregister the MTD device before `map_destroy()`. A driver that fails to set `map->fldrv` or take a module reference can break lifetime assumptions. Registry lookup is name-based, so module aliases and registration names must remain consistent.

Test signals: probing built-in and modular chip drivers, module autoload by probe name, unregister/reload races, correct module refcount behavior after probe-only modules hand off to command-set modules, and clean `map_destroy()` without leaks.
