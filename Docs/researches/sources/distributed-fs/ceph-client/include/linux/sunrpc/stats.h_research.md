# sources/distributed-fs/ceph-client/include/linux/sunrpc/stats.h

Purpose: declares coarse SUNRPC client and server statistics structures and procfs registration helpers.

Important APIs and types: `struct rpc_stat` records program pointer plus network, UDP/TCP/connect/reconnect, RPC, retransmission, auth-refresh, and garbage counters. `struct svc_stat` records server program pointer plus network/TCP/UDP/connect, RPC, bad format, bad auth, and bad client counters. Procfs-enabled APIs initialize/exit per-net proc entries, register/unregister client/server stats, zero RPC program counters, and show service stats.

Control flow: RPC client/server paths increment counters, procfs registration exposes them under the network namespace, and proc readers render cumulative values. Without `CONFIG_PROC_FS`, all helpers become no-ops.

State and persistence: stats are in-memory cumulative counters for program/service lifetime; no persistent storage.

Dependencies and integration points: integrates with procfs, `seq_file`, RPC program descriptors, service descriptors, and net namespaces.

Risks and test signals: risks include counter drift, procfs-disabled blind spots, unregister ordering, and parsers depending on output format. Test with procfs enabled/disabled, per-net namespace teardown, client/server call counters, and stats reset paths.
