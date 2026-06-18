# sources/distributed-fs/ceph-client/fs/nfsd/localio.c

## Purpose
`localio.c` supports local NFS clients bypassing the network stack by opening NFSD filehandles directly through server-side authorization and filecache APIs. It also defines a hidden LOCALIO RPC version used to register/check whether a client UUID is local.

## Important APIs, types, and functions
The central helper is `nfsd_open_local_fh()`, exposed through `struct nfsd_localio_operations nfsd_localio_ops` installed by `nfsd_localio_ops_init()`. Other operation callbacks include `nfsd_net_try_get`, `nfsd_net_put`, `nfsd_file_put_local`, `nfsd_file_file`, and `nfsd_file_dio_alignment()`. RPC handling includes `localio_proc_null()`, `localio_proc_uuid_is_local()`, `localio_decode_uuidarg()`, `localio_procedures1`, and `localio_version1`.

## Control flow
LOCALIO open validates filehandle size, pins the NFSD net namespace, tries an already cached local `nfsd_file` pointer under RCU, converts an NFS filehandle into `svc_fh`, maps client RPC credentials into `svc_cred`, calls `nfsd_file_acquire_local()`, releases temporary credential state, then atomically installs the resulting file pointer for reuse. If another thread wins installation, the function drops the extra file and net references and returns the already installed object. The UUID RPC decodes a fixed UUID and calls `nfs_uuid_is_local()` to update per-net local client tracking.

## State and persistence
State is runtime-only: cached LOCALIO `nfsd_file` pointers supplied by the NFS client, net namespace references paired with those pointers, and `nfsd_net.local_clients` membership. Cached DIO alignment fields are read from `struct nfsd_file`. Shutdown invalidates local clients from the filecache purge path.

## Dependencies and integration points
It depends on NFSD VFS/filecache/filehandle verification, SUNRPC auth mapping, NFS client LOCALIO hooks (`nfs_to`), `nfslocalio`, per-net NFSD state, and the hidden RPC program/version dispatch table. It bridges client kernel context to server authorization code, which is a stronger integration boundary than normal network RPC.

## Risks and test signals
Risks include net reference leaks or premature drops, stale cached local file pointers, racing `cmpxchg()` installation, missing credential cleanup, bypassing connection-based authorization, invalid filehandle sizes, and local-client invalidation during namespace shutdown. Test signals include concurrent LOCALIO opens of the same filehandle, read/write mode combinations, server shutdown while local files are cached, failed `nfsd_net_try_get()`, credential mapping with supplemental groups, DIO alignment propagation, UUID_IS_LOCAL from multiple clients, and LOCALIO disabled builds.
