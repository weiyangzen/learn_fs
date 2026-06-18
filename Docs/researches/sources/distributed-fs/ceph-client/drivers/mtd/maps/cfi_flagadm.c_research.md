<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/cfi_flagadm.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/maps/cfi_flagadm.c

Purpose: static CFI map driver for the Flaga digital module flash at physical address `0x40000000`.

Important APIs, types, and functions: `flagadm_map` describes a 4 MiB, 16-bit map. `flagadm_parts` defines bootloader, kernel, initial ramdisk, and persistent storage partitions. `init_flagadm()` and `cleanup_flagadm()` handle lifecycle.

Control flow: module init ioremaps the fixed flash window, initializes simple map methods, probes with `cfi_probe`, sets module ownership, and registers the four static partitions. Cleanup unregisters the MTD, destroys the map, and unmaps IO memory.

State and persistence: persistent state is flash contents in fixed partitions. Runtime state is the global `mymtd` and `flagadm_map.virt`.

Dependencies and integration points: depends on PowerPC 8xx/Flaga platform config, MTD CFI, map APIs, and static partition registration.

Risks: fixed addresses and partitions must match board wiring. Failure to register partitions is not checked after `mtd_device_register()`. Test signals are successful ioremap, CFI detection, partition names/sizes, and clean unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/maps/cfi_flagadm.c -->
