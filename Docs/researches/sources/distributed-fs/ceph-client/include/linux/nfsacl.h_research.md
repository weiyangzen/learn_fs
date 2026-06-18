# sources/distributed-fs/ceph-client/include/linux/nfsacl.h

Purpose: Declares NFS ACL buffer sizing and XDR encode/decode helpers for POSIX ACL transport.

Important APIs, types, and functions: Exports ACL entry/page sizing constants, `nfsacl_size()`, `nfsacl_encode()`, `nfsacl_decode()`, and ACL validity helpers. Detected source surface: 48 lines; includes `linux/posix_acl.h`, `linux/sunrpc/xdr.h`, `uapi/linux/nfsacl.h`; macros `NFSACL_MAXPAGES`, `NFSACL_MAXWORDS`, `NFS_ACL_INLINE_BUFSIZE`, `NFS_ACL_MAX_ENTRIES`, `NFS_ACL_MAX_ENTRIES_INLINE`, `__LINUX_NFSACL_H`; structs `posix_acl`; enums none; typedefs none; function-like declarations/helpers `nfs_stream_decode_acl`, `nfs_stream_encode_acl`, `nfsacl_decode`, `nfsacl_encode`, `nfsacl_size`.

Control flow: NFS ACL RPC paths size buffers, encode POSIX ACL entries into XDR words, decode replies back to kernel ACLs, and validate ACL masks.

State and persistence behavior: No global state is owned; ACL objects and pages are caller-owned transient RPC data.

Dependencies and integration points: Depends on POSIX ACL, SUNRPC XDR, and UAPI NFS ACL constants.

Risks and test signals: Risks are entry-count overflow, inline buffer under-sizing, and invalid ACL acceptance. Test max-entry ACLs, default/access ACL pairs, malformed XDR, and permission enforcement after set/get ACL.
