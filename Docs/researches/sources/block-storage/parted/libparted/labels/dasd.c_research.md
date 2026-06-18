# File Research: sources/block-storage/parted/libparted/labels/dasd.c

Purpose: IBM S/390 DASD disk-label backend using fdasd/VTOC helpers, with support for CDL labels and read-only handling of LDL/CMS-style layouts.

Main interfaces: Registers `PedDiskType` named `dasd`. Implements probe, alloc, duplicate, free, read, write, partition allocation/duplication/destruction, flag mapping, alignment, enumeration, system mapping, metadata allocation, and partition limit reporting.

Control flow: `dasd_probe()` initializes an fdasd anchor, reads DASD geometry, and rejects missing labels on CDL devices. `dasd_read()` distinguishes unlabeled/FBA implicit partitions, LDL/CMS labels, and CDL/VTOC partitions. CDL partitions are created from `partition_info_t` track ranges, with free-space pseudo-partitions where fdasd reports gaps. `dasd_write()` refuses LDL/CMS mutation, recreates the VTOC for CDL, adds partitions by track range, updates DS1DSNAM type strings, prepares/writes labels, and cleans fdasd state.

Data model: Disk private data stores format type, label block, and volume label. Partition private data stores a raw type and Linux system ID. Supported flags map to Linux LVM, RAID, and swap type IDs.

Important details and risks: DASD alignment is track-based using Linux real sector size and hardware sectors per track. LDL/CMS format reports only one real partition and disables flags. `dasd_write()` has a local `part_info` array that is populated only for encountered partitions before `dasd_update_type()` consumes corresponding entries; sparse partition numbering should be tested carefully. Metadata allocation marks leading VTOC/label space and, for LDL/CMS, possible trailing metadata after the implicit partition. Tests require S390/fdasd fixtures or mocks for CDL, LDL, CMS, FBA, sparse partitions, and flag-to-type updates.
