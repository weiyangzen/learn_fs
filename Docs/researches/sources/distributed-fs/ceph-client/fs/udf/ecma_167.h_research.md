# sources/distributed-fs/ceph-client/fs/udf/ecma_167.h

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/ecma_167.h` defines packed ECMA-167 revision 3 on-disk descriptors and constants used by UDF. It is the media-layout vocabulary for volume descriptors, partition maps, file entries, file identifiers, allocation descriptors, timestamps, entity identifiers, extended attributes, and integrity metadata. The source was read as a complete 816-line header.

## Important APIs, Types, and Functions

There are no functions. Important types include `charspec`, `timestamp`, `regid`, volume structure descriptors, `extent_ad`, `tag`, primary/anchor/logical volume descriptors, partition maps, unallocated-space and logical-volume integrity descriptors, `lb_addr` and `kernel_lb_addr`, short/long/extended allocation descriptors and in-core variants, `fileSetDesc`, `partitionHeaderDesc`, `fileIdentDesc`, `icbtag`, `indirectEntry`, `terminalEntry`, `fileEntry`, extended attribute records, `unallocSpaceEntry`, `spaceBitmapDesc`, `partitionIntegrityEntry`, `logicalVolHeaderDesc`, `pathComponent`, and `extendedFileEntry`. Constants define tag identifiers, partition/access flags, file characteristics, ICB strategy/file types/flags, permissions, record formats, extended-attribute IDs, and extent type/length masks.

## Control Flow

This header has no runtime flow. UDF parser and writer code casts disk buffers to these packed structures, verifies descriptor tags/CRCs, converts little-endian fields to kernel types, and builds in-core inode/superblock state. Allocation and inode code interpret the high bits of extent lengths using `EXT_TYPE_MASK` and `EXT_LENGTH_MASK`.

## State and Persistence Behavior

Every packed struct is a persistent media structure. Volume descriptors describe filesystem identity, partition mapping, and integrity state. File entries and extended file entries persist inode metadata, allocation descriptors, timestamps, unique IDs, and stream directories. File identifier descriptors persist directory entries. Space bitmap and unallocated-space entries persist free-space state. In-core mirror structs such as `kernel_lb_addr`, `kernel_long_ad`, and `kernel_ext_ad` hold converted values for runtime logic.

## Dependencies and Integration Points

The header depends only on Linux integer/endian types. It is consumed by UDF superblock parsing, partition mapping, block allocation, inode read/write, directory iteration, symlink parsing, Unicode/name conversion, time conversion, and miscellaneous descriptor helper code.

## Risks and Edge Cases

Packed layout and little-endian annotations are ABI-sensitive. Many structures have flexible trailing arrays whose actual length is constrained by descriptor size fields and block size, so callers must validate before accessing. Extent length high bits encode type, not byte count. File entry and extended file entry layouts differ, especially creation time, object size, and stream directory fields. Changing constants can break compatibility with existing UDF media and other operating systems.

## Test Signals

Signals include descriptor parser tests against UDF revisions/images, sparse and allocated extent decoding, FE/EFE inode read/write round trips, directory FID CRC validation, logical volume integrity parsing, special-file extended attributes, timestamp conversion, and fuzzing of packed descriptor length fields.
