# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/iatt.h

## Purpose
Defines GlusterFS internal inode-attribute representation and conversions to/from POSIX `struct stat`.

## APIs, Types, and Functions
`ia_type_t` models file type. `ia_prot_t` stores suid/sgid/sticky and owner/group/other rwx bits. `struct iatt` stores valid flags, inode/device/rdev, size, nlink, uid/gid, block size/count, atime/mtime/ctime/btime with nanoseconds, file attributes/mask, GFID, type, and protection. `mdata_iatt` carries mutable time metadata. Validity masks and macros check field presence. Helpers convert device major/minor, mode to type/protection, type/protection to mode, `iatt_to_mdata()`, `iatt_from_stat()`, `iatt_to_stat()`, and `is_same_mode()`.

## Control Flow, State, and Persistence
`iatt` values are passed through FOP callbacks and xdata and may represent persistent filesystem metadata. `iatt_from_stat()` caps `ia_blocks` to size-derived maximum to avoid over-accounting preallocated blocks, then sets valid flags except GFID/INO. Conversion helpers centralize mode and timestamp representation.

## Dependencies and Integration
Depends on `compat.h` timestamp macros, UUID support, sys/stat, and device macros. Used by lookup/stat/create/readdirp callbacks, dict serialization, inode linking, quota, DHT, AFR, and protocol code.

## Risks and Test Signals
Risks include sparse-file block accounting inaccuracies, timestamp precision portability, invalid `ia_flags`, mode/type conversion mistakes, birth-time availability, and device-number conversion differences. Test signals include stat conversion round trips, sparse/preallocated file quota tests, mode-bit tests, nanosecond preservation tests, and GFID validity checks.
