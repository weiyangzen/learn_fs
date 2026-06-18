# sources/distributed-fs/ceph-client/fs/xfs/scrub/rcbag_btree.h

## Purpose
`rcbag_btree.h` defines the record format, block layout macros, and public helpers for the in-memory refcount bag btree.

## Important APIs, Types, And Functions
Under `CONFIG_XFS_BTREE_IN_MEM`, it defines `RCBAG_MAGIC`, `struct rcbag_key`, `struct rcbag_rec`, `rcbag_ptr_t`, `RCBAG_BLOCK_LEN`, address macros for records, keys, and pointers, sizing helpers, cursor cache lifecycle, memory initialization, cursor creation, lookup/get/update/insert functions. Without in-memory btree support it stubs cache lifecycle only.

## Control Flow
There is no runtime flow in the header. The macros describe how btree blocks are laid out after the long-form CRC header.

## State And Persistence Behavior
The described state is volatile btree-buffer state. Records contain AG start block, block count, and multiplicity refcount.

## Dependencies And Integration Points
It depends on XFS btree block layout constants, `xfbtree`, mount, transaction, cursor, and rmap types. It is shared by `rcbag.c` and `rcbag_btree.c`; address macros are noted as used by userspace too.

## Risks And Edge Cases
Feature guarding is partial: most APIs disappear without `CONFIG_XFS_BTREE_IN_MEM`, so callers must be compiled conditionally. Layout macros must remain synchronized with `rcbag_btree.c` verifier and max record calculations.

## Test Signals
Compile both config paths, validate address macro offsets, and verify record/key sizing fits inside XFS btree unions.
