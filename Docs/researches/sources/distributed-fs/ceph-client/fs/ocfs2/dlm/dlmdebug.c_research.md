<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.c -->
## sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.c

Purpose: provides diagnostic printing and debugfs views for OCFS2 DLM domains, lock resources, locks, master-list entries (MLEs), purge lists, and DLM state. It also maps `enum dlm_status` values to stable strings for callers.

Important APIs and functions: exported helpers are `dlm_print_one_lock()`, `dlm_errname()`, and the debugfs lifecycle routines declared in `dlmdebug.h`. `dlm_print_one_lock_resource()` and `__dlm_print_one_lock_resource()` dump owner/state, refmap, queue contents, AST/BAST state, and lock cookies. `dump_mle()` and `dlm_print_one_mle()` render MLE type, current/new master, heartbeat attachment, refcount, and node maps. Under `CONFIG_DEBUG_FS`, `dlm_debug_init()` creates per-domain files `dlm_state`, `locking_state`, `mle_state`, and `purge_list`; `dlm_create_debugfs_root()` creates the global `o2dlm` root.

Control flow: print helpers take the relevant spinlocks, stringify lock names, and walk queue/list structures. The debugfs single-page files (`dlm_state`, `mle_state`, `purge_list`) allocate one page at open time, snapshot current state into it, set inode size, and serve it through `simple_read_from_buffer()`. `locking_state` uses seq_file state in `struct debug_lockres` to iterate one tracked lock resource at a time; each `seq_start` advances through `dlm->tracking_list`, takes a reference to the selected lockres, dumps it under `res->spinlock`, and drops the previous reference.

State and persistence behavior: the module does not persist DLM state; it snapshots in-memory structures into temporary pages or seq buffers. `dlm_errnames[]` is static read-only mapping data. Debugfs dentries live for the module/domain lifetime. `debug_lockres` pins a `dlm_ctxt` with `dlm_grab()` and pins the current lockres while a seq file is open, releasing both on close.

Dependencies and integration points: integrates with Linux debugfs, seq_file, simple read helpers, OCFS2 mask logging, DLM lock/resource/MLE structures, and DLM domain tracking lists. `dlmmaster.c` and error paths call `dlm_print_one_mle()` and lock-resource printers to explain invariant failures. `dlmdomain.c` invokes the debugfs init/destroy hooks at module and domain creation/destruction.

Risks: debug code runs while holding spinlocks and must not sleep in those regions. Single-page debugfs snapshots can truncate large domains, so output is useful but not exhaustive under heavy load. `stringify_lockname()` embeds OCFS2 lock-name format knowledge and may misrepresent future formats. The seq iterator only emits one lockres per read iteration via a custom tracking cursor; reference accounting around `dl_res` is critical to avoid use-after-free when resources are purged while debugfs is open.

Test signals: mount with `CONFIG_DEBUG_FS=y`, inspect `/sys/kernel/debug/o2dlm/<domain>/dlm_state`, `locking_state`, `mle_state`, and `purge_list` during idle, active lock traffic, conversion, migration, and recovery. Validate disabled-debugfs builds use stubs. Exercise `dlm_errname()` for valid and out-of-range statuses and check lockdep under concurrent resource purge plus debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ocfs2/dlm/dlmdebug.c -->
