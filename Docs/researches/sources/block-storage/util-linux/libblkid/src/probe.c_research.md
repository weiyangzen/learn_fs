# File Research: sources/block-storage/util-linux/libblkid/src/probe.c

Low-level libblkid probing core. It allocates and owns `blkid_probe` state, opens devices/files, configures probing dimensions, initializes probing chains for superblocks, topology, and partitions, and exposes the string-based and binary result APIs used by the rest of libblkid.

Its central data flow is: set a device with offset/size, read aligned cached buffers from the target, run enabled chain drivers, store `NAME=value` results, and optionally wipe or hide detected signatures. The buffer layer uses anonymous `mmap`, read caching, parent-probe sharing for clones, prunable superseded buffers, O_DIRECT retry support, and range hiding for dry-run wipe loops.

Important behaviors include hidden/private device-mapper suppression, floppy and CD-ROM handling, OPAL lock detection, zoned-device wipe handling, whole-disk helper probes, chain filters, safe/full/progressive probe modes, checksum validation with optional bad-checksum acceptance, result lookup/enumeration, UUID formatting, wiper heuristics for signature conflict resolution, and numeric probing hints such as CD session offsets. Risk concentrates around offset arithmetic, device-size boundaries, I/O error interpretation, and preserving chain position semantics after filters or wipes.
