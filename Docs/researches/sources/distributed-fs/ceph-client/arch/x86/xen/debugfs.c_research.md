# sources/distributed-fs/ceph-client/arch/x86/xen/debugfs.c

Purpose: Creates and caches the top-level Xen debugfs directory for Xen-specific diagnostics and tuning files.

Important APIs/types/functions: `xen_init_debugfs()` returns a `struct dentry *` for `/sys/kernel/debug/xen`, creating it on first use and reusing `d_xen_debug` afterward.

Control flow and state: The only persistent state is the static `d_xen_debug` dentry pointer. Callers can safely request the Xen debugfs root during init and attach their own subdirectories/files.

Dependencies and integration points: It depends on `CONFIG_XEN_DEBUG_FS`, Linux debugfs, and `xen-ops.h`. `p2m.c` uses this root for an MMU/p2m debug file.

Risks and test signals: The file is small, but null or duplicate dentry handling affects all Xen debugfs consumers. Signals include debugfs-mounted Xen guests showing a single `xen` root and p2m debug entries appearing under it when enabled.
