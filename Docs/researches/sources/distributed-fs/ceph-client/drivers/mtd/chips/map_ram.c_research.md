## sources/distributed-fs/ceph-client/drivers/mtd/chips/map_ram.c

Purpose: exposes a memory-mapped RAM range as an `MTD_RAM` device. It supports direct reads/writes, panic writes, erase-by-filling-0xff, and optional direct `point()` access for XIP-like users.

Important APIs, types, and functions: `map_ram_probe()` initializes `mtd_info` with `MTD_CAP_RAM`; `mapram_read()`, `mapram_write()`, `mapram_erase()`, `mapram_point()`, and `mapram_unpoint()` implement the MTD callbacks. The chip-driver name is `map_ram`.

Control flow: probe currently trusts the map as RAM because the destructive test writes are compiled out. It sets erasesize to PAGE_SIZE and halves it until it divides the mapped size. Read/write use `map_copy_from()` and `map_copy_to()`. Erase writes an all-ones map word across the requested range.

State and persistence: data persists only in the underlying mapped RAM for as long as the platform preserves it. Software state is the `mtd_info` and `map_info`.

Dependencies and integration points: used by map drivers that provide RAM-backed flash-like regions. Direct access is disabled when `map->phys == NO_XIP`.

Risks: no bounds checks are visible in the callbacks, so MTD core validation is relied on. Probe does not verify the memory really is writable RAM. Erase loops in map-bankwidth increments and assumes aligned lengths.

Test signals: read-after-write, panic-write path, erasesize selection for non-page-multiple sizes, erase producing 0xff, `point()` returning virtual and physical addresses when available, and clean module registration/unregistration.
