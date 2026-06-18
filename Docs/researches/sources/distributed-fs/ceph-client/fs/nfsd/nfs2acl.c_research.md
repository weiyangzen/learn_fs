# sources/distributed-fs/ceph-client/fs/nfsd/nfs2acl.c

## Purpose
`nfs2acl.c` implements the version 2 NFSACL side protocol for NFSD. It exposes NULL, GETACL, SETACL, GETATTR, and ACCESS procedures over the NFSD dispatcher using NFSv2-style filehandles and NFSv3 ACL helper structures.

## Important APIs, types, and functions
Procedure handlers are `nfsacld_proc_null()`, `nfsacld_proc_getacl()`, `nfsacld_proc_setacl()`, `nfsacld_proc_getattr()`, and `nfsacld_proc_access()`. XDR helpers decode GETACL/SETACL/ACCESS arguments and encode GETACL/ACCESS replies. Release helpers free filehandles and POSIX ACL references. The registration object is `const struct svc_version nfsd_acl_version2` backed by `nfsd_acl_procedures2`.

## Control flow
GETACL verifies the filehandle with no-op access, validates the requested mask, gets attributes, fetches access/default POSIX ACLs, synthesizes a minimal access ACL from inode mode when absent, and defers ACL release to the release hook. SETACL verifies setattr permission, obtains write access, locks the inode, sets access and default POSIX ACLs, unlocks/drops write access, gets final attributes, and releases decoded ACLs. GETATTR and ACCESS are thin wrappers around `fh_getattr()` and `nfsd_access()`. The procedure table wires decode, encode, release, cache behavior, and estimated XDR response sizes.

## State and persistence
This service stores no private state. Persistent effects occur only when SETACL writes POSIX ACLs to the target inode through the filesystem. Per-CPU procedure counters are maintained by the service dispatch layer.

## Dependencies and integration points
It depends on NFSD filehandle verification, VFS POSIX ACL helpers, NFSACL stream encode/decode helpers, NFSD attribute and access helpers, and the generic `nfsd_dispatch` path. It shares several NFSv3 ACL data structures even though it registers protocol version 2.

## Risks and test signals
Risks include mask validation differences from v3 (`nfserr_io` for bad GETACL mask), setting default ACLs on non-directories, ACL memory leaks on decode or partial failure, inode lock/write-access ordering, and Solaris compatibility assumptions. Test signals include GETACL with access/default/count masks, files without stored ACLs, SETACL with invalid masks, non-directory default ACL attempts, ACCESS with varied permission bits, release-hook leak checks, and v2 ACL client interoperability.
