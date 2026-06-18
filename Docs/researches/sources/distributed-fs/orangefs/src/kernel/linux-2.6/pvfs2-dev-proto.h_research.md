# sources/distributed-fs/orangefs/src/kernel/linux-2.6/pvfs2-dev-proto.h

## Purpose
`pvfs2-dev-proto.h` defines the ABI constants and small serialization helpers shared by the kernel module and the user-space client daemon for `/dev/pvfs2-req` upcalls and downcalls. It is the operation-number registry for the kernel-to-client protocol.

## Important APIs and types
The `PVFS2_VFS_OP_*` constants identify every request type: file I/O, lookup, create, getattr, remove, mkdir, readdir, setattr, symlink, rename, statfs, truncate, readahead flush, mount/unmount, xattrs, parameter control, performance counters, cancellation, fsync, fskey, readdirplus, vector I/O, and feature negotiation. `PVFS2_FEATURE_READAHEAD` advertises readahead support. Name/debug array limits and readdir entry limits define fixed buffer sizes. `roundup4`, `roundup8`, `enc_string`, and `dec_string` provide alignment-aware in-place string encoding. `struct read_write_x` carries offset/length pairs for extended I/O.

## Control flow and integration
The protocol constants are written into `pvfs2_kernel_op_t.upcall.type` by VFS helpers and checked by the daemon and device request code when matching downcalls. `pvfs2-cache.c` uses the constants for debug names, `pvfs2-utils.c` switches on them to derive an fsid from an operation, and proc/sysctl handlers issue `PVFS2_VFS_OP_PARAM` and `PVFS2_VFS_OP_PERF_COUNT`.

## State and persistence behavior
This header carries no runtime state. Its values are persistent ABI: changing IDs, struct alignment assumptions, or maximum sizes requires matching daemon-side changes and compatibility handling.

## Dependencies
It includes `pvfs2.h`, `upcall.h`, `downcall.h`, and `quickhash.h`. Those headers define the bulk request/response payloads and hash-list links used by kernel request tracking.

## Risks and test signals
The string macros do not validate destination capacity or decode length, so callers must provide trusted protocol buffers. The comment requires multiples of 8 for 32/64-bit compatibility; tests should include mixed 32-bit userspace to 64-bit kernel ioctl/downcall paths. ABI tests should verify operation ID parity with the daemon, max readdir count limits, string alignment, and feature negotiation behavior.
