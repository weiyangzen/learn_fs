<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/netsc520.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/netsc520.c

Purpose: static map driver for the AMD NetSc520 demonstration board flash region and its predefined partitions.

Important APIs, types, and functions: `netsc520_map` defines the flash window, `partition_info[]` defines boot kernel, low BIOS, filesystem, and high BIOS partitions, and lifecycle functions are `init_netsc520()` and `cleanup_netsc520()`.

Control flow: init ioremaps the fixed window, initializes simple map methods, probes in order with `cfi_probe`, `map_ram`, then `map_rom`, sets module ownership, and registers static partitions. Cleanup unregisters/destroys the MTD and unmaps the window.

State and persistence: flash contents persist in static partitions. Runtime state is global map and MTD pointer.

Dependencies and integration points: depends on MELAN/Sc520 platform config, MTD CFI/map RAM/ROM probes, and MTD partition registration.

Risks: comments describe a 16 MiB flash bank but `WINDOW_SIZE` is 1 MiB in the viewed source, so partition sizes extending beyond the map require validation against actual platform mapping. BIOS partitions are dangerous to mount/write. Test signals are probe fallback behavior, partition boundaries, and filesystem partition accessibility without touching BIOS partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/netsc520.c -->
