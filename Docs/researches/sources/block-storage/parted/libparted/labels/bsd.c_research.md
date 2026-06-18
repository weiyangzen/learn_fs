# File Research: sources/block-storage/parted/libparted/labels/bsd.c

Purpose: BSD disklabel backend for reading and writing classic 8-slot BSD labels.

Main interfaces: Registers `PedDiskType` named `bsd`. Implements probe, alloc, duplicate, free, read, write, partition allocation/duplication/destruction, system mapping, boot/RAID/LVM flags, alignment, enumeration, and metadata reservation.

Control flow: `bsd_probe()` reads sector 0 and checks the label at offset 64 for little-endian `BSD_DISKMAGIC`. `bsd_alloc()` initializes a default SCSI-style label from BIOS geometry. `bsd_read()` copies sector-zero label data and creates active partitions from nonzero size/type entries. `bsd_write()` optionally preserves existing boot code, clears and refills raw partition entries, updates `d_npartitions`, computes the XOR checksum, computes Alpha bootblock checksum, writes sector data, and syncs.

Data model: `BSDDiskData` contains 64 bytes of boot code, a packed `BSDRawLabel`, and trailing unused bytes. Per-partition private data stores raw BSD type plus libparted boot/RAID/LVM booleans.

Important details and risks: `d_npartitions` is written as `max_part + 1`, which reflects historical label semantics but deserves regression coverage. Flag state is libparted-private and does not appear to affect raw BSD partition type beyond `bsd_partition_set_system()`. Alignment reserves sector 0 metadata and allows partitions from sector 1 onward. Tests should cover checksum round trips, boot-code preservation, slot enumeration, Linux swap system mapping, and invalid/corrupt labels.
