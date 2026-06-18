# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/generic.c

Purpose: implements a simple platform-device glue layer for memory-mapped OneNAND flash on generic boards.

Important APIs and types: `struct onenand_info` embeds `struct mtd_info` and `struct onenand_chip`. The platform driver uses `generic_onenand_probe()` and `generic_onenand_remove()` under driver name `onenand-flash`. It consumes optional `struct onenand_platform_data` for `mmcontrol` and partition arrays.

Control flow: probe allocates `onenand_info`, reserves the memory resource, ioremaps it into `onenand.base`, copies optional memory-control hook, obtains IRQ 0, initializes `mtd.dev.parent` and `mtd.priv`, scans the chip with `onenand_scan()`, registers the MTD device and partitions with `mtd_device_register()`, and stores drvdata. Error paths unwind ioremap, memory region, and allocation. Remove calls `onenand_release()`, releases the memory region, unmaps the base, and frees the wrapper.

State and persistence: runtime state is the mapped register/window base, IRQ, MTD object, OneNAND chip object, and registered partitions. Persistent state is the flash contents managed by the OneNAND core.

Dependencies and integration points: depends on platform resources, I/O memory mapping, OneNAND core scanning/release, MTD device registration, optional board platform data, and partition registration.

Risks and test signals: risks include resource lifetime ordering, missing/invalid IRQ or memory resources, partition registration failure handling, and compatibility with the renamed `onenand-flash` platform data format. Tests should cover successful probe/remove, no platform data, busy memory region, ioremap failure, IRQ failure, scan failure, partition registration failure, and repeated bind/unbind with resource cleanup.
