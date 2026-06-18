# sources/distributed-fs/ceph-client/fs/omfs/dir.c

Purpose: implements OMFS directory lookup, create, mkdir, unlink, rmdir, rename, readdir, empty-directory initialization, and on-disk hash-chain validation.

Important APIs and functions: exported operations are `omfs_dir_inops` and `omfs_dir_operations`, plus helpers `omfs_make_empty` and `omfs_is_bad`. Key internals are `omfs_hash`, `omfs_get_bucket`, `omfs_scan_list`, `omfs_find_entry`, `omfs_add_link`, `omfs_delete_entry`, `omfs_dir_is_empty`, `omfs_remove`, `omfs_add_node`, `omfs_lookup`, `omfs_fill_chain`, `omfs_rename`, and `omfs_readdir`.

Control flow: directories are hash tables embedded in the directory inode block starting at `OMFS_DIR_START`, with each bucket storing the first inode block in a sibling chain. Lookup hashes the dentry name, reads the bucket pointer, then follows sibling inodes until a matching name is found. Create and mkdir allocate a new inode, initialize the inode block, prepend it to the target bucket, set the child name/sibling/parent fields, and instantiate the dentry. Unlink/rmdir remove an entry from the hash chain and clear the inode link count. Rename optionally removes an existing destination, deletes the old hash entry first, then adds the old inode under the new name.

State and persistence behavior: directory membership is persisted through bucket head pointers in the parent block and `i_sibling`, `i_parent`, and `i_name` fields in child inode blocks. Dirty parent and child inodes are later checksummed by `omfs_write_inode`. New directories initialize all bucket pointers to `~0`; regular files initialize an empty extent table. `ctx->pos` encodes readdir progress with high bits for bucket number and low 20 bits for chain index.

Dependencies and integration points: uses `omfs_bread`, `omfs_iget`, `omfs_new_inode`, `omfs_make_empty_table`, VFS dentry/inode operations, buffer-head dirtying, and dcache splice helpers. `omfs_is_bad` validates `h_self` and basic block range against superblock limits and is shared with file extent traversal.

Risks: `omfs_dir_is_empty` appears inverted: it returns `*ptr != ~0` after the loop, while callers treat false as empty, so empty-directory handling deserves targeted validation. Name comparisons use `strncmp` for `namelen` without checking that the on-disk name terminates at the same length, so prefix collisions may be possible. Rename is not atomic and can lose the old entry if adding the new link fails after deletion. Error mapping often returns `-ENOMEM` for read failures. Readdir position packing limits per-bucket chain indexes to 20 bits and rejects positions with bits above 32.

Test signals: lookup with case-insensitive hash collisions, create/unlink/rmdir, non-empty directory rejection, rename within and across directories, overwrite rename with `RENAME_NOREPLACE`, names at `OMFS_NAMELEN`, corrupt sibling self-pointers, readdir resume from nonzero cookies, and checksum updates after directory mutation.
