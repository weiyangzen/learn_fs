# sources/distributed-fs/ceph-client/fs/nfs/callback.c

## Purpose
This file owns the NFSv4 callback service lifecycle and authentication policy. It creates and shares SUNRPC callback services per NFS minor version, binds per-network-namespace callback transports, starts/stops svc threads, wires v4.1+ backchannel transports, and validates callback credentials.

## Important APIs, types, and functions
The exported lifecycle entry points are `nfs_callback_up()` and `nfs_callback_down()`. Authentication support is provided by `check_gss_callback_principal()` and the program-level `nfs_callback_authenticate()`. `nfs_callback_info[]` tracks users and `svc_serv` pointers per minor version under `nfs_callback_mutex`.

Important helpers include `nfs_callback_create_svc()`, `nfs_callback_up_net()`, `nfs_callback_down_net()`, `nfs_callback_start_svc()`, `nfs_callback_bc_serv()`, and the svc-thread function `nfs4_callback_svc()`.

## Control flow
`nfs_callback_up()` serializes with a global mutex, creates the `svc_serv` if needed, increments per-net callback use by binding the service, creates TCP/IPv4 and TCP/IPv6 listeners for NFSv4.0, enables backchannel service for minor versions with `bc_setup`, starts the configured number of svc threads, and increments global users. Error paths unwind per-net users, threads, and the service if no users remain.

`nfs_callback_down()` decrements per-net users, destroys transports for that net when the last user leaves, decrements global users, and destroys the service/backchannel binding when the minor-version user count reaches zero.

## State and persistence behavior
State is runtime-only: global per-minor callback service refs, per-net `cb_users[]`, callback TCP ports, and backchannel `bc_serv`. No durable state is written. Service lifetime is tied to mounted NFS clients and their transports.

## Dependencies and integration points
The file depends on SUNRPC svc and socket layers, backchannel transport support, netns storage, GSS auth helpers, module parameters declared elsewhere, and callback XDR service versions from `callback_xdr.c`. It integrates with NFSv4 client setup/teardown and with session backchannel creation.

## Risks and test signals
Risks include reference-count imbalance across minor versions/net namespaces, IPv6 listener partial failure handling, unsupported backchannel transports, GSS principal mismatch, and callback thread count changes. Test signals include v4.0 callback listener port publication, v4.1 session backchannel setup, mount/unmount reference churn across netns, AUTH_NULL only for `CB_NULL`, and GSS callback acceptance/rejection.
