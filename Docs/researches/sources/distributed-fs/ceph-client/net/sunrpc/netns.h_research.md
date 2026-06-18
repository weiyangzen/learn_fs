# sources/distributed-fs/ceph-client/net/sunrpc/netns.h

Purpose: defines SUNRPC per-network-namespace state shared across client, server, rpc_pipefs, auth cache, rpcbind, and GSS proxy code. It centralizes the `struct sunrpc_net` layout stored under `sunrpc_net_id`.

Important APIs/types/functions: `struct sunrpc_net` contains procfs root `proc_net_rpc`, cache pointers (`ip_map_cache`, `unix_gid_cache`, `rsc_cache`, `rsi_cache`), pipefs state (`pipefs_sb`, `gssd_dummy`, `pipefs_sb_lock`, `pipe_users`, `pipe_version`), client registry (`all_clients`, `rpc_client_lock`), local rpcbind clients and locks, GSS proxy state (`gssp_lock`, `gssp_clnt`, `use_gss_proxy`, `use_gssp_proc`, `gss_krb5_enctypes`), and exported `sunrpc_net_id`. It declares `ip_map_cache_create()` and `ip_map_cache_destroy()`.

Control flow: code obtains the namespace state with `net_generic(net, sunrpc_net_id)`. `clnt.c` registers clients in `all_clients` and uses pipefs state; `svcauth_gss.c` creates/destroys `rsc_cache`, `rsi_cache`, and proc entries; cache registration uses `proc_net_rpc`; rpcbind and gssproxy code use the local client fields and locks.

State and persistence behavior: all fields are per-net runtime state. Namespace initialization and teardown create and destroy caches, proc entries, pipefs references, and clients. No persistent storage is represented here.

Dependencies/integration points: depends on network namespace generic storage and forward-declared `struct cache_detail`. It is a coordination header for SUNRPC modules across `net/sunrpc`, especially cache, client, rpc_pipefs, rpcbind, and auth_gss.

Risks: field lifetime is tied to network namespace teardown; users must clear pointers before destroying referenced objects and hold the appropriate lock for client, rpcbind, pipefs, or gssproxy fields. Because many subsystems share this struct, layout changes can have wide build and lifetime impacts.

Test signals: create and destroy network namespaces while running RPC clients, rpcbind lookups, GSS server auth, and pipefs mounts. Verify all per-net caches and proc entries appear and disappear, and run with KASAN/lockdep to catch stale namespace pointers.
