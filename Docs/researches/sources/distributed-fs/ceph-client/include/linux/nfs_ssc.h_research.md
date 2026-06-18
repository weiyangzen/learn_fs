# sources/distributed-fs/ceph-client/include/linux/nfs_ssc.h

Purpose: Declares NFS server-side copy client operation registration used for NFSv4.2 inter-server/server-side copy coordination.

Important APIs, types, and functions: Exports global `nfs_ssc_client_tbl`, `struct nfs4_ssc_client_ops`, `struct nfs_ssc_client_ops`, `struct nfs_ssc_client_ops_tbl`, register/unregister helpers for NFSv4.2 SSC, inline open/close wrappers, `struct nfsd4_ssc_umount_item`, and generic SSC registration APIs. Detected source surface: 81 lines; includes `linux/nfs_fs.h`, `linux/sunrpc/svc.h`; macros none; structs `file`, `list_head`, `nfs4_ssc_client_ops`, `nfs_fh`, `nfs_ssc_client_ops`, `nfs_ssc_client_ops_tbl`, `nfsd4_ssc_umount_item`, `vfsmount`; enums none; typedefs none; function-like declarations/helpers `ERR_PTR`, `nfs42_ssc_close`, `nfs42_ssc_register`, `nfs42_ssc_register_ops`, `nfs42_ssc_unregister`, `nfs42_ssc_unregister_ops`, `nfs_do_sb_deactive`, `nfs_ssc_register`, `nfs_ssc_unregister`.

Control flow: The NFS server copy path registers client ops, opens a source file on a mounted source server, performs copy work, closes it, and defers superblock deactivation through umount list items when needed.

State and persistence behavior: Global ops tables persist while modules are registered. Umount items and opened files persist for copy operation lifetime.

Dependencies and integration points: Depends on NFS client fs headers, SUNRPC server types, vfsmount/superblock state, and NFSv4.2 copy implementation.

Risks and test signals: Risks are ops-table races, leaked mounts/files, and cleanup ordering during module unload. Test copy registration/unregistration, inter-server copy success/failure, and umount while copy state exists.
