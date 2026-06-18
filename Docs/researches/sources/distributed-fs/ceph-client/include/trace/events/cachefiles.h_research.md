# sources/distributed-fs/ceph-client/include/trace/events/cachefiles.h

## Purpose
`cachefiles.h` defines tracepoints for the CacheFiles backend of fscache/netfs. It tracks object references, lookup and directory operations, coherency checks, read/write/truncate preparation, active/failed/inactive marking, VFS/I/O errors, and on-demand cache file protocol operations.

## Important APIs, types, and functions
The header declares enums for object reference reasons, object kill reasons, coherency reasons, truncate reasons, read preparation reasons, and error locations. Events include `cachefiles_ref`, `cachefiles_lookup`, `cachefiles_mkdir`, `cachefiles_tmpfile`, `cachefiles_link`, `cachefiles_unlink`, `cachefiles_rename`, `cachefiles_coherency`, `cachefiles_vol_coherency`, `cachefiles_prep_read`, `cachefiles_read`, `cachefiles_write`, `cachefiles_trunc`, active/failed/inactive marks, VFS/I/O errors, and on-demand open/copen/close/read/cread/fd-write/fd-release.

## Control flow
Object lifecycle paths emit ref and lookup/create/link/unlink/rename events. Coherency paths compare auxiliary data, content state, xattrs, and volume metadata. Read preparation determines whether data exists, holes are present, no backing file exists, or seek failed. I/O paths trace read/write/truncate and error locations. On-demand mode traces requests and replies exchanged with userspace cache handlers.

## State and persistence behavior
The header stores no state. Event records snapshot object/cookie/volume debug ids, usage counts, backing inode numbers, coherency aux values, content/source enums, offsets/lengths, error codes, message ids, object ids, file descriptors, and flags.

## Dependencies and integration points
It depends on CacheFiles internals, fscache object kill reasons, `netfs_sreq_sources`, VFS dentries/inodes, endian helpers for inline aux data, and tracepoint macros. It integrates the cache backend with netfs/fscache diagnostics and the on-demand cachefiles userspace protocol.

## Risks and test signals
Risks include stale enum mappings, dereferencing optional objects/backers, duplicate macro text in the source around some prototypes that would be caught at build time, and leaking cache object ids or inode numbers to trace consumers. Test signals are fscache/cachefiles mount and read/write workloads, coherency mismatch injection, VFS error injection, object withdrawal/culled paths, and on-demand open/read/close flows with matching msg/object ids.
