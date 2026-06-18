<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/map_funcs.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/map_funcs.c

Purpose: provides out-of-line simple map IO operations when complex mappings are enabled.

Important APIs, types, and functions: `simple_map_init()` validates bank width and installs `simple_map_read()`, `simple_map_write()`, `simple_map_copy_from()`, and `simple_map_copy_to()`. The helpers wrap `inline_map_*` operations and are marked `__xipram`.

Control flow: drivers call `simple_map_init(&map)` after filling `virt`, `size`, `bankwidth`, and names. After that, chip probes use the installed hooks for reads, writes, and copies.

State and persistence: no persistent state. It mutates function pointers in caller-provided `struct map_info`.

Dependencies and integration points: depends on `linux/mtd/map.h`, `linux/mtd/xip.h`, and `map_bankwidth_supported()`. It exports `simple_map_init()` for map drivers.

Risks: unsupported bank width triggers `BUG_ON`, so callers must validate configuration first. Test signals are successful use by simple physmap/board drivers under `CONFIG_MTD_COMPLEX_MAPPINGS` and correct IO behavior matching inline map operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/map_funcs.c -->
