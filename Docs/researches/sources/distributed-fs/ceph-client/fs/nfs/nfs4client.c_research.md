# sources/distributed-fs/ceph-client/fs/nfs/nfs4client.c

## Purpose

`nfs4client.c` manages NFSv4 client and server objects: allocation, initialization, callback setup, session setup/shutdown, trunking discovery, pNFS data-server clients, referral server creation, mount server creation, size negotiation, and transport migration.

## Important APIs, Types, and Functions

Important public functions include `nfs4_alloc_client`, `nfs4_init_client`, `nfs41_init_client`, `nfs41_shutdown_client`, `nfs4_free_client`, `nfs4_match_client`, `nfs4_detect_session_trunking`, `nfs41_walk_client_list`, `nfs4_find_client_ident`, `nfs4_find_client_sessionid`, `nfs4_set_ds_client`, `nfs4_find_or_create_ds_client`, `nfs4_session_limit_rwsize`, `nfs4_session_limit_xasize`, `nfs4_create_server`, `nfs4_create_referral_server`, and `nfs4_update_server`.

## Control Flow

`nfs4_alloc_client` starts with generic allocation, validates minor version bounds, initializes locks/lists/workqueues/client state, creates an RPC client, derives a callback IP address if needed, creates idmapping state, and marks the idmap resource bit. `nfs4_init_client` runs minor-version initialization, starts callbacks, performs server trunking discovery, and may replace a new client with an existing trunk-compatible one.

Mount server creation flows through `nfs4_create_server` -> `nfs4_init_server` -> `nfs4_set_client` -> `nfs_init_server_rpcclient` -> `nfs4_server_common_setup`. Common setup initializes sessions, gets the root filehandle, probes server capabilities, limits negotiated read/write/xattr sizes, inserts the server into global lists, and installs a destroy callback.

## State and Persistence Behavior

This file creates and tears down long-lived in-memory `nfs_client` and `nfs_server` state. It maintains callback IDs, session pointers, pNFS data-server RPC clients, pending callback copy state, idmap resources, sysfs links, delegation hash tables, owner/trunking identity fields, and mount-time metadata. It also updates capability-derived I/O sizes and xattr size limits based on session channel attributes.

## Dependencies and Integration Points

Dependencies include SUNRPC transports/auth/backchannel, rpc_pipefs, NFS callback service, NFS idmapping, pNFS, NFS sysfs, TLS/RDMA transport options, and generic NFS client/server allocation helpers. `nfs4super.c` and `nfs4proc.c` call these functions through NFS operation tables; pNFS layout drivers use the data-server helpers.

## Risks and Edge Cases

Client matching/trunking is subtle: code waits for initializing clients before trusting IDs, compares client IDs, owner IDs, server owner IDs, and server scope, and must avoid loops when a server would attach to itself. Transport migration requires a quiescent server and reinserts the old list state on failure. Xattr/read/write size limiting depends on correct XDR overhead constants.

## Test Signals

Tests should cover v4.0 and v4.1/v4.2 mounts, callback lookup by cb_ident/sessionid, session trunking with multiple addresses, referrals, migration, pNFS data-server access with matching MDS auth flavors, TCP/TCP-TLS/RDMA selection, nconnect behavior, negotiated xattr size caps, and failed client initialization cleanup.
