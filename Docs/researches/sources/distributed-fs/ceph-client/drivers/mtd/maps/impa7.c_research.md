<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/impa7.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/impa7.c

Purpose: board map driver for implementa impA7 NOR flash, exposing two fixed 8 MiB banks.

Important APIs, types, and functions: `impa7_map[]` contains two `map_info` entries, `impa7_mtd[]` stores detected devices, `partitions[]` defines a single `FileSystem` partition, and lifecycle functions are `init_impa7()` and `cleanup_impa7()`.

Control flow: init iterates two fixed physical windows, ioremaps each, initializes simple map hooks, probes with `jedec_probe`, registers the single partition on each found chip, and unmaps banks that do not probe. Cleanup unregisters/destroys/unmaps each detected MTD.

State and persistence: persistent state is NOR contents in fixed banks. Runtime state is the two map structures and MTD pointers.

Dependencies and integration points: depends on ARM, JEDEC probe support, MTD partition registration, and static board memory map.

Risks: first-bank ioremap failure returns without cleaning previously mapped banks in unusual partial-failure cases. Partition size is fixed to 8 MiB and assumes bank size. Test signals are both bank probes, correct `impa7-%d` mtdparts naming expectation from comments, partition registration, and clean module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/impa7.c -->
