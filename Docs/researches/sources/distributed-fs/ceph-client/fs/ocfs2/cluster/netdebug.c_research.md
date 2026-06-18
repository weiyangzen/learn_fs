# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/netdebug.c

## Purpose
`netdebug.c` provides debugfs diagnostics for O2CB TCP networking when `CONFIG_DEBUG_FS` is enabled. It exposes current socket containers, send-tracking entries, per-socket stats, and connected-node bitmap.

## Important APIs, types, and functions
Public hooks are `o2net_debug_add_nst`, `o2net_debug_del_nst`, `o2net_debug_add_sc`, `o2net_debug_del_sc`, `o2net_debugfs_init`, and `o2net_debugfs_exit`. Internal seq-file operations walk `send_tracking` and `sock_containers` lists under `o2net_debug_lock`; files are `send_tracking`, `sock_containers`, `stats`, and `connected_nodes`.

## Control flow
Networking code adds/removes live tracking and socket objects to debug lists. Opening a debugfs seq file allocates a dummy cursor object and inserts it into the same list to iterate safely. Show functions locate the next real object, format task/message timing for sends, socket endpoint and callback timing for sockets, CSV-like stats for tooling, or a simple connected-node bitmap.

## State and persistence behavior
State is runtime-only debugfs state: global lists, dummy per-open cursors, and formatted snapshots. It does not affect network behavior or persist across unload. With `CONFIG_OCFS2_FS_STATS` disabled, stats fields report zero.

## Dependencies and integration points
It depends on debugfs, seq_file, spinlocks with bottom halves disabled, O2NET internal structures from `tcp_internal.h`, nodemanager node names/numbers, socket internals, and optional stats instrumentation.

## Risks and test signals
Risks include list iteration races, dereferencing partially destroyed socket/send objects, holding the debug spinlock while formatting larger records, and tooling depending on the stats string version. Test signals include concurrent connection churn while reading debugfs files, send timeout diagnostics, stats reads with and without `CONFIG_OCFS2_FS_STATS`, connected-node bitmap correctness, and debugfs init/exit cleanup.
