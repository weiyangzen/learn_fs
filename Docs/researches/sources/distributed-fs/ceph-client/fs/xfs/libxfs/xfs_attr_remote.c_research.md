# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.c

## Purpose
`xfs_attr_remote.c` implements out-of-line storage for extended attribute values that do not fit inside an attr leaf block. Remote values live in data blocks mapped by the inode attribute fork. The file handles remote block sizing, v5 remote headers and CRC verification, synchronous value writes, value reads, buffer invalidation, extent allocation, and extent removal.

## Important APIs, types, and functions
Public functions include `xfs_attr3_rmt_buf_space`, `xfs_attr3_rmt_blocks`, `xfs_attr_rmtval_get`, `xfs_attr_rmt_find_hole`, `xfs_attr_rmtval_set_value`, `xfs_attr_rmtval_stale`, `xfs_attr_rmtval_find_space`, `xfs_attr_rmtval_set_blk`, `xfs_attr_rmtval_invalidate`, and `xfs_attr_rmtval_remove`. The buffer verifier is `xfs_attr3_rmt_buf_ops`.

Internal verification and copy helpers include `xfs_attr3_rmt_hdr_ok`, `xfs_attr3_rmt_verify`, `__xfs_attr3_rmt_read_verify`, read/write verifier wrappers, `xfs_attr3_rmt_verify_struct`, `xfs_attr3_rmt_hdr_set`, `xfs_attr_rmtval_copyout`, and `xfs_attr_rmtval_copyin`. The file uses a one-entry extent map batch size (`ATTR_RMTVALUE_MAPSIZE`) for remote reads.

## Control flow
For reads, `xfs_attr_rmtval_get` walks attr-fork mappings from `args->rmtblkno` for `args->rmtblkcnt`, reads each mapped buffer with remote verifier ops, translates disk ENODATA to EIO, copies value bytes out, and advances logical block, remaining block count, offset, and destination pointer.

For writes, delayed attr code first calls `xfs_attr_rmtval_find_space`, which finds an unused attr-fork hole and stores logical start/count in both args and intent. Repeated `xfs_attr_rmtval_set_blk` calls allocate mapped extents with `xfs_bmapi_write` and advance the intent cursor. After all extents are allocated, `xfs_attr_rmtval_set_value` maps the extents back, obtains buffers, fills headers and payload with `xfs_attr_rmtval_copyin`, and writes each buffer synchronously with `xfs_bwrite`.

For removal, `xfs_attr_rmtval_invalidate` walks mapped remote extents and marks incore buffers stale. `xfs_attr_rmtval_remove` calls `xfs_bunmapi` to unmap remote blocks, returning `-EAGAIN` until the bmap layer reports completion.

## State and persistence behavior
Remote attribute values are intentionally not logged. On CRC-enabled filesystems each remote fsblock carries an `xfs_attr3_rmt_hdr` with magic, offset, byte count, uuid, owner, disk block number, and `NULLCOMMITLSN`. The write verifier rejects any non-`NULLCOMMITLSN` value because log recovery must not treat remote buffers as normal logged metadata after block reuse. Values are written synchronously before the corresponding leaf entry is made complete, providing crash safety in combination with `XFS_ATTR_INCOMPLETE`.

The block count calculation differs between CRC and non-CRC filesystems because each CRC block loses header space. For max-sized xattrs, this can require more than 64 KiB of buffer space across multiple fsblocks, which is why remote buffers must never acquire log items.

## Dependencies and integration points
This file depends on bmap read/write/unmap functions, XFS buffer cache, attr geometry, CRC/magic verification, inode locks, attr fork health marking, delayed attr state in `struct xfs_attr_intent`, and leaf-state code that stores `rmtblkno`, `rmtblkcnt`, and `rmtvaluelen` in leaf entries. It integrates with `xfs_attr.c` remote state transitions and with `xfs_attr_leaf.c` clear/set/flip incomplete flag routines.

## Risks and edge cases
The most important invariant is that remote buffers do not enter the logging system. Header mismatch on owner, byte offset, byte count, uuid, or block number indicates corruption and marks the attr fork sick. Sizing must account for per-block headers on CRC filesystems. Sparse, delayed, or hole mappings in remote value extents are corruption. `xfs_attr_rmtval_remove` intentionally uses `-EAGAIN` as progress, so callers must roll transactions and retry. ENODATA from disk I/O must not be confused with ENOATTR semantics. Buffer invalidation uses trylock flags and must be safe if buffers are absent.

## Test signals
Tests should cover remote values at local/remote boundary, max xattr size, CRC and non-CRC remote block layout, multi-block values on 4 KiB and 64 KiB filesystems, header corruption detection, stale buffer invalidation before unmap, bmap holes/corruption rejection, transaction-rolled removal returning `-EAGAIN`, synchronous write error propagation, and crash recovery before and after leaf incomplete flag clearing.
