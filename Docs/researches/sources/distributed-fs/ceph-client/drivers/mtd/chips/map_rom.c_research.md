## sources/distributed-fs/ceph-client/drivers/mtd/chips/map_rom.c

Purpose: exposes a memory-mapped ROM range as a read-only `MTD_ROM` device. It provides direct reads and optional `point()` access while rejecting writes and erases with `-EROFS`.

Important APIs, types, and functions: `map_rom_probe()` initializes `mtd_info`; `default_erasesize()` reads an optional Device Tree `erase-size` property; `maprom_read()`, `maprom_write()`, `maprom_erase()`, `maprom_point()`, and `maprom_unpoint()` are the callbacks. The chip-driver name is `map_rom`.

Control flow: probe allocates the MTD, sets type/caps/size, installs callbacks, sets erasesize from DT or the whole map size, and takes a module reference. Reads use `map_copy_from()`. `point()` returns direct virtual and optional physical addresses if `map->virt` exists.

State and persistence: no mutable media state exists. The persistent software state is only the mapped address metadata and MTD structure.

Dependencies and integration points: integrates with map drivers, OF properties, and the MTD chip registry. Useful for firmware images or board ROM windows that should be visible through MTD APIs.

Risks: erase size defaults to full map size unless DT supplies `erase-size`, which can affect partition tooling expectations. Like `map_ram`, it relies on upper layers for range validation.

Test signals: read correctness, `point()`/`unpoint()` behavior, write and erase returning `-EROFS`, DT `erase-size` parsing, and successful fallback to full-size erase geometry.
