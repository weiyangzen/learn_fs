# sources/distributed-fs/ceph-client/fs/gfs2/dir.c

## Purpose
Implements GFS2 directory storage and operations, including stuffed linear directories, extendible-hash directories, dirent scanning/validation, lookup, readdir cookies, insert/delete/rename updates, hash-table caching, leaf splitting/doubling, and exhash deallocation.

## Important APIs, Types, And Functions
Public functions include `gfs2_dir_search()`, `gfs2_dir_check()`, `gfs2_dir_add()`, `gfs2_dir_del()`, `gfs2_dir_read()`, `gfs2_dir_mvino()`, `gfs2_dir_exhash_dealloc()`, `gfs2_diradd_alloc_required()`, `gfs2_dir_get_new_buffer()`, and `gfs2_dir_hash_inval()`. Internal helpers handle directory data I/O (`gfs2_dir_write_data()`, `gfs2_dir_read_data()`), hash-table cache (`gfs2_dir_get_hash_table()`), dirent validation/scanning (`gfs2_dirent_scan()` and scan callbacks), leaf access (`get_leaf*()`), conversion (`dir_make_exhash()`), leaf split (`dir_split_leaf()`), hash doubling (`dir_double_exhash()`), new chained leaves (`dir_new_leaf()`), sorted cookie emission (`do_filldir_main()`), and leaf deallocation (`leaf_dealloc()`).

## Control Flow
Small directories are stuffed in the dinode after `struct gfs2_dinode`. When space runs out, `dir_make_exhash()` allocates an initial leaf, copies dirents, and replaces inline data with a hash table of leaf block pointers. Exhash lookups compute an index from the name hash, scan the first leaf and chained leaves, and validate every dirent. Adds first search saved free space from preflight, otherwise convert/split/double/add-chain until space exists. Reads gather dirents, compute stable cookies from hash or local leaf offsets, sort collision runs when needed, and emit through `dir_emit()`. Deletes merge record length into the previous dirent or sentinel the first entry, update leaf and directory entry counts, and adjust nlink for directories. Exhash deallocation walks hash table leaves, locks relevant rgrps, frees metadata, zeroes hash-table pointers, updates dinode, and can change mode to regular file on final dealloc to avoid double free after crash.

## State And Persistence
Persists directory entries, hash table pointers, leaf metadata (`lf_depth`, `lf_entries`, `lf_next`, timestamps, distance), inode `i_entries`, `i_depth`, `GFS2_DIF_EXHASH`, inode size, link counts, timestamps, inode block counts, resource-group metadata, quota/statfs effects, and the in-memory `i_hash_cache`.

## Dependencies And Integration Points
Depends on bmap extent allocation, unstuffing, metadata I/O, glocks, transactions, quotas, rgrps, CRC hashing, sort/vmalloc, and VFS `dir_context`. Used by lookup, create/link/unlink/rename, dentry revalidation, NFS export name lookup, and directory teardown.

## Risks
Dirent record-length validation is corruption-critical. Hash-table cache invalidation must happen whenever pointer tables change. Readdir cookies must be stable across hash collisions and large directories. Conversion, split, and doubling are multi-block metadata transactions where crash consistency depends on journal ordering. Exhash leaf deallocation must avoid freeing the same leaf twice when multiple hash slots point to it.

## Test Signals
Test stuffed lookup/read/add/delete, conversion to exhash, leaf split, hash-table doubling, chained leaves at max depth, hash collisions and seek cookies, `loccookie` on/off, rename `..` updates via `gfs2_dir_mvino()`, corrupt dirent lengths/counts, hash-cache invalidation, and exhash deallocation/recovery.
