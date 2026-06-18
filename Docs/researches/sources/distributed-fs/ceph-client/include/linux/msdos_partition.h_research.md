<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_partition.h -->
# sources/distributed-fs/ceph-client/include/linux/msdos_partition.h

## Purpose
`msdos_partition.h` defines the classic MBR partition entry layout, label magic, and common system-indicator partition type values.

## Important APIs, Types, and Functions
It defines `MSDOS_LABEL_MAGIC`, packed `struct msdos_partition`, and `enum msdos_sys_ind` values for extended partitions, Linux data/LVM/RAID, Solaris, disk managers, BSDs, Minix, and UnixWare/Hurd/SCO.

## Control Flow and State
Partition parsers read packed entries from sector 0 or extended boot records, validate magic, interpret CHS/LBA fields, and use `sys_ind` to classify partitions.

## State and Persistence Behavior
The struct maps on-disk MBR/EBR data. No runtime state is owned here.

## Dependencies and Integration Points
It integrates with block partition scanning and disk-label code. Endianness is explicit for LBA fields via `__le32`.

## Risks
Packed layout must not change. CHS fields are legacy and often unreliable; parsers should prefer LBA. Type aliases can be ambiguous, especially `0x82`.

## Test Signals
Partition scan tests with primary, extended, logical, Linux RAID/LVM, BSD, Solaris, and malformed MBR images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/msdos_partition.h -->
