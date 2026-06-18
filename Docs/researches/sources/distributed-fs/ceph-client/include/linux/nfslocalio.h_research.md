# sources/distributed-fs/ceph-client/include/linux/nfslocalio.h

Purpose: Declares NFS localio support that lets an NFS client use local nfsd file access when the server is on the same host and UUID/auth checks permit it.

Important APIs, types, and functions: Exports localio UUID/list/client helpers, registration structures, enable/disable paths, and wrappers linking NFS client state to nfsd file handles and local credentials. Detected source surface: 123 lines; includes `linux/list.h`, `linux/module.h`, `linux/nfs.h`, `linux/sunrpc/clnt.h`, `linux/sunrpc/svcauth.h`, `linux/uuid.h`, `net/net_namespace.h`; macros `__LINUX_NFSLOCALIO_H`; structs `auth_domain`, `file`, `list_head`, `net`, `nfs_client`, `nfs_file_localio`, `nfsd_file`, `nfsd_localio_operations`, `rpc_clnt`; enums none; typedefs none; function-like declarations/helpers `nfs_close_local_fh`, `nfs_localio_disable_client`, `nfs_localio_enable_client`, `nfs_localio_invalidate_clients`, `nfs_to_nfsd_file_put_local`, `nfs_to_nfsd_net_put`, `nfs_uuid_begin`, `nfs_uuid_end`, `nfs_uuid_init`, `nfs_uuid_is_local`, `nfsd_localio_ops_init`.

Control flow: Client/server localio code exchanges or checks a UUID, determines whether a mount is local, opens local nfsd files for read/write shortcuts, and falls back to normal RPC when local access is unavailable.

State and persistence behavior: State includes per-client UUID pointers, registered localio clients, nfsd file references in `struct nfs_file_localio`, and net namespace scoped lookup data.

Dependencies and integration points: Depends on module/list/uuid, SUNRPC client and server auth, NFS base types, net namespaces, and NFS fs/sb integration.

Risks and test signals: Risks are auth bypass, stale nfsd file references, namespace confusion, and fallback inconsistency. Test local and remote mounts, UUID mismatch, permission changes, server restart, and module unload.
