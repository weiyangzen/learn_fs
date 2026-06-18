# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_da_btree.h

## Purpose
`xfs_da_btree.h` defines the in-core contracts for XFS directory/attribute btree operations. It describes directory/attribute geometry, operation arguments, lookup comparison results, btree traversal state, in-core node headers, logging offset helpers, and the exported DA btree API.

## Important APIs, Types, And Functions
`struct xfs_da_geometry` stores all derived sizing and address-space constants for a directory or attribute fork, including block size, node entry count, leaf/free block locations, and maximum extents. `struct xfs_da_args` is the central argument object for directory and xattr operations; it carries the name/value, inode, transaction, owner, hash, fork selector, remote attr fields, operation flags, and lookup comparison result.

`enum xfs_dacmp` defines exact, case-only, and different name comparisons. `struct xfs_da_state_blk`, `struct xfs_da_state_path`, and `struct xfs_da_state` model active and alternate btree paths during lookup, split, and join. `struct xfs_da3_icnode_hdr` is the normalized in-core view of v2/v3 node headers. `XFS_DA_LOGOFF` and `XFS_DA_LOGRANGE` calculate byte ranges for transaction logging.

The header declares the exported split/join/search/mapping functions, buffer accessors, name hash/compare helpers, state allocation helpers, v3 node header conversion/checking helpers, and `xfs_da_state_cache`.

## Control Flow
The header has no runtime control flow beyond macros, but it encodes how DA operations are driven: callers populate `xfs_da_args`, allocate an `xfs_da_state`, use lookup to build a path, then call split/join/fixhash helpers as leaf-level code requests structural changes. Buffer helpers use `whichfork` and mount geometry to map logical DA blocks to buffers.

## State And Persistence
The structures are in-memory only, but many fields directly represent persistent metadata coordinates. `xfs_da_geometry` determines where directory data, leaf, and free spaces live in the file. `xfs_da_args::owner`, `whichfork`, `blkno`, remote attr fields, and hash/index fields are used to find and mutate persistent directory or xattr blocks. Operation flags such as `XFS_DA_OP_RECOVERY` and `XFS_DA_OP_LOGGED` influence logged/recovery behavior in higher layers.

## Dependencies And Integration Points
The header is included by directory, xattr, and btree implementation files. It depends on `xfs_da_format.h` for on-disk DA types and on XFS core types such as `xfs_inode`, `xfs_trans`, `xfs_buf`, and fork constants. Its prototypes integrate DA btree code with directory leaf/block code, attribute leaf/remote code, bmap, transaction logging, and buffer verification.

## Risks
Because this header is the ABI between several XFS subsystems, field semantics must remain synchronized with all call sites. Incorrect geometry can send metadata writes into the wrong logical address range. Mis-set operation flags can turn lookup misses into corruption assertions or skip required logging. The fixed `XFS_DA_NODE_MAXDEPTH` bounds path arrays; tree fanout assumptions must remain valid.

## Test Signals
Build coverage should include CRC and non-CRC filesystems, attr and data forks, ascii-ci directory mode, parent pointer attrs, logged attr operations, and recovery builds. Runtime tests should exercise all exported prototypes through directory and xattr add/remove/replace paths, with assertions enabled to catch bad path indexes and geometry-derived range errors.
