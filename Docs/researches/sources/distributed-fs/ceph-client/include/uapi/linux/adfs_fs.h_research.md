<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adfs_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/adfs_fs.h

## Purpose
Defines the Acorn Disc Filing System disk record layout and constants needed to identify and parse an ADFS volume descriptor.

## Important APIs, Types, And Functions
`struct adfs_discrecord` is a packed, 4-byte-aligned 60-byte disk record containing geometry, root location, disk size/id/name/type, share size, zone count, format version, and root size. Constants define the on-disk record address and size.

## Control Flow
ADFS code reads the disk record at `ADFS_DISCRECORD`/`ADFS_DR_OFFSET`, interprets little-endian fields, derives filesystem geometry and root metadata, then mounts or reports the volume.

## State And Persistence
All state is persistent on disk. The structure mirrors the disk format and must not gain padding beyond the declared packed layout.

## Dependencies And Integration Points
Depends on Linux fixed-width types and magic definitions. Integrates with the ADFS filesystem driver, mount tooling, and disk image parsers.

## Risks And Edge Cases
Bitfields, little-endian values, high disk-size fields, and fixed 60-byte layout can break cross-compiler or cross-endian parsing. Corrupt disk records can produce invalid geometry.

## Test Signals
Mount/read tests against known ADFS images, structure size checks, endian decoding tests, and malformed geometry rejection are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/adfs_fs.h -->
