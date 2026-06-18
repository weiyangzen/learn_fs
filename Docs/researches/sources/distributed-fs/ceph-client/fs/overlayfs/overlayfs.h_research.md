# sources/distributed-fs/ceph-client/fs/overlayfs/overlayfs.h

## Purpose
`overlayfs.h` is the central internal interface for OverlayFS. It defines feature enums, on-disk xattr/file-handle formats, wrapper helpers around VFS operations, mount option constants, inode/dentry flag helpers, and prototypes shared across lookup, readdir, copy-up, inode, dir, file, export, superblock, and xattr code.

## Important APIs, types, and functions
Key enums include `ovl_path_type`, `ovl_xattr`, `ovl_inode_flag`, `ovl_entry_flag`, redirect modes, UUID modes, xino modes, verity modes, and fsync modes. Persistent formats are `struct ovl_fb`, `struct ovl_fh`, and `struct ovl_metacopy`. The header declares the global `ovl_fs_type`, `ovl_xattr_table`, and many internal entry points including `ovl_lookup()`, `ovl_dir_operations`, `ovl_fill_super()`, `ovl_xattr_handlers()`, copy-up helpers, fileattr helpers, index helpers, export operations, and inode allocation/lookup helpers.

Inline wrappers such as `ovl_do_create()`, `ovl_do_unlink()`, `ovl_do_rename()`, `ovl_do_setxattr()`, `ovl_do_tmpfile()`, `ovl_lookup_upper_unlocked()`, and `ovl_start_creating_upper()` ensure upper-layer operations consistently use `ovl_upper_mnt_idmap(ofs)` and emit debug traces. Convenience helpers expose feature policy, including `ovl_redirect_follow()`, `ovl_redirect_dir()`, `ovl_origin_uuid()`, `ovl_has_fsid()`, `ovl_should_sync()`, `ovl_should_sync_metadata()`, `ovl_is_volatile()`, `ovl_allow_offline_changes()`, `ovl_same_fs()`, `ovl_same_dev()`, and `ovl_xino_bits()`.

## Control flow
This header does not own a standalone algorithm; it standardizes cross-file control flow. Upper mutations go through `ovl_do_*` wrappers; xattrs go through `ovl_xattr(ofs, enum)` to select `trusted.overlay.*` versus `user.overlay.*`; lookup and readdir code use `ovl_path_type()` and path accessor prototypes; copy-up uses `ovl_copy_up_start()`/`ovl_copy_up_end()` and `ovl_open_flags_need_copy_up()`.

## State and persistence
The file documents and encodes the persistent xattr namespace and file-handle layouts. `struct ovl_fb` stores a magic/versioned exported file handle plus filesystem UUID and endian/path flags; `struct ovl_fh` aligns that payload; `struct ovl_metacopy` stores optional fs-verity digest metadata. In-memory state is represented by inode and entry flags plus `struct ovl_inode_params`, which transfers lookup/copy-up results into inode construction.

## Dependencies and integration points
It includes kernel VFS, UUID, fs-verity, namei, and ACL headers, then includes `ovl_entry.h` for core OverlayFS state objects. Almost every OverlayFS implementation file includes this header, so changes here have a broad ABI-like effect inside the filesystem.

## Risks
Risks include changing packed persistent formats, misusing idmapped upper helpers, adding xattrs without updating `ovl_xattr_table`, and weakening feature policy helpers in ways that break export, redirect, metacopy, or volatile semantics. Since many helpers are inline, subtle semantic changes propagate widely.

## Test signals
Compile coverage with all relevant config combinations is important: POSIX ACL on/off, Unicode/casefold on/off, fs-verity on/off, NFS export, userxattr, metacopy, xino, and redirect modes. Runtime tests should exercise idmapped upper operations, xattr namespace selection, file-handle validation, volatile sync behavior, and copy-up decisions for write/truncate opens.
