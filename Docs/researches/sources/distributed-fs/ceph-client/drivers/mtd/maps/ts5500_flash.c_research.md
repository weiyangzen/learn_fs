# sources/distributed-fs/ceph-client/drivers/mtd/maps/ts5500_flash.c

Purpose: fixed physical map driver for the Technology Systems TS-5500 board flash. It maps a 2 MiB 8-bit window at `0x09400000`, probes JEDEC flash with ROM fallback, and registers three static partitions named Drive A, BIOS, and Drive B.

Important APIs/types/functions: `ts5500_map`, `ts5500_partitions`, `init_ts5500_map()`, `cleanup_ts5500_map()`, `mymtd`. It depends on `ioremap()`, `simple_map_init()`, `do_map_probe("jedec_probe")`, `do_map_probe("map_rom")`, `mtd_device_register()`, and static board partition definitions.

Control flow: init maps the fixed window, initializes the map, probes JEDEC then ROM, sets module owner, and registers the partitions. If mapping or probing fails, it unwinds the map and returns `-EIO` or `-ENXIO`. Cleanup unregisters and destroys the MTD if present, then unmaps the window.

State and persistence: all runtime state is static and single-device. Flash contents persist; partition boundaries are hard-coded and reflect BIOS/RFD layout assumptions.

Risks and test signals: no memory-region reservation is performed, so conflicts are not detected. ROM fallback can expose read-only flash while still using static partitioning. Tests should cover absent flash, ROM fallback, partition offsets/sizes, failed mapping cleanup, and successful unregister/unmap.
