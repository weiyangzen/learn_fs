# sources/distributed-fs/ceph-client/fs/ntfs3/ntfs.h

## Purpose
`ntfs.h` is the NTFS3 on-disk format contract. It defines little-endian structures, constants, tags, attribute layouts, index records, reparse buffers, EA records, and security-descriptor fragments that other NTFS3 source files parse and mutate.

## Important APIs, Types, and Constants
`CLST` is the cluster-number type, normally 32 bit and optionally 64 bit under `CONFIG_NTFS3_64BIT_CLUSTER`. Sentinel LCNs distinguish sparse, resident, compressed, EOF, and delayed-allocation states. Core disk structures include `MFT_REF`, `NTFS_BOOT`, `NTFS_RECORD_HEADER`, `MFT_REC`, `ATTRIB`, `ATTR_RESIDENT`, `ATTR_NONRESIDENT`, `NTFS_DE`, `INDEX_HDR`, `INDEX_BUFFER`, `INDEX_ROOT`, `REPARSE_DATA_BUFFER`, `EA_INFO`, `EA_FULL`, and security descriptor/ACL/SID fragments. Helpers such as `ino_get()`, `attr_size()`, `attr_ondisk_size()`, `resident_data_ex()`, `attr_name()`, `attr_run()`, `hdr_first_de()`, and `hdr_next_de()` provide bounded access to variable-length disk records.

## Control Flow and Integration
The header has no standalone runtime path; it supplies parsing primitives to record, run, mount, xattr, security, directory, and index code. Callers use these definitions while traversing raw disk buffers, so the static layout assertions are part of the runtime safety story.

## State and Persistence Behavior
Every major structure maps persistent NTFS metadata: boot sectors, MFT records, resident/nonresident attributes, index buffers, reparse records, EAs, and security descriptors. The helpers expose data but do not persist changes; callers update dirty records or indexes after mutation.

## Dependencies and Integration Points
It depends on Linux endian, block, kernel, string, and type helpers plus NTFS3 `debug.h`. It is included by `ntfs_fs.h` and indirectly by most NTFS3 implementation files.

## Risks
The risk surface is high because offset, alignment, endian, or sentinel mistakes can corrupt metadata or cause out-of-bounds access on untrusted images. Optional 64-bit cluster support changes arithmetic boundaries.

## Test Signals
Use crafted images with resident/nonresident attributes, sparse/compressed streams, reparse points, EAs, large indexes, and NTFS 1.x/3.x metadata. Fuzz record and index buffers and build both endian/cluster-width variants where possible.
