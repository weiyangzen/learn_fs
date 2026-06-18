# sources/distributed-fs/ceph-client/fs/jfs/jfs_types.h

## Purpose
`jfs_types.h` defines basic JFS scalar IDs, endian-aware on-disk extent descriptors, directory component names, and DASD limit accounting helpers. It is intended to be the first JFS include in C files so core types are available consistently.

## Important APIs, types, and functions
The header defines `tid_t`, `lid_t`, `struct timestruc_t`, bit constants, `pxd_t`, `struct pxdlist`, `dxd_t`, `struct component_name`, and `struct dasd`. Inline helpers `PXDlength()`, `PXDaddress()`, `lengthPXD()`, and `addressPXD()` pack and unpack physical extents. DXD macros wrap PXD helpers and size conversion. DASD macros read and write 40-bit-ish limit/used counters split into high-byte and little-endian low-word fields.

## Control flow
This header is purely declarative and inline. Extent creators call `PXDlength()` and `PXDaddress()` or the DXD wrappers when constructing on-disk descriptors; readers call `lengthPXD()` and `addressPXD()` before doing allocation-map, metapage, or log arithmetic. Directory and unicode code use `struct component_name` as the in-kernel UCS name container.

## State and persistence behavior
`pxd_t` stores a 24-bit length and a 40-bit address split across `len_addr` and `addr2`. `dxd_t` persists extended attribute or data extent metadata with flags for inline, index, single extent, file-backed, or corrupt forms. `timestruc_t`, PXD, DXD, and DASD fields are little-endian on disk, so every arithmetic path must convert explicitly.

## Dependencies and integration points
The header depends on Linux integer types and NLS declarations. It is used throughout JFS by superblock, log, transaction, inode map, block map, xtree, xattr, unicode, and metapage code. It also underpins on-disk compatibility with fsck and OS/2-derived layout constraints.

## Risks
The PXD packing is easy to misuse because `len_addr` contains both length and high address bits. Lengths are masked to 24 bits; addresses beyond the supported bit split would truncate. Macros such as `setDASDLIMIT` and `setDASDUSED` are statement blocks without `do { } while (0)`, so callers need normal care in conditional contexts. Any change to `tid_t` or `lid_t` affects transaction table indexing and lock overlay alignment.

## Test signals
Unit-style tests should round-trip PXD and DXD lengths/addresses across boundary values, validate little-endian encodings, check DASD counter macros over 32-bit boundaries, and mount filesystems with EA, ACL, fsck, and log descriptors that exercise each DXD/PXD consumer.
