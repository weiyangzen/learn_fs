# sources/distributed-fs/ceph-client/fs/udf/udfend.h

## Purpose
`udfend.h` provides small endian-conversion helpers for UDF logical block addresses and allocation descriptors, converting between on-disk little-endian structures and kernel-native helper structures.

## Important APIs, types, and functions
It defines `lelb_to_cpu`, `cpu_to_lelb`, `lesa_to_cpu`, `cpu_to_lesa`, `lela_to_cpu`, `cpu_to_lela`, and `leea_to_cpu`. The converted structures include `lb_addr`, `short_ad`, `long_ad`, `kernel_long_ad`, and `kernel_extent_ad`.

## Control flow
There is no branching beyond field-by-field conversion. Callers use these helpers when reading FIDs, file set descriptors, logical volume contents, extent descriptors, and when writing FID ICB locations or allocation descriptors.

## State and persistence
The helpers do not own state. They are persistence-critical because they determine the byte order of block numbers, partition references, extent lengths, and descriptor locations written to disk.

## Dependencies and integration points
It depends on Linux byteorder helpers and is included by `udfdecl.h`. `namei.c`, `super.c`, `partition.c`, inode extent code, and truncation paths all use these conversions.

## Risks and test signals
Risks include double conversion, missing conversion on mixed-endian fields, and confusing native `kernel_*` structures with disk structures. Test signals include mounting and mutating media on big-endian and little-endian systems, FID location checks, allocation descriptor round trips, and metadata partition extent traversal.
