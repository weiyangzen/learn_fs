# sources/distributed-fs/openafs/src/afs/LINUX/osi_nfssrv.c

## Purpose
This file installs Linux NFS server authentication hooks for the OpenAFS NFS translator. It tracks active `nfsd` kernel threads, captures client credentials/address during RPC authentication, maps them to AFS PAG/UID state, and restores original auth operations on shutdown.

## Important APIs, types, and functions
- Module parameter `authtab_addr` supplies the kernel `authtab` address if the weak symbol is unavailable.
- `struct nfs_server_thread` records nfsd pid, active flag, latest client address/auth fields, mapped AFS UID/PAG, and handler result.
- `find_nfs_thread(create)` verifies current is an `nfsd` kernel thread, finds/creates its tracking record, and links it in `nfssrv_list`.
- `svcauth_afs_accept` wraps original `auth_ops.accept`, captures RPC credential/client data, and calls `afs_nfsclient_reqhandler`.
- `osi_linux_nfs_initreq` applies captured NFS translator state to an AFS request.
- `osi_linux_nfssrv_init` clones and registers replacement `auth_ops` for each flavor.
- `osi_linux_nfssrv_shutdown` restores originals and frees tracking state.

## Control flow and behavior
Init locates `authtab` via weak symbol or module parameter, initializes `afs_xnfssrv`, iterates auth flavors, holds each original owner module, allocates a clone of its `auth_ops`, replaces `.owner` with OpenAFS and `.accept` with `svcauth_afs_accept`, unregisters the original flavor, and registers the clone. On each accepted RPC, the wrapper first delegates to the original accept; if successful, it finds the nfsd tracking record under `AFS_GLOCK`, captures IPv4 address, auth flavor, uid/gid/groups, maps anonymous uid -1 to -2, calls `afs_nfsclient_reqhandler`, stores success/error code and AFS uid, and returns `SVC_OK` so later request initialization can enforce access.

`osi_linux_nfs_initreq` checks current nfsd state, returns no-op for inactive threads, and when active sets the request code and marks credentials as `NFSXLATOR_CRED` with the mapped AFS uid.

## State and persistence
Runtime state includes `afs_authtab`, cloned/original auth operation arrays, `nfssrv_list`, `whine_memory`, and `afs_xnfssrv`. Each nfsd thread record persists until shutdown and is updated per RPC. No disk state is written.

## Dependencies and integration points
This code depends on Linux SunRPC `auth_ops`, `svc_auth_register/unregister`, nfsd task identity, OpenAFS locks/allocation/credentials, and `afs_nfsclient_reqhandler`. It is initialized by `osi_module.c` unless `AFS_NONFSTRANS` is defined and has stubs elsewhere for the standalone PAG module.

## Risks
Hooking global SunRPC auth tables is invasive and version-sensitive. If `authtab` is missing, translator hooks are silently skipped after warnings. Thread tracking is keyed by pid and may leak stale nfsd entries until module shutdown. Only IPv4 clients are accepted for mapping; non-IPv4 requests log and leave access denied state. Auth operation clone/restore ordering must be correct to avoid disrupting NFS server auth. Concurrent RPCs on the same nfsd thread update a single record.

## Test signals
Test NFS translator access through multiple auth flavors, missing and supplied `authtab_addr`, IPv4 and non-IPv4 clients, anonymous uid mapping, multiple nfsd threads, module unload restoring original auth ops, and failure paths for allocation and `afs_nfsclient_reqhandler`.
