# sources/distributed-fs/ceph-client/include/linux/nfs.h

Purpose: Defines common NFS client constants and file-handle helpers shared by NFS versions and localio support.

Important APIs, types, and functions: Exports NFS localio program/procedure IDs, `NFS_MAXFHSIZE`, `struct nfs_fh`, `nfs_compare_fh()`, `nfs_copy_fh()`, `enum nfs3_stable_how`, and `nfs_fhandle_hash()`. Detected source surface: 69 lines; includes `linux/crc32.h`, `linux/cred.h`, `linux/string.h`, `linux/sunrpc/auth.h`, `linux/sunrpc/msg_prot.h`, `uapi/linux/nfs.h`; macros `LOCALIOPROC_NULL`, `LOCALIOPROC_UUID_IS_LOCAL`, `NFS_LOCALIO_PROGRAM`, `NFS_MAXFHSIZE`, `_LINUX_NFS_H`; structs `nfs_fh`; enums `nfs3_stable_how`; typedefs none; function-like declarations/helpers `nfs_compare_fh`, `nfs_copy_fh`, `nfs_fhandle_hash`.

Control flow: Code compares/copies opaque file handles and hashes them for display or lookup; write paths use stable-how values to request unstable, data-sync, or file-sync semantics.

State and persistence behavior: File handles are persistent opaque server identifiers carried in inode and RPC state. The header owns no global storage.

Dependencies and integration points: Depends on credentials, SUNRPC auth/protocol, string helpers, crc32, and UAPI NFS constants.

Risks and test signals: Risks are file-handle length overflow, bad equality comparisons, and incorrect stable-write semantics. Test max-sized handles, copy/compare/hash helpers, and NFSv3 write commit paths.
