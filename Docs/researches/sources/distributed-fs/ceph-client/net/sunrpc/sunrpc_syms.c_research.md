# sources/distributed-fs/ceph-client/net/sunrpc/sunrpc_syms.c

## Purpose
`sunrpc_syms.c` owns SUNRPC module and per-network-namespace initialization and teardown. It wires together memory pools, authentication, cache infrastructure, rpc_pipefs, procfs, sysfs/debugfs, client/server socket transports, and namespace-local SUNRPC state.

## Important APIs, Types, And Functions
The file exports `sunrpc_net_id`, defines pernet callbacks `sunrpc_init_net()` and `sunrpc_exit_net()`, registers `sunrpc_net_ops`, and implements module entry/exit through `init_sunrpc()` and `cleanup_sunrpc()`. It calls core subsystem initializers such as `rpc_init_mempool()`, `rpcauth_init_module()`, `cache_initialize()`, `register_pernet_subsys()`, `register_rpc_pipefs()`, `rpc_sysfs_init()`, `svc_init_xprt_sock()`, and `init_socket_xprt()`.

## Control Flow
Module init starts scheduler memory/workqueue infrastructure, initializes RPC auth and cache support, registers pernet state, registers rpc_pipefs, initializes sysfs/debugfs/sysctl when enabled, and finally registers server and client socket transports. Per-net init creates `/proc/net/rpc`, AUTH_UNIX IP and gid caches, rpc_pipefs namespace state, and client/rpcbind locks/lists. Teardown runs in reverse: per-net exit removes pipefs state and auth caches, module exit removes sysfs/client IDs/transport IDs/auth/socket/debugfs/pipefs/mempools/pernet state, checks auth domains, unregisters sysctls, and waits for outstanding RCU callbacks.

## State And Persistence
Global state includes the registered pernet subsystem ID and module-level subsystems. Per-net state is allocated as `struct sunrpc_net` and contains procfs roots, auth caches, rpc_pipefs state, all-client lists, and rpcbind client locking. State persists until the namespace or module exits.

## Dependencies And Integration Points
This file is the integration point for virtually all SUNRPC core subsystems: scheduler, auth, cache, pipefs, sysfs, debugfs, sysctl, procfs, xprtsock, svc socket transports, network namespaces, client tracking, and RCU cleanup. It uses `fs_initcall()` so SUNRPC initializes before NFS users.

## Risks And Edge Cases
Initialization ordering matters because later subsystems depend on earlier memory pools, auth, per-net state, and pipefs registration. Error labels must unwind only initialized components. Per-net teardown warns if clients remain on `all_clients`, and final `auth_domain_cleanup()` only warns because release callbacks may belong to modules already gone. `rcu_barrier()` is required to wait for delayed frees before module exit completes.

## Test Signals
Useful signals include module load/unload, namespace create/destroy, failure injection at each init step, `/proc/net/rpc` and rpc_pipefs availability per namespace, auth cache creation/destruction, transport registration presence, sysfs/debugfs/sysctl cleanup, and RCU/KASAN checks on module removal.
