# sources/distributed-fs/ceph-client/fs/nfs/client.c

## Purpose
This file manages shared NFS clients and mounted NFS server records. It registers NFS protocol subversions, allocates and shares `struct nfs_client` objects, creates RPC clients, initializes v2/v3 server records, probes filesystem information, manages server lists and procfs output, and handles per-net NFS client state.

## Important APIs, types, and functions
Protocol registration APIs are `register_nfs_version()`, `unregister_nfs_version()`, `find_nfs_version()`, `get_nfs_version()`, and `put_nfs_version()`. Client lifecycle APIs include `nfs_alloc_client()`, `nfs_get_client()`, `nfs_init_client()`, `nfs_put_client()`, `nfs_free_client()`, `nfs_mark_client_ready()`, and `nfs_wait_client_init_complete()`.

Server lifecycle and setup APIs include `nfs_alloc_server()`, `nfs_create_server()`, `nfs_clone_server()`, `nfs_free_server()`, `nfs_init_server_rpcclient()`, `nfs_server_set_init_caps()`, `nfs_probe_server()`, `nfs_server_insert_lists()`, and `nfs_server_remove_lists()`. Net/proc hooks include `nfs_clients_init()`, `nfs_clients_exit()`, `nfs_fs_proc_net_init()`, `nfs_fs_proc_net_exit()`, `nfs_fs_proc_init()`, and `nfs_fs_proc_exit()`.

## Control flow
Mount setup calls into `nfs_create_server()`, which allocates a server, initializes a shared client through `nfs_init_server()`, probes fsinfo/pathconf, sets FSID and capability state, inserts the server into client/net lists, and returns a mounted server record. `nfs_get_client()` searches the per-net client list under lock, waits for in-progress client initialization when needed, or allocates and inserts a new client before invoking version-specific init.

RPC setup starts from `nfs_init_timeout_values()` and `nfs_create_rpc_client()`, then `nfs_init_server_rpcclient()` clones the shared client with mount-selected auth. v2/v3 setup starts lockd unless local flock/fcntl options avoid it. Probe logic uses version-specific `set_capabilities`, `fsinfo`, `pathconf`, and optional trunking discovery.

## State and persistence behavior
Persistent kernel runtime state includes per-net client and volume lists, client refcounts and construction state, RPC clients, sysfs/procfs visibility, server flags/sizes/cache timers/capabilities, lockd host state, pNFS wait queues, delegation lists, and fscache/proc output. State is released with RCU for clients and servers.

## Dependencies and integration points
The file integrates with SUNRPC transports and auth, NFS version modules, lockd, fs_context mount parsing, sysfs, procfs, fscache, pNFS, NFS localio, NFSv4 callback IDR state, and net namespaces. It is central glue between mount-time configuration and protocol-specific NFS operations.

## Risks and test signals
Risks include client-sharing mismatches across address/xprtsec/minor version, waiting races during client initialization, refcount/list imbalance, error unwinding after partially initialized lockd/RPC/sysfs state, and procfs iteration over live lists. Tests should cover concurrent mounts to the same and different endpoints, TLS xprtsec matching, failed RPC creation, v2/v3 lockd setup, fsinfo bounds on I/O sizes, clone server cleanup, netns teardown warnings, and procfs server/volume output.
