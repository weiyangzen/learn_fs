# sources/distributed-fs/ceph-client/include/linux/sunrpc/clnt.h

Purpose: declares the high-level SUNRPC client object, RPC program/procedure descriptors, client creation arguments, and synchronous/asynchronous call APIs.

Important APIs and types: `struct rpc_clnt` holds refs, IDs, task lists, transport pointers, procedure tables, auth/stats/metrics, retry and shutdown policy bits, transport security, RTT/timeout data, pipefs/sysfs/debugfs state, xprt iterator/work, credentials, and task counts. `struct rpc_program`, `rpc_version`, and `rpc_procinfo` describe program numbers, versions, procedure encode/decode callbacks, sizing, timers, stats indexes, and names. `struct rpc_create_args` configures network, address, protocol, auth, timeout, backchannel, credentials, nconnect, and transport security.

Control flow: callers create or clone a client, bind program/version/auth, submit `rpc_call_sync()` or `rpc_call_async()`, then tasks encode arguments, reserve a transport/request, transmit, decode replies, update stats, and release client/transport references. Multipath helpers add, remove, probe, and switch transports.

State and persistence: client state is in-memory and refcounted; metrics and RPC counters live for the client/mount lifetime but are not persistent. Pipefs/sysfs/debugfs objects mirror runtime state.

Dependencies and integration points: integrates RPC scheduler, transports, auth, stats, RTT timers, pipefs, paths, IPv6, and xprt multipathing. NFS and lock managers are primary consumers.

Risks and test signals: risks include client shutdown races, stale RCU transport pointers, retry policy mismatches, auth/transport security drift, multipath trunking mistakes, and wrong procedure sizing. Test with sync/async calls, soft/hard timeouts, rpcbind autobind, transport switching, nconnect, backchannel, and per-net cleanup.
