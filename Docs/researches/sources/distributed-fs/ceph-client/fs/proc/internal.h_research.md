<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/internal.h -->
## sources/distributed-fs/ceph-client/fs/proc/internal.h

Purpose: defines the private procfs data model and cross-file contracts shared by proc root, pid entries, sysctl, network proc entries, task memory views, namespace links, and generic proc registration.

Important APIs and types: declares `struct proc_dir_entry`, `struct proc_inode`, `union proc_op`, `struct pde_opener`, `struct proc_maps_locking_ctx`, and `struct proc_maps_private`. Key helpers include `PROC_I`, `PDE`, `proc_pid`, `get_proc_task`, `pde_get`, `is_empty_pde`, `pde_force_lookup`, `proc_splice_unmountable`, `folio_precise_page_mapcount`, and `folio_average_page_mapcount`. It also declares core entry points such as `proc_get_inode`, `proc_entry_rundown`, `proc_lookup_de`, `proc_readdir_de`, `proc_setup_self`, `proc_setup_thread_self`, `proc_sys_init`, `proc_net_init`, and task maps/smaps/pagemap operation tables.

Control flow: the header has no runtime dispatcher, but it establishes how proc modules cooperate. Generic registration fills `proc_dir_entry` fields, inode creation stores the PDE in `proc_inode`, pid and sysctl code recover task/sysctl state through the inline helpers, and task memory files share `proc_maps_private` to pin the inode, task, mm, VMA iterator, locking state, and optional NUMA mempolicy.

State and persistence behavior: all structures are kernel-resident and tied to procfs object lifetimes. PDEs form an rb-tree directory hierarchy, carry callback pointers and callback-private data, and use `refcnt` plus `in_use` for removal safety. `proc_inode` extends VFS inodes with proc-specific task, sysctl, namespace, and sibling-inode metadata. Mapcount helpers snapshot folio mapping state for proc page-monitor outputs.

Dependencies and integration points: includes procfs public API, namespaces, refcounting, scheduler task APIs, memory-management APIs, binfmt/coredump state, and page mapcount configuration. It is the main internal ABI between `inode.c`, `generic.c`, `root.c`, `base.c`, `array.c`, `proc_sysctl.c`, `proc_net.c`, and task MMU/NOMMU files.

Risks: because this is an internal ABI, field invariants are broad: permanent PDEs must not disappear, forced lookup must be used for namespace-sensitive dentries, proc maps locking semantics differ under `CONFIG_PER_VMA_LOCK`, and mapcount helpers have different precision under `CONFIG_PAGE_MAPCOUNT`. Changing structure layout or flag meaning can break many proc subtrees.

Test signals: all relevant config combinations (`CONFIG_PROC_SYSCTL`, `CONFIG_NET`, `CONFIG_TTY`, `CONFIG_PROC_PAGE_MONITOR`, `CONFIG_PAGE_MAPCOUNT`, `CONFIG_PER_VMA_LOCK`, MMU/NOMMU); proc entry create/remove tests; pid/task lookup under exiting tasks; smaps/kpagecount mapcount validation; namespace-sensitive dentry revalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/internal.h -->
