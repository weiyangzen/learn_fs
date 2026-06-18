# sources/distributed-fs/ceph-client/tools/perf/trace/beauty/include/uapi/linux/stat.h

## Purpose

`stat.h` defines Linux file type/mode constants and the extended `statx(2)` ABI. Perf trace beauty uses it for stat-like syscall masks, returned attribute masks, file mode bits, and newer direct-I/O or atomic-write query fields.

## Important APIs, Types, and Constants

The header exposes file type and permission bits when appropriate for the include context; `S_IS*` macros; `struct statx_timestamp`; fixed-layout `struct statx` with mask, block size, attributes, ownership, mode, inode, size, blocks, timestamps, device IDs, mount ID, DIO alignment, subvolume, atomic write limits, DIO read alignment, and spare space; `STATX_*` request/result bits including newer subvolume, atomic write, and DIO read alignment; deprecated userspace `STATX_ALL`; and `STATX_ATTR_*` file attribute bits.

## Control Flow and Integration

`statx` callers pass a mask of `STATX_*` bits and path flags from `fcntl.h`. The kernel fills `struct statx` and sets `stx_mask` to report valid fields. Some data may be fabricated or opportunistically filled. Perf decodes the request mask and should keep attribute bits separate from request/result bits.

## State and Persistence Behavior

`statx` is a query interface. It may force remote attribute synchronization when combined with `AT_STATX_FORCE_SYNC`, but the masks do not mutate file metadata. Returned fields describe file and mount state at query time.

## Dependencies and Integration Points

The header includes `linux/types.h` and integrates with VFS, filesystems, network filesystems, direct I/O, statx path flags, fs-verity, DAX, encryption, automounts, and mount-id reporting.

## Risks

Consumers must check `stx_mask`; request bits do not guarantee returned validity. `STATX_ALL` is deprecated and omits newer fields. `STATX_MNT_ID` and `STATX_MNT_ID_UNIQUE` differ. Attribute bits and request bits are separate namespaces. Spare space is reserved for future ABI expansion.

## Test Signals

Decode masks such as `STATX_BASIC_STATS|STATX_BTIME|STATX_DIOALIGN`, newer `STATX_SUBVOL`, `STATX_WRITE_ATOMIC`, and `STATX_DIO_READ_ALIGN`, file mode bits, `STATX_ATTR_*`, and statx path flags in a separate namespace.
