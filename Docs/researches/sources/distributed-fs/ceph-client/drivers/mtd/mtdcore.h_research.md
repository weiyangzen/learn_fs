# sources/distributed-fs/ceph-client/drivers/mtd/mtdcore.h

Purpose: private MTD core header shared by core-adjacent implementation files. It exposes internal registry, partition, parser, and char-device entry points that are intentionally not part of the public driver API.

Important APIs/types/functions: declarations for `mtd_table_mutex`, `mtd_bdi`, `__mtd_next_device()`, `add_mtd_device()`, `del_mtd_device()`, `add_mtd_partitions()`, `del_mtd_partitions()`, `release_mtd_partition()`, `parse_mtd_partitions()`, `mtd_part_parser_cleanup()`, `init_mtdchar()`, `cleanup_mtdchar()`, and `mtd_for_each_device`.

Control flow: the header has no executable flow, but it defines the internal iteration pattern used by notifiers and blktrans: start from `__mtd_next_device(0)` and request the next index after the current `mtd->index`.

State and persistence: it centralizes access to the global registry mutex and backing device info. It does not own persistent state.

Dependencies and integration: included by `mtdcore.c`, `mtdchar.c`, `mtd_blkdevs.c`, `mtdpart.c`, and virtual concat code when they need internal functions outside public `<linux/mtd/*.h>`.

Risks and test signals: because these symbols are internal, accidental external use would couple drivers to core internals. Tests are indirect: successful builds with partition, char, blktrans, and virtual concat configurations; lockdep coverage that callers hold `mtd_table_mutex` where required; and iterator behavior under dynamic add/remove.
