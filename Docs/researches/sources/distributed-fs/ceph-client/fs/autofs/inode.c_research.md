# sources/distributed-fs/ceph-client/fs/autofs/inode.c

Purpose: implements autofs mount-context parsing, superblock construction/destruction, autofs private inode metadata allocation, and generic inode creation for directories and symlinks. It is the entry point that turns fs_context options from the daemon into an initialized autofs superblock.

Important APIs/types/functions: `autofs_new_ino`, `autofs_clean_ino`, `autofs_free_ino`, `autofs_kill_sb`, `autofs_param_specs`, `autofs_parse_fd`, `autofs_parse_param`, `autofs_validate_protocol`, `autofs_fill_super`, `autofs_init_fs_context`, and `autofs_get_inode`. `struct autofs_fs_context` carries mount-time uid/gid/pgrp state while `struct autofs_sb_info` is allocated and attached to `fc->s_fs_info`.

Control flow: fs_context setup allocates option state and a catatonic `sbi`; parameter parsing opens and validates the daemon pipe early, records protocol bounds, mount type, flags, uid/gid, and owner process group; `get_tree_nodev()` calls `autofs_fill_super()`, which initializes simple superblock fields, creates the root inode and dentry, attaches root `autofs_info`, resolves the owner pgrp, marks trigger roots managed, and clears catatonic mode. `autofs_kill_sb()` puts the filesystem back into catatonic mode, drops the daemon pid, kills the anonymous superblock, and frees `sbi` by RCU.

State and persistence: no disk persistence exists; state lives in `sbi`, dentries, inodes, wait queues, and a packet pipe to userspace. `autofs_info` tracks active/expiring list membership, requester uid/gid, expiry timestamps, and child counts. Pipe file references and process-group references are explicitly owned and released.

Dependencies and integration: integrates with the VFS fs_context API, simple/statfs super operations, dentry operations from `root.c`, symlink operations from `symlink.c`, wait queue handling from `waitq.c`, and UAPI autofs protocol versions. It relies on `autofs_check_pipe()` and packet pipe flag helpers declared elsewhere in autofs.

Risks: fd parsing must happen in the syscall context to avoid descriptor reuse races. Error paths around `autofs_fill_super()` can leak or leave partially constructed state if future edits skip dentry/inode ownership rules. Protocol negotiation and pipe validation are security boundaries because they select daemon packet format and kernel/userspace trust.

Test signals: mount autofs with fd/uid/gid/pgrp/minproto/maxproto/type flags; verify `/proc/mounts` option output; exercise missing fd and invalid protocol bounds; unmount while waiters exist to validate catatonic cleanup; run lockdep/KASAN with repeated mount/unmount cycles.
