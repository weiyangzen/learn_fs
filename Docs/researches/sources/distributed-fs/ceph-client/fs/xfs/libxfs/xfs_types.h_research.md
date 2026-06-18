# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.h

Purpose: Defines fundamental XFS scalar types, null sentinel values, geometry limits, fork identifiers, extent/rmap/refcount records, group/free-counter enums, and verifier prototypes.

Important APIs, types, and functions: Provides typedefs for AG/RTG block and group numbers, inode numbers, extent lengths, filesystem/realtime block numbers, file offsets, log sequence numbers, quota ids, and failure addresses. Defines `NULL*` sentinels, block/sector size limits, fork ids, name length, lookup enum, `struct xfs_name`, bit constants, extent cursor and bmap record types, refcount domains/records, rmap flags/records, AG reservation types, btree record packing enum, group type enum, free counter enum, and verifier declarations.

Control flow: Headers across XFS use these types to maintain unit clarity. String mapping macros feed trace/debug output. Verifier prototypes route metadata checks to `xfs_types.c`.

State and persistence: Many typedefs and structs mirror persistent metadata fields or incore decoded forms of persistent records. Sentinel values are serialized or compared in metadata paths, so width stability matters.

Dependencies and integration points: Foundational include for libxfs, kernel XFS, userspace tools, tracepoints, btree/rmap/refcount/bmap code, scrub, quota, and transaction reservations.

Risks and test signals: Risks include changing type widths, sentinel collisions, trace enum drift, record flag mask mistakes, and misuse of filesystem vs realtime block units. Test kernel/userspace builds, sparse type checks where available, metadata boundary verifiers, trace enum consistency, and big filesystem/rtgroup configurations.
