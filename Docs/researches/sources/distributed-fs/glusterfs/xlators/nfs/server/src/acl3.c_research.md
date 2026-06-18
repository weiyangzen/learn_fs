# sources/distributed-fs/glusterfs/xlators/nfs/server/src/acl3.c

## Purpose
Implements the NFS ACL version 3 RPC program for Gluster's NFS server. It handles NULL, GETACL, and SETACL procedures, resolves NFS file handles to Gluster locations, translates ACL wire entries to and from POSIX ACL xattr buffers, and submits XDR-encoded RPC replies.

## APIs, Types, and Functions
Important exported functions are `acl3svc_init()`, `acl3svc_null()`, `acl3svc_getacl()`, `acl3svc_setacl()`, `acl3_getacl_reply()`, and `acl3_setacl_reply()`. Internal flow uses `acl3svc_submit_reply()`, callbacks `acl3_stat_cbk()`, `acl3_default_getacl_cbk()`, `acl3_getacl_cbk()`, `acl3_setacl_cbk()`, resume functions `acl3_getacl_resume()` and `acl3_setacl_resume()`, and conversion helpers `acl3_nfs_acl_to_xattr()` and `acl3_nfs_acl_from_xattr()`. The file defines validation macros for NFSv3 state, Gluster file handles, file-handle-to-volume mapping, subvolume start state, resolved file handles, and call-state initialization. `acl3svc_actors` and `acl3prog` register the RPC program.

## Control Flow, State, and Persistence
GETACL decodes `getaclargs`, validates the mask and file handle, maps the handle to a volume, creates `nfs3_call_state_t`, resolves the file handle asynchronously, stats the resolved object, fills NFS attributes, then reads default ACL xattrs for directories and access ACL xattrs for all objects before replying. SETACL allocates max-size ACL arrays, decodes `setaclargs`, validates masks and handles, converts user and default ACL entries into `cs->aclxattr` and `cs->daclxattr`, resolves the file handle, builds a dict containing `POSIX_ACL_ACCESS_XATTR` and/or `POSIX_ACL_DEFAULT_XATTR`, calls `nfs_setxattr()`, then replies from callback. `acl3svc_init()` creates an ACL listener on `GF_ACL3_PORT`, honors insecure port settings, and uses a static `acl3_inited` boolean to make setup one-shot. Persistent effects are POSIX ACL xattrs on backend files and RPC listener registration.

## Dependencies and Integration
Depends on NFSv3 state/call-state helpers, Gluster RPC service APIs, XDR serializers/deserializers, iobuf/iobref pools, file-handle resolution, `nfs_getxattr()`, `nfs_setxattr()`, `nfs_stat()`, POSIX ACL xattr structures, endian conversion, and NFS message logging. It integrates as an auxiliary RPC program beside the main NFSv3 service.

## Risks and Test Signals
Risks include ACL count bounds, endian conversion correctness, default ACL flag masking, Solaris mask-bit compatibility, reply cleanup on asynchronous error paths, listener one-shot behavior across reloads, and possible null `cs` cleanup on early SETACL failures. Test signals include GETACL on files and directories with and without ACL xattrs, SETACL round trips for access and default ACLs, invalid masks returning `NFS3ERR_INVAL`, bad handles returning `NFS3ERR_BADHANDLE` or stale mapping, backend xattr ENODATA handling as success, and listener creation with insecure-port options.
