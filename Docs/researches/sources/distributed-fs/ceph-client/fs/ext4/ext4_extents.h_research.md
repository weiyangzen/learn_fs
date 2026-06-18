# sources/distributed-fs/ceph-client/fs/ext4/ext4_extents.h

## Purpose
`ext4_extents.h` defines the on-disk extent tree format and small helper API used by ext4 extent mapping, allocation, split, conversion, truncate, fiemap, and test code. It is included by extent implementation code and by the KUnit extent split/conversion tests.

## Important APIs, types, and constants
The on-disk extent tree is described by `struct ext4_extent_header`, `struct ext4_extent`, `struct ext4_extent_idx`, and `struct ext4_extent_tail`. The header stores magic, entry count, max capacity, depth, and generation. Leaf extents store first logical block, encoded length, and the split high/low physical block. Index entries store the logical starting key and physical child block. Non-inode extent blocks carry `struct ext4_extent_tail`, a checksum slot placed after the max extent array.

`struct ext4_ext_path` is the traversal cursor used by lookup, insert, split, and truncate code. Each path element records the current physical block, depth, max depth, selected leaf extent or index, header pointer, and buffer head. `struct partial_cluster` records bigalloc partial clusters during removal with `initial`, `tofree`, and `nofree` state.

Key constants include `EXT4_EXT_MAGIC`, `EXT4_MAX_EXTENT_DEPTH`, `EXT_INIT_MAX_LEN`, and `EXT_UNWRITTEN_MAX_LEN`. The high bit of `ee_len` encodes unwritten status, except the special `0x8000` value which remains an initialized extent of length 32768. Macros such as `EXT_FIRST_EXTENT`, `EXT_LAST_EXTENT`, `EXT_FIRST_INDEX`, `EXT_LAST_INDEX`, `EXT_MAX_EXTENT`, `EXT_MAX_INDEX`, and `EXT_HAS_FREE_INDEX` provide typed pointer arithmetic over extent blocks.

Inline helpers include `ext_inode_hdr()`, `ext_block_hdr()`, `ext_depth()`, `ext4_ext_mark_unwritten()`, `ext4_ext_is_unwritten()`, `ext4_ext_get_actual_len()`, `ext4_ext_mark_initialized()`, `ext4_ext_pblock()`, `ext4_idx_pblock()`, `ext4_ext_store_pblock()`, and `ext4_idx_store_pblock()`.

## Control flow and integration
Extent lookup starts from `ext_inode_hdr(inode)`, descends through `struct ext4_extent_idx` entries, and records the route in `struct ext4_ext_path`. Leaf operations then inspect or update `struct ext4_extent` entries. Split and conversion code relies on the encoded `ee_len` state to distinguish initialized and unwritten extents, and on path capacity helpers to decide whether an insert can happen in-place or requires splitting/growing the tree.

The header declares implementation entry points used elsewhere: `__ext4_ext_dirty()` to journal/dirty an extent path, `ext4_ext_zeroout()` for zeroing unwritten ranges, and KUnit-only hooks `ext4_ext_space_root_idx_test()` and `ext4_split_convert_extents_test()` when `CONFIG_EXT4_KUNIT_TESTS` is enabled.

## State and persistence behavior
All extent tree structures in this header are persistent little-endian metadata. The root extent header lives in `EXT4_I(inode)->i_data`, which corresponds to the on-disk inode `i_block` area for extent-enabled inodes. Child extent/index blocks are normal metadata blocks and may include checksum tails. Physical block numbers are stored as low 32 bits plus high 16 bits; helpers must be used to avoid truncation.

Unwritten state is persisted in `ee_len`, not in a separate flag field. That compact encoding is central to fallocate, delayed allocation, direct IO completion, and conversion paths. Any code that changes extent length must preserve the encoding convention and the maximum length rules.

## Dependencies and integration points
This header depends on `ext4.h` for core types, inode access, block numbers, and JBD2 handle declarations. It integrates with `extents.c`, `inode.c`, `move_extent.c`, fiemap, fast commit replay extent updates, and the KUnit test in `extents-test.c`.

## Risks and review notes
The main risks are off-by-one and endian mistakes in extent pointer arithmetic, length encoding, and physical block split/join helpers. `EXT_LAST_EXTENT()` and similar macros assume `eh_entries` is nonzero; callers must validate tree headers before dereferencing. `ext4_ext_mark_unwritten()` has a `BUG_ON` for zero-length unwritten extents, which is appropriate for an invariant breach but dangerous if reachable from corrupted metadata without prior validation.

Checksum-tail placement relies on `eh_max` and block-size geometry. If a caller corrupts `eh_max`, `find_ext4_extent_tail()` can point at the wrong location. Tree depth is capped by `EXT4_MAX_EXTENT_DEPTH`; validation paths must enforce that before recursion or path allocation.

## Test signals
The KUnit hooks exported under `CONFIG_EXT4_KUNIT_TESTS` are direct test signals. Useful invariants include physical block round trips through store/load helpers, initialized/unwritten length transitions around `0x8000`, root header access through inode private data, checksum-tail offset computation, and extent/index pointer macros over synthetic headers.
