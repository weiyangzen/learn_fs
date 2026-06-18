# sources/distributed-fs/ceph-client/include/linux/fsnotify.h

Purpose: provides inline VFS notification hooks for filesystem events, consolidating fanotify/inotify/dnotify/audit call sites across file, dentry, inode, mount, and namespace operations.

Important APIs and functions: `fsnotify_sb_has_priority_watchers()` and `fsnotify_sb_has_watchers()` fast-path event suppression by checking superblock watcher counts. Core wrappers include `fsnotify_name()`, `fsnotify_dirent()`, `fsnotify_inode()`, `fsnotify_parent()`, `fsnotify_dentry()`, `fsnotify_path()`, and `fsnotify_file()`. Permission hooks under `CONFIG_FANOTIFY_ACCESS_PERMISSIONS` include `fsnotify_open_perm_and_set_mode()`, `fsnotify_file_area_perm()`, `fsnotify_mmap_perm()`, `fsnotify_truncate_perm()`, and `fsnotify_file_perm()`. Event-specific helpers cover link count, rename/move, inode/mount/mntns delete, inode removal, create, link, delete, `d_delete_notify()`, unlink, mkdir, rmdir, access, modify, open, close, xattr, attribute changes, and mount attach/detach/move.

Control flow: VFS and filesystem code call event helpers after successful operations or before permission-sensitive reads/writes/mmap/truncate. The helpers skip work when no watchers exist, add `FS_ISDIR` where needed, route events to parent/name or child/inode as appropriate, generate rename cookies for paired move events, and call audit hooks for creates. Permission hooks may invoke pre-content/HSM notifications and must run without superblock write freeze protection held.

State and persistence: fsnotify marks and watcher counts live in fsnotify backend state attached to inodes, mounts, and superblocks. This header emits transient events; it does not persist data. Event masks and cookies become observable userspace notification ABI.

Dependencies and integration points: depends on `fsnotify_backend.h`, audit, slab/bug helpers, VFS files/dentries/paths, fanotify HSM/pre-content support, superblock `SB_I_ALLOW_HSM`, and file mode bits such as `FMODE_NONOTIFY` and `FMODE_PATH`.

Risks and test signals: risks include missing events for VFS operations, duplicate events, unstable dentry names, notifying fanotify-generated fds, permission hook deadlocks with freeze protection, rename cookie mismatches, and HSM pre-content policy bypass. Tests should cover inotify/fanotify for create/delete/link/rename/open/close/modify/access/xattr/attrib, permission denial, pre-content range events, mount namespace events, no-watcher fast paths, negative/disconnected dentries, and audit child records.
