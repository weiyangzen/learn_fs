<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/root.c -->
## sources/distributed-fs/ceph-client/fs/proc/root.c

Purpose: implements procfs mount/context handling, superblock construction, root directory behavior, mount options, filesystem registration, and boot initialization of the static proc tree.

Important APIs and functions: exports `proc_root_init` and defines global `proc_root`. Key internals include `struct proc_fs_context`, `proc_parse_hidepid_param`, `proc_parse_subset_param`, `proc_parse_pidns_param`, `proc_parse_param`, `proc_apply_options`, `proc_fill_super`, `proc_reconfigure`, `proc_get_tree`, `proc_init_fs_context`, `proc_kill_sb`, `proc_root_getattr`, `proc_root_lookup`, and `proc_root_readdir`.

Control flow: `proc_init_fs_context` creates a mount context bound to the current active PID namespace and its user namespace. Option parsing handles `gid=`, `hidepid=`, `subset=pid`, and optionally `pidns=` from an nsfs file or path. `proc_fill_super` allocates `proc_fs_info`, applies options, sets proc superblock flags and operations, creates the root inode from `proc_root`, and installs persistent `self` and `thread-self` dentries. Root lookup first tries numeric PID lookup, then static proc entries; readdir emits static entries before switching to PID directories at `FIRST_PROCESS_ENTRY`.

State and persistence behavior: each proc superblock owns `proc_fs_info` with pid namespace, hidepid policy, pid gid, and pid-only subset setting. Reconfigure can update hidepid/gid/subset but rejects pid namespace changes. `proc_root` is a static permanent PDE anchoring the global proc tree; each mounted superblock has its own root dentry/inode.

Dependencies and integration points: integrates fs_context, user and PID namespaces, nsfs pidns files, proc inode/super ops, proc self/thread-self setup, proc net/sys/tty initialization, generic proc registration, NFSd/openprom mount points, and VFS anonymous superblocks.

Risks: mount option parsing affects process visibility and namespace semantics. `pidns=` permission rules must match joining pid namespaces and only allow descendant namespaces. Error unwinding in `proc_fill_super` is sparse after allocation failures. Root readdir position split between static and PID entries is ABI-sensitive.

Test signals: mount proc with numeric and string hidepid values, gid, subset=pid, and pidns file/path; reconfigure hidepid/gid/subset and reject pidns reconfigure; root lookup for static names and numeric PIDs; nested PID/user namespace mounts; unmount frees pid namespace and `proc_fs_info` via RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/root.c -->
