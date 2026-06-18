# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-metadata-disk.h

## Purpose

This header defines the on-disk wire/storage layout for the POSIX translator's `trusted.glusterfs.mdata` timestamp xattr.

## Important APIs, Types, and Functions

`gf_timespec_disk_t` stores `tv_sec` and `tv_nsec` as `uint64_t`. `posix_mdata_disk_t` is packed and contains a `uint8_t version`, `uint64_t flags`, and disk-format ctime, mtime, and atime fields. Comments state the version must be bumped when adding members.

## Control Flow

There is no control flow. Conversion functions in `posix-metadata.c` serialize and deserialize this structure with big-endian conversions.

## State and Persistence Behavior

This is a persistent format. It is stored as the value of `GF_XATTR_MDATA_KEY` on backend files and must remain machine-independent. Packing avoids compiler padding in the xattr payload.

## Dependencies and Integration Points

It depends on fixed-width integer types through the includer environment. It is included by `posix-metadata.h` and used by metadata fetch/store and legacy lookup healing code.

## Risks

Changing field order, size, signedness, packing, or endian handling can corrupt or misread existing metadata xattrs. The `uint64_t` representation of time should be reviewed for platforms where `time_t` semantics differ.

## Test Signals

Round-trip mdata xattrs across little-endian and big-endian assumptions, verify packed size, verify version handling, and test upgrades from files without mdata xattrs.
