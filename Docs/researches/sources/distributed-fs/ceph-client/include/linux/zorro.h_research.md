# sources/distributed-fs/ceph-client/include/linux/zorro.h

## Purpose
Defines the Linux Amiga Zorro AutoConfig bus device and driver interfaces. It bridges architecture-discovered Zorro expansion boards into the generic device model and exposes helpers for resource management, driver registration, device lookup, and Zorro II RAM tracking.

## Important APIs, Types, and Functions
`struct zorro_dev` represents a discovered expansion device with ROM data, `zorro_id`, generic `struct device`, slot address/size, name, and memory resource. `struct zorro_driver` contains list linkage, name, optional match table, `probe`/`remove` callbacks, and embedded `device_driver`. Conversion helpers are `to_zorro_dev()` and `to_zorro_driver()`. Iteration uses `zorro_for_each_dev()`. Driver APIs are `zorro_register_driver()` and `zorro_unregister_driver()`. Global discovery state is `zorro_num_autocon`, `zorro_autocon`, and init-time `zorro_autocon_init[]`. Resource helpers expose start/end/length/flags and wrap `request_mem_region()`/`release_mem_region()`. `zorro_get_drvdata()` and `zorro_set_drvdata()` wrap generic device driver data. Zorro II RAM constants and `zorro_unused_z2ram` track allocatable 64 KiB chunks.

## Control Flow
Architecture boot code discovers AutoConfig boards into temporary init data, the Zorro bus creates persistent `zorro_dev` objects, and drivers register match tables plus callbacks. The bus matches devices and calls `probe`; drivers request the memory resource before using board address space and release it on remove. Lookup and iteration helpers allow legacy code to scan all discovered boards.

## State and Persistence
Persistent state includes the `zorro_autocon` array of devices, each device's resource and driver data, registered driver list, and the `zorro_unused_z2ram` bitmap. `zorro_autocon_init[]` is `__initdata` and valid only until init memory is freed.

## Dependencies and Integration Points
Depends on UAPI Zorro IDs, generic device model, init annotations, ioport resources, module device tables, and architecture `asm/zorro.h`. Integrates with Amiga/m68k platform setup, memory-resource management, module autoloading, and legacy Zorro board drivers.

## Risks
Use of init-only discovery data after boot is invalid. Drivers must request resources to avoid overlapping MMIO use. `remove` can be NULL for non-hotplug-capable drivers, so callers must respect optional removal. Zorro II RAM bitmap users must clear bits for allocated chunks to avoid double allocation.

## Test Signals
Signals include m68k/Amiga build and boot tests, Zorro driver probe/remove tests, resource conflict tests, module alias matching, `zorro_find_device()` coverage, and Zorro II RAM allocation bitmap validation.
