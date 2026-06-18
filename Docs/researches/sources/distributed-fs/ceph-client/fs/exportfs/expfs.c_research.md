# sources/distributed-fs/ceph-client/fs/exportfs/expfs.c

Purpose: Provides generic helpers for encoding inodes/dentries into file handles and decoding file handles back into connected dentries for NFS export and related users.

Important APIs/types/functions: Exports `exportfs_encode_inode_fh`, `exportfs_encode_fh`, `exportfs_decode_fh_raw`, and `exportfs_decode_fh`. Key internal helpers are `exportfs_get_name`, `find_acceptable_alias`, `dentry_connected`, `clear_disconnected`, `reconnect_one`, `reconnect_path`, `get_name`, `filldir_one`, and `exportfs_encode_ino64_fid`. It consumes filesystem `struct export_operations` methods such as `encode_fh`, `fh_to_dentry`, `fh_to_parent`, `get_parent`, and `get_name`.

Control flow: Encoding checks whether the filesystem can encode the requested handle. If there is no export operation and the caller only wants a non-decodeable FID, `exportfs_encode_ino64_fid` stores inode number plus generation. Connectable non-directory handles include parent inode information. Decoding first asks the filesystem for a dentry via `fh_to_dentry`, optionally rejects non-directories, and returns disconnected dentries directly when no caller acceptance callback is supplied. With subtree checks, directories are reconnected to root through repeated `get_parent`, name lookup, and `lookup_one_unlocked`; non-directories first search acceptable aliases, then decode/reconnect a parent and verify the child name maps back to the same inode.

State and persistence behavior: No on-disk state is mutated. Runtime dentry-cache state is changed by clearing `DCACHE_DISCONNECTED` after reconnection. Dentry and file references are carefully acquired/released while walking aliases, parents, and directory files.

Dependencies and integration points: Depends on VFS dentries, mounts, path lookup, directory iteration, credentials, kstats, and export operation contracts documented by NFS exporting. `get_name` falls back to opening the parent directory and iterating entries until a matching child inode number is found using `vfs_getattr_nosec` to handle 64-bit inode numbers.

Risks: Race handling is central: renames/removes can occur between parent discovery, name discovery, and lookup. Stale/corrupt filesystems must return `-ESTALE` rather than incorrectly reconnecting an inode. Alias scanning must not leak references while dropping inode locks. The fallback `get_name` is O(directory size) and can be expensive for large directories.

Test signals: NFS export subtree-check tests; decoding handles for renamed, removed, disconnected, and alias-heavy dentries; directory-only decode rejection; filesystems with custom `get_name`; 32-bit host with 64-bit inode numbers; fanotify FID-only encoding with too-small `max_len`.
