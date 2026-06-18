<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/inode.c -->
## sources/distributed-fs/ceph-client/fs/proc/inode.c

Purpose: implements the generic procfs inode layer: proc inode allocation/free, proc superblock operations, proc dir entry inode instantiation, dynamic entry lifetime protection, file-operation wrappers, symlink support, mount option display, and dcache invalidation for entries whose backing task/sysctl state disappears.

Important APIs and functions: exports `proc_sops`, `proc_init_kmemcache`, `proc_invalidate_siblings_dcache`, `proc_entry_rundown`, `proc_link_inode_operations`, and `proc_get_inode`. Important internals are `proc_alloc_inode`, `proc_free_inode`, `proc_evict_inode`, `use_pde`, `unuse_pde`, `close_pdeo`, `proc_reg_open`, `proc_reg_release`, the `proc_reg_*` read/write/poll/ioctl/mmap/llseek wrappers, and compat/read-iter file-operation tables.

Control flow: proc root initialization calls `proc_init_kmemcache` before proc inodes or `proc_dir_entry` objects are allocated. `proc_get_inode` converts a `proc_dir_entry` into a VFS inode, selecting regular, iterator, compat, directory, symlink, or empty-directory operations from PDE flags and mode. Regular proc file operations dispatch through wrapper functions that either call permanent PDE operations directly or temporarily increment `pde->in_use` to block removal while a callback runs. Open paths register files with custom release hooks in `pde_openers`; removal calls `proc_entry_rundown`, biases `in_use` negative, waits for active callbacks, and force-closes pending openers.

State and persistence behavior: procfs state is in-memory. `struct proc_inode` stores PID, fd, namespace, PDE, sysctl header, sibling-dcache tracking, and operation payloads. `struct proc_dir_entry` lifetime uses `refcnt`, `in_use`, `pde_openers`, `pde_unload_lock`, and optional unload completion. Eviction clears pagecache, releases task PID tracking, and hands sysctl inodes to `proc_sys_evict_inode`. `proc_show_options` reflects per-superblock hidepid, gid, and pid-only subset state.

Dependencies and integration points: integrates VFS inode/superblock/file operation APIs, proc generic registration, pid and sysctl proc backends, seq_file, compat ioctl, mmap area selection, mount option reporting, and dentry alias invalidation. `proc_invalidate_siblings_dcache` is used by sysctl unregister and similar dynamic namespaces to invalidate all aliases across proc superblocks.

Risks: the PDE rundown protocol is concurrency-sensitive: missing `use_pde`/`unuse_pde` pairing can race module removal, and opener tracking must call release exactly once despite concurrent close and remove. Permanent entries bypass protections and must only be used for never-removed callbacks. Dcache invalidation crosses superblocks and must hold active references carefully. Sysctl pointers are nulled on eviction to avoid stale unregister references.

Test signals: open/read/write/poll/ioctl/mmap dynamic proc entries while removing them; forced module removal with an fd held open; compat ioctl builds; proc symlink readlink after entry removal; sysctl unregister dcache invalidation; hidepid/gid/subset mount option display; KASAN/lockdep coverage around `pde_unload_lock`, completions, and proc inode eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/inode.c -->
