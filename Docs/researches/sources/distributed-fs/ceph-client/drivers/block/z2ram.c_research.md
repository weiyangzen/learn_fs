# sources/distributed-fs/ceph-client/drivers/block/z2ram.c

Purpose: Amiga-specific RAM disk block driver exposing unused Zorro II RAM, Chip RAM, or selected memory-list entries as `/dev/z2ram*` devices for swap or ramdisk use.

Important APIs/types/functions: global state includes `z2ram_map`, `z2ram_size`, memory counters, `current_device`, per-minor `gendisk` pointers, a global mutex, and an I/O spinlock. `z2_queue_rq()` copies request data between block bios and mapped RAM chunks. `get_z2ram()` consumes bits from `zorro_unused_z2ram`; `get_chipram()` allocates Chip RAM chunks. `z2_open()` selects memory according to the minor, builds the chunk map, and sets capacity. `z2_init()` registers the fixed major, blk-mq tag set, and disks.

Control flow: module init only succeeds on Amiga hardware, registers major 37, initializes a single-queue blk-mq tag set, and creates minors. Opening a minor lazily claims the selected memory pool and fixes the driver to that single active minor. Requests bounds-check sector ranges, translate logical offsets through `z2ram_map`, and copy under `z2ram_lock`. Exit unregisters disks and returns claimed Zorro/Chip memory where implemented.

State and persistence: all backing storage is volatile physical RAM. The active minor and map are global, so only one configuration can be open at a time. Zorro RAM is marked used by clearing `zorro_unused_z2ram` and partially restored on module exit. Release does not tear down the active mapping and contains a FIXME for unmapping memory.

Dependencies and integration: depends on m68k/Amiga setup, `amigahw`, Zorro memory metadata, Chip RAM allocation APIs, low-level remapping for memory-list entries, and blk-mq/gendisk block APIs.

Risks: global single-device state makes concurrent opens sensitive; release is incomplete; memory-list mappings have architecture-specific remap behavior; request handling assumes the request bio buffer can be copied directly for the current segment; cleanup is asymmetric for list-entry mappings. Fixed major/minor layout constrains extension.

Test signals: test Amiga-only probe rejection elsewhere, each minor mode, invalid memory-list indexes, no-memory cases, read/write across chunk boundaries, out-of-range I/O, repeated opens of same vs different minors, module unload memory restoration, and blk-mq error return behavior.
