# sources/distributed-fs/ceph-client/net/sunrpc/debugfs.c

Purpose: implements SUNRPC debugfs visibility for RPC clients and transports, plus optional SUNRPC fault-injection controls. It creates `/sys/kernel/debug/sunrpc/rpc_clnt` and `/sys/kernel/debug/sunrpc/rpc_xprt` directories, per-client task listings, per-transport info files, symlinks from clients to transports, and `fail_sunrpc` knobs when configured.

Important APIs/types/functions: exported functions include `rpc_clnt_debugfs_register`, `rpc_clnt_debugfs_unregister`, `rpc_xprt_debugfs_register`, `rpc_xprt_debugfs_unregister`, `sunrpc_debugfs_init`, and `sunrpc_debugfs_exit`; `fail_sunrpc` is exported under `CONFIG_FAIL_SUNRPC`. Key file ops are `tasks_fops` and `xprt_info_fops`, with seq helpers `tasks_start/next/stop/show` and `xprt_info_show`.

Control flow: init creates the top-level directories and initializes fault injection. Client registration creates a directory named by client id, adds a `tasks` file, and creates symlinks to all current transports. Opening `tasks` takes a client ref and seq iteration walks `cl_tasks` under `cl_lock`. Transport registration allocates a monotonically increasing debug id and creates an `info` file. Opening `info` takes a transport ref and prints netid, address, port, state, net namespace inode, and optional source address.

State and persistence behavior: debugfs dentries are runtime-only pointers stored in `rpc_clnt` and `rpc_xprt`. Top-level directory pointers are static globals. Fault injection booleans live in exported `fail_sunrpc`. No persistent state is stored.

Dependencies/integration points: integrates with `clnt.c` client/transport lifecycle, `rpc_clnt_iterate_for_each_xprt`, debugfs, seq_file, xprt refcounting, and `fail.h` fault injection consumers in cache and transport code.

Risks: seq iteration holds `cl_lock` while rendering task rows and prints footer data in `tasks_stop`; long debugfs reads can contend with task list updates. Symlink name buffers are fixed-size and silently fail on overflow. Debugfs creation errors are mostly ignored, so absence of files is not fatal. Fault-injection knobs can deliberately alter cache wait and disconnect behavior and should not be enabled accidentally in production tests.

Test signals: mount debugfs, create RPC clients/transports, verify client directories, task rows, xprt symlinks, transport info, open/release refcounts during client destruction, and cleanup on unregister/exit. With `CONFIG_FAIL_SUNRPC`, toggle `ignore-client-disconnect`, `ignore-server-disconnect`, and `ignore-cache-wait` and confirm corresponding fault-injection paths observe them.
