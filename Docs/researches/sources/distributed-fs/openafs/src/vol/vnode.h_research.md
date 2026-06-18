# sources/distributed-fs/openafs/src/vol/vnode.h

## Purpose

`vnode.h` defines OpenAFS vnode on-disk and in-memory structures, vnode number/class conversion helpers, size constants, state flags, and public vnode package APIs. It is the main structural contract for volume metadata records.

## Important Types, Macros, and APIs

`ViceLock` stores advisory lock counters/timestamps with inline helpers to check and clear it. Vnode types are `vNull`, `vFile`, `vDirectory`, and `vSymlink`; vnode classes are `vLarge` for directories and `vSmall` for files/symlinks. Inline conversions map types and vnode ids to class, bitmap bit number, index offset, and vnode number.

`VnodeDiskObject` is the persisted vnode record. It stores type, cloned flag, mode bits, link count, 64-bit length split into low/high fields, uniquifier, data version, inode number split into low/high fields, user/server modify times, author/owner/group, parent vnode, magic number, and advisory lock. Small disk vnodes are 64 bytes; large disk vnodes are 256 bytes and use the extra space for directory ACL data via `VVnodeDiskACL`.

Under `AFS_DEMAND_ATTACH_FS`, `VnState` describes vnode cache state and `enum VnFlags` tracks hash/LRU/per-volume-list membership. `struct Vnode` is the in-memory cache object containing queue/hash/LRU links, changed/delete bits, id, volume pointer, refcount, cacheCheck, DAFS state or non-DAFS lock, writer owner, class pointer, inode handle, and disk object.

The header declares core operations implemented in `vnode.c`: init, get, put, allocate, write-to-read conversion, free-vnode retrieval, lookup, and list/hash manipulation.

## State and Persistence Behavior

The disk object layout is persistent and size-sensitive. Macros `VN_GET_LEN`, `VN_SET_LEN`, `VN_GET_INO`, and related disk variants preserve 64-bit fields on platforms that support 64-bit inode operations while keeping the old layout. `vnodeIndexOffset` accounts for an index header record at the start of each vnode index file.

## Dependencies and Integration Points

The header is used by file server, salvager, volume utilities, directory scanning, vol-info tools, and vnode cache implementation. It assumes OpenAFS core typedefs, lock definitions, ACL structures, and volume forward declarations.

## Risks and Test Signals

Any layout change risks on-disk compatibility. Tests should assert `CHECKSIZE_SMALLVNODE`, `SIZEOF_LARGEDISKVNODE`, vnode id/class round trips, ACL pointer placement, 64-bit inode/length macros, and DAFS state validity. API tests should verify callers obey lock ownership and do not access disk fields after a vnode has been put and possibly recycled.
