# sources/distributed-fs/ceph-client/fs/ext4/fsmap.h

## Purpose
`fsmap.h` defines ext4's internal representation and owner namespace for filesystem mapping queries. It isolates the byte-oriented userspace `struct fsmap` ABI from ext4's block-oriented internal query engine.

## Important APIs, types, and functions
The core types are `struct ext4_fsmap`, which stores list linkage, device id, flags, physical block offset, owner, and block length, and `struct ext4_fsmap_head`, which stores ioctl flags, entry counts, and low/high keys. It declares `ext4_fsmap_from_internal`, `ext4_fsmap_to_internal`, `ext4_getfsmap`, and the formatter callback type `ext4_fsmap_format_t`. It also defines callback continuation codes and owner constants for free space, unknown ownership, static filesystem metadata, journal log, inode tables, group descriptors, reserved GDT blocks, block bitmaps, and inode bitmaps.

## Control flow
Callers translate ioctl keys into `ext4_fsmap` keys, call `ext4_getfsmap()`, and supply a formatter that copies or counts records. The implementation in `fsmap.c` fills `ext4_fsmap` records and converts them back before returning to userspace.

## State and persistence behavior
The header itself has no mutable state. Its structures describe transient query state and returned records. Owner constants are part of the user-visible interpretation of persistent disk regions, so renumbering them would affect tooling.

## Dependencies and integration points
It depends on the generic `fsmap` owner definitions and kernel list heads. It is used by ext4 ioctl code and by `fsmap.c`, with owner values shared conceptually with XFS where generic constants exist.

## Risks and test signals
Risks are ABI confusion between byte and block units, insufficient reserved-field clearing in converters, owner-code drift from userspace expectations, and formatter implementations that mishandle `fmh_entries`. Test signals include ioctl structure round trips, owner decoding in xfs_io-style tools, empty/count-only queries, and mappings for each special owner type.
