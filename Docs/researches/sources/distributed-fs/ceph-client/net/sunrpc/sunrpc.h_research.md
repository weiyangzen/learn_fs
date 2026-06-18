# sources/distributed-fs/ceph-client/net/sunrpc/sunrpc.h

## Purpose
`sunrpc.h` is an internal SUNRPC header for small shared definitions and cross-file prototypes that are not part of the public UAPI or exported Linux SUNRPC headers.

## Important APIs, Types, And Functions
It defines `struct rpc_buffer`, the inline helper `sock_is_loopback()`, and prototypes for `rpc_clients_notifier_register()`, `rpc_clients_notifier_unregister()`, `auth_domain_cleanup()`, `svc_sock_update_bufs()`, and `svc_authenticate()`.

## Control Flow
The only executable logic is `sock_is_loopback()`, which reads `sk->sk_dst_cache` under RCU and returns true when the cached destination device advertises `NETIF_F_LOOPBACK`. Other declarations are implemented in scheduler, pipefs, authentication, and server socket code.

## State And Persistence
`struct rpc_buffer` describes dynamically allocated RPC call/reply buffers with a stored allocation length followed by flexible data. The header owns no global state.

## Dependencies And Integration Points
The header depends on networking types and is included by core SUNRPC files such as scheduler, module lifecycle, pipefs, server dispatch, and authentication. `struct rpc_buffer` is used by `sched.c` allocation, notifier prototypes tie into client pipefs integration, and auth/server prototypes avoid circular includes.

## Risks And Edge Cases
`sock_is_loopback()` is only as current as the cached route and must remain RCU-safe. `struct rpc_buffer` layout is coupled to `rpc_malloc()`/`rpc_free()` using `container_of()` from the data pointer, so layout changes can break buffer freeing. Adding broad dependencies here can increase coupling across the SUNRPC core.

## Test Signals
Compile coverage across SUNRPC core files is the primary signal. Runtime signals include RPC buffer allocation/free under KASAN and route/loopback detection tests that exercise cached destination changes under RCU.
