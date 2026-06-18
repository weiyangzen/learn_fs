# sources/distributed-fs/ceph-client/fs/nfsd/nfs3acl.c

## Purpose
`nfs3acl.c` implements the NFSACL version 3 side protocol for NFSD, exposing NULL, GETACL, and SETACL procedures with NFSv3 filehandle and post-op-attribute encoding.

## Important APIs, types, and functions
Procedure handlers are `nfsd3_proc_null()`, `nfsd3_proc_getacl()`, and `nfsd3_proc_setacl()`. XDR helpers are `nfs3svc_decode_getaclargs()`, `nfs3svc_decode_setaclargs()`, `nfs3svc_encode_getaclres()`, `nfs3svc_encode_setaclres()`, and `nfs3svc_release_getacl()`. The service table is `nfsd_acl_procedures3`, exported through `nfsd_acl_version3`.

## Control flow
GETACL decodes an NFSv3 filehandle and mask, verifies access, rejects unknown mask bits with `nfserr_inval`, fetches requested access/default POSIX ACLs, synthesizes an access ACL from mode if absent, and encodes status plus post-op attrs and ACL payloads. SETACL decodes optional access/default ACLs according to the mask, verifies setattr permission, takes write access, locks the inode, sets both ACL types, unlocks/drops write access, and encodes status plus post-op attributes. Release hooks free filehandles and ACL references.

## State and persistence
The module maintains only per-CPU procedure counters. SETACL persists ACL changes in the backing filesystem; GETACL state is temporary POSIX ACL references attached to the response.

## Dependencies and integration points
It depends on NFSv3 XDR helpers in `nfs3xdr.c`, POSIX ACL VFS helpers, NFSD filehandle/access infrastructure, and `nfsd_dispatch`. It complements the core NFSv3 procedure table in `nfs3proc.c`.

## Risks and test signals
Risks include ACL reference leaks, post-op attrs after failure, invalid mask handling, setting ACLs under idmapped-mount assumptions (`nop_mnt_idmap`), and filesystem-specific ACL rejection. Test signals include Linux NFSv3 ACL client GETACL/SETACL, invalid masks, missing access ACL synthesis, default ACL on non-directory, filesystem without ACL support, and reply-size limits for maximum ACL entries.
