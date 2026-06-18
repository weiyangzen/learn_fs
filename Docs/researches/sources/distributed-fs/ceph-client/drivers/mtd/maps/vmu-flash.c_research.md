# sources/distributed-fs/ceph-client/drivers/mtd/maps/vmu-flash.c

Purpose: Sega Dreamcast Visual Memory Unit memory-card MTD driver. Unlike simple map drivers, it implements MTD `_read` and `_write` over the Maple bus, discovers VMU partitions via `GETMINFO`, and registers one MTD device per VMU partition.

Important APIs/types/functions: `struct memcard`, `struct vmupart`, `struct vmu_cache`, `struct mdev_part`, `ofs_to_block()`, `maple_vmu_read_block()`, `maple_vmu_write_block()`, `vmu_flash_read()`, `vmu_flash_write()`, `vmu_queryblocks()`, `vmu_connect()`, `vmu_disconnect()`, and Maple driver registration. It depends on Maple packet commands, `mtd_device_register()`, wait queues, `atomic_t busy`, and kmsg device hotplug behavior.

Control flow: Maple probe installs unload/error handlers and calls `vmu_connect()`, which decodes function data, allocates card/partition/MTD arrays, stores drvdata, and sends an async meminfo request. `vmu_queryblocks()` receives partition geometry, allocates names/cache/private data, fills `mtd_info` callbacks and geometry, registers the MTD, then recursively queries further partitions. Reads convert offsets to blocks, use a one-second valid block cache, and fetch missing blocks through phased Maple reads. Writes read-modify-write full VMU blocks and invalidate cache. Disconnect unregisters all partition MTDs and frees arrays.

State and persistence: persistent state is VMU flash blocks. Runtime state includes per-partition cache buffers, Maple busy state, pending read buffer pointer, partition metadata, and registered MTD objects.

Risks and test signals: hot-unplug is explicitly awkward; read/write paths must translate `busy == 2` to errors. Several failure paths allocate nested objects and require precise cleanup. Tests should cover phased read/write counts, cache hit/expiry, boundary truncation, interrupted waits, unplug during I/O, multi-partition recursion, and open-ref refusal in `vmu_can_unload()`.
