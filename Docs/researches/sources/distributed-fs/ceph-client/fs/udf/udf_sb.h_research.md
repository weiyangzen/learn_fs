# sources/distributed-fs/ceph-client/fs/udf/udf_sb.h

## Purpose
`udf_sb.h` defines UDF superblock-private state, mount/compatibility flags, partition-map state, and helpers for querying and mutating filesystem flags.

## Important APIs, types, and functions
Key types are `struct udf_meta_data`, `struct udf_sparing_data`, `struct udf_virtual_data`, `struct udf_bitmap`, `struct udf_part_map`, and `struct udf_sb_info`. It defines read/write revision limits, mount flags such as `UDF_FLAG_USE_AD_IN_ICB`, `UDF_FLAG_STRICT`, `UDF_FLAG_RW_INCOMPAT`, partition flags, map type constants, metadata flags, `UDF_SB()`, `UDF_QUERY_FLAG`, `UDF_SET_FLAG`, and `UDF_CLEAR_FLAG`.

## Control flow
There is no independent control flow. `super.c` allocates, fills, and frees this state at mount/unmount; `partition.c` dispatches through `s_partition_func`; allocation and namespace paths use `s_alloc_mutex`, LVID state, and mount flags to decide behavior.

## State and persistence
`udf_sb_info` holds runtime representation of persistent media state: partition maps, volume identifier, session/anchor/last block, LVID buffer, root partition, serial number, UDF revision, VAT inode, and NLS map. Permission defaults, mount flags, allocation mutex, and dirty-LVID marker are runtime mount state.

## Dependencies and integration points
It depends on Linux bitops, mutexes, magic values, NLS, buffer heads, and inodes. It is the shared state surface between `super.c`, `partition.c`, `namei.c`, allocation, inode writeback, and `statfs`.

## Risks and test signals
Risks include wrong map type dispatch, stale LVID dirty state, mutable permission defaults racing without `s_cred_lock`, and treating `RW_INCOMPAT` as writable. Test signals include all partition map variants, remount option changes, LVID updates under allocation and namespace mutations, and read-only fallback when unsupported write features appear.
