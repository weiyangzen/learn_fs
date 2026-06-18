# sources/distributed-fs/ceph-client/drivers/mtd/maps/uclinux.c

Purpose: generic uClinux direct-mapped ROM/RAM filesystem MTD driver. It exposes a ROMfs image directly following kernel BSS, or at a module-supplied physical address, as a single `"ROMfs"` MTD partition using either `map_rom` or `map_ram` depending on configuration.

Important APIs/types/functions: `uclinux_ram_map`, `physaddr` module parameter, `uclinux_point()`, `uclinux_mtd_init()`, `uclinux_romfs`. It depends on linker symbol `__bss_stop`, `phys_to_virt()`, ROMfs size at offset 8 in network byte order, `PAGE_ALIGN()`, `simple_map_init()`, `do_map_probe("map_rom"/"map_ram")`, and `mtd_device_register()`.

Control flow: device init selects physical base, derives size from the ROMfs header when not preset, sets 32-bit bankwidth, translates to virtual memory, initializes the map, probes the matching map driver, overrides `_point` for direct access, saves the MTD pointer, and registers one partition.

State and persistence: the mapped image is persistent only if backed by ROM/flash; RAM mode is volatile. `_point` exposes direct virtual and optional physical addresses for XIP/NOMMU-style users.

Risks and test signals: it trusts the image header at `phys + 8` and casts physical addresses directly while deriving size before `phys_to_virt()`. There is no cleanup path because it uses `device_initcall`. Tests should validate boot-time image discovery, explicit `physaddr`, invalid/missing mapping, size alignment, `_point` address translation, and ROM vs RAM config behavior.
