# sources/distributed-fs/ceph-client/fs/autofs/symlink.c

Purpose: provides autofs symlink inode operations for synthetic symlinks created by the daemon inside autofs directories.

Important APIs/types/functions: `autofs_get_link` and exported `autofs_symlink_inode_operations`. The link target is stored in `inode->i_private` by `autofs_dir_symlink()` in `root.c`.

Control flow: VFS symlink resolution calls `.get_link`; RCU lookup without a dentry returns `-ECHILD`; otherwise the code obtains `sbi` and `autofs_info`, updates `last_used` for non-daemon callers, and returns the in-memory link target.

State and persistence: no disk state exists. The symlink string is heap-allocated and stored in inode private data, later freed by `autofs_evict_inode()` from `inode.c`. Access time is represented only by the autofs expiry `last_used` timestamp.

Dependencies and integration: depends on `autofs_i.h`, `autofs_oz_mode()`, and inode private storage populated by `root.c`.

Risks: callers must respect the `-ECHILD` RCU fallback. Lifetime is safe only if inode eviction frees `i_private` after all link users are gone.

Test signals: resolve daemon-created symlinks as daemon and non-daemon tasks; verify expiry timestamp changes only for non-daemon access; test RCU path walk fallback.
