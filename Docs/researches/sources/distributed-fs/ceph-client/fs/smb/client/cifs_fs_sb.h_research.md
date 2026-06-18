<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_fs_sb.h -->
## sources/distributed-fs/ceph-client/fs/smb/client/cifs_fs_sb.h

Purpose: defines CIFS mount flag bits and the CIFS-specific superblock state stored in `struct cifs_sb_info`.

Important APIs and types: mount flags include permission bypass, server inode use, direct I/O, xattr disable, SFU/SFM character remapping, POSIX paths/ACLs, Unix emulation, byte-range lock behavior, ACL handling, uid/gid override, fscache, Minshall-French symlinks, multiuser, strict I/O, backup intent, prefix paths, DFS disable, cache assumptions, and shutdown. `struct cifs_sb_info` holds tcon links, local NLS table, parsed mount context, active count, flags, prune work, RCU cleanup, optional prepath, serverino autodisable state, and root dentry.

Control flow: this header has no executable flow, but mount parsing and runtime code test `mnt_cifs_flags` to select behavior in path conversion, permission checks, caching, DFS, and network operations.

State and persistence: per-superblock state lives for the mount lifetime. Flags are atomic because multiple paths inspect or update mount behavior. `prepath` and `root` are available after mount setup.

Dependencies and integration: integrates with VFS superblock private data, tcon link management, rbtrees, delayed work, RCU, NLS, and `smb3_fs_context`.

Risks: flag exhaustion and bit overlap are high-impact because flags are persisted across many call sites. Atomic flag updates need consistent helper use. Prefix-path and root-dentry availability assumptions can break early mount or reconnect code.

Test signals: mount option matrix for each flag, remount/shutdown transitions, prefix path mounts, serverino autodisable matching, multiuser tlink pruning, DFS-disabled mounts, fscache/strict/direct I/O interactions, and lockdep around tlink tree access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/client/cifs_fs_sb.h -->
