## sources/distributed-fs/ceph-client/drivers/mtd/chips/map_absent.c

Purpose: implements a placeholder chip driver for socketed or removable map devices when real probing fails. It creates an `MTD_ABSENT` device so expected MTD device nodes can exist even though all data operations fail.

Important APIs, types, and functions: `map_absent_probe()` allocates and initializes `mtd_info`; `map_absent_read()`, `map_absent_write()`, and `map_absent_erase()` all return `-ENODEV`; `map_absent_sync()` and `map_absent_destroy()` are no-ops. The registered chip-driver name is `map_absent`.

Control flow: a board driver can call `do_map_probe("map_absent", map)` after CFI/JEDEC failures. Probe fills size from `map->size`, assigns PAGE_SIZE erase size and writesize 1, takes a module reference, and returns the placeholder MTD.

State and persistence: only the allocated `mtd_info` and `map->fldrv` persist. There is no backing storage or hardware state.

Dependencies and integration points: integrates with the map chip registry and MTD core. It is useful as a fallback policy in board-specific map drivers.

Risks: userspace sees a device but cannot read/write/erase it. Any code that assumes a registered MTD implies usable media must check `type` or operation errors.

Test signals: fallback registration after missing media, open/read/write/erase returning `-ENODEV`, stable device sizing for expected partitions, and clean unregister through `map_destroy()`.
