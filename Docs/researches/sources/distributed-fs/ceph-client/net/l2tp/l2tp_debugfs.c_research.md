# sources/distributed-fs/ceph-client/net/l2tp/l2tp_debugfs.c

## Purpose
Exposes L2TP tunnel and session runtime state through debugfs at `l2tp/tunnels`. It is diagnostic-only and renders core and pseudowire state through a seq_file iterator.

## Important APIs, types, and functions
- `rootdir` holds the debugfs directory dentry.
- `struct l2tp_dfs_seq_data` stores the opener's net namespace, namespace tracker, tunnel/session iteration keys, and current referenced objects.
- `l2tp_dfs_seq_start`, `l2tp_dfs_seq_next`, `l2tp_dfs_seq_stop`, and `l2tp_dfs_seq_show` implement seq_file iteration.
- `l2tp_dfs_seq_tunnel_show` prints tunnel IDs, socket addresses, encap type, session count, refcounts, and stats.
- `l2tp_dfs_seq_session_show` prints session IDs, pseudowire type, sequence state, refcount, config, cookies, stats, and invokes `session->show`.

## Control flow
Opening the file allocates iterator state and derives the network namespace from the current PID. Seq iteration alternates between a tunnel row and its session rows by using `l2tp_tunnel_get_next` and `l2tp_session_get_next`, dropping references from the previous element before advancing. The show path emits a header for `SEQ_START_TOKEN`, then tunnel or session detail. Release drops the tracked namespace and iterator memory.

## State and persistence behavior
No L2TP state is modified. The only local state is per-open iterator memory and the global debugfs dentry. References are held only while iterating and are dropped in `stop` or while advancing. Output reflects live in-kernel counters and may change between reads.

## Dependencies and integration points
Depends on debugfs, seq_file, net namespaces, socket address formatting, and the L2TP core lookup APIs. Pseudowires can extend session output through `session->show`; `l2tp_eth.c` uses this to print the interface name when debugfs support is enabled.

## Risks and test signals
Risks are reference leaks in iterator transitions, namespace lifetime handling, and stale pointers while sessions/tunnels are deleted concurrently. Test signals include successful creation/removal of `debugfs/l2tp/tunnels`, correct per-namespace output, stable reads while tunnels/sessions are created or deleted, and presence of pseudowire-specific lines.
