# sources/distributed-fs/ceph-client/drivers/mtd/ftl.c

Purpose: legacy Flash Translation Layer block translation driver for PCMCIA-style FTL-formatted MTD devices. It exposes a 512-byte-sector block device through `mtd_blktrans_ops`.

Important APIs/types/functions: `partition_t` stores the blktrans device, FTL header, virtual block map, erase-unit info, transfer-unit info, BAM cache, and counters. Discovery/build functions are `scan_header()` and `build_maps()`. Maintenance functions include `erase_xfer()`, `prepare_xfer()`, `copy_erase_unit()`, `reclaim_block()`, `find_free()`, and `set_bam_entry()`. Block callbacks are `ftl_readsect()`, `ftl_writesect()`, `ftl_discardsect()`, and `ftl_getgeo()`.

Control flow: when an MTD appears, `ftl_add_mtd()` scans the first MiB for an `FTL100` header, validates geometry against MTD erasesize, builds erase-unit and virtual-sector maps from headers/BAMs, then registers a blktrans device. Reads translate virtual sectors through `VirtualBlockMap` to erase-unit offsets or return zeroes for unmapped sectors. Writes reclaim space if needed, reserve a free BAM entry, write the data sector, mark old mappings deleted, then publish the new mapping. Reclaim chooses a prepared transfer unit, copies a selected erase unit into it, swaps metadata, and erases the old unit.

State and persistence: persistent on-flash state is the FTL header, per-erase-unit headers, BAM entries, erase counts, data sectors, deleted/free/control markers, and transfer units. Runtime state caches those maps and one BAM. `shuffle_freq` affects wear-leveling selection.

Dependencies/integration: MTD read/write/erase/sync APIs, MTD block translation framework, `linux/mtd/ftl.h` format macros, vmalloc/kmalloc, and 512-byte sector semantics.

Risks: legacy format has patent/licensing caveats for non-PCMCIA uses. Error handling often returns generic `-EIO` and may leave partially updated BAM state after power loss. Reclaim logic is complex and relies on correct transfer-unit preparation. `ftl_add_mtd()` leaks built maps if `add_mtd_blktrans_dev()` fails after successful build.

Test signals: formatted and corrupt header scans, erasesize mismatch, map build from representative BAM states, read unmapped sectors as zero, write update ordering, discard deleting mappings, reclaim under low free space, transfer erase failures, and blktrans add/remove cleanup.
