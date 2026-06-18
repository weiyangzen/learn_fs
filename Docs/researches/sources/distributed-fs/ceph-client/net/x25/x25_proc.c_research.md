# sources/distributed-fs/ceph-client/net/x25/x25_proc.c

Purpose: exposes X.25 diagnostic procfs files for routes, sockets, and forwarding entries.

Important APIs/functions: `x25_proc_init()` creates `/proc/net/x25/{route,socket,forward}` and `x25_proc_exit()` removes them. Seq operations walk `x25_route_list`, `x25_list`, and `x25_forward_list`.

Control flow: when `CONFIG_PROC_FS` is enabled, init creates the directory and three seq files, rolling back the subtree on failure. Route output shows address prefix, significant digits, and device. Socket output shows addresses, device, LCI, state, sequence variables, timers, send/receive memory, and inode. Forward output shows LCI and paired devices.

State and persistence: no state is owned; output is a snapshot under the corresponding read lock. Without procfs, init/exit are stubs.

Dependencies and integration: depends on global lists from route, socket, and forwarding modules, timer display helper, seq_file, procfs, and init_net proc directory.

Risks and test signals: diagnostics must hold the right locks while tolerating missing device/socket pointers. Tests should cover partial init rollback, concurrent route/socket/forward deletion during reads, disabled `CONFIG_PROC_FS`, and formatting for sockets without neighbours or socket inodes.
