# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/gf-dirent.h

## Purpose
Defines GlusterFS directory-entry objects and helpers for readdir/readdirp results, inode linking from directory entries, and distributed offset transformation.

## APIs, Types, and Functions
`gf_dirent_t` stores list links, inode number, offset, name length, d_type, optional `iatt`, per-entry dict, inode pointer, and flexible `d_name`. `gf_dirent_len()` and `gf_dirent_size()` compute allocation size. `inode_dir_or_parentdir()` recognizes `.` and `..`. APIs include `gf_dirent_for_name()`, `gf_dirent_for_name2()`, `entry_copy()`, `gf_dirent_entry_free()`, `gf_dirent_free()`, `gf_link_inode_from_dirent()`, `gf_link_inodes_from_dirent()`, `gf_fill_iatt_for_dirent()`, and offset transforms `gf_itransform()`, `gf_deitransform()`, and `gf_dirent_orig_offset()`.

## Control Flow, State, and Persistence
Directory entries are transient result lists passed through callbacks. Readdirp-style entries may carry stat data and inode references, allowing the inode table to be populated from directory listings. Offset transform helpers encode/decode distributed translator offsets.

## Dependencies and Integration
Depends on `iatt.h`, `inode.h`, `dict_t`, `xlator_t`, and list primitives. It integrates with `GF_FOP_READDIR`, `GF_FOP_READDIRP`, DHT offset handling, md-cache, protocol serialization, and inode cache population.

## Risks and Test Signals
Risks include flexible-array allocation mistakes, leaked dict/inode refs, incorrect `.`/`..` handling, and offset collisions across subvolumes. Test signals include readdir/readdirp round trips, valgrind/leak tests for entry lists, inode-linking checks, and DHT offset encode/decode tests.
