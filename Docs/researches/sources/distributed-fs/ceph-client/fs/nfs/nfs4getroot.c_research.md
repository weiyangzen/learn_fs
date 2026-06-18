# sources/distributed-fs/ceph-client/fs/nfs/nfs4getroot.c

## Purpose

`nfs4getroot.c` provides the small root-filehandle helper used during NFSv4 server setup. It retrieves the server pseudo-root filehandle, verifies it is a directory, and stores the root FSID on the `nfs_server`.

## Important APIs, Types, and Functions

The file exports `nfs4_get_rootfh(struct nfs_server *server, struct nfs_fh *mntfh, bool auth_probe)`. It allocates an `nfs_fattr`, calls `nfs4_proc_get_rootfh`, validates `NFS_ATTR_FATTR_TYPE` and `S_ISDIR(fattr->mode)`, copies `fattr->fsid` into `server->fsid`, and frees the attribute object.

## Control Flow

The control flow is linear: allocate fattr, call the NFSv4 procedure layer, return the negative RPC/procedure error if lookup fails, reject non-directory or missing-type results with `-ENOTDIR`, copy FSID on success, and release the fattr in all cases.

## State and Persistence Behavior

The only state mutation is `server->fsid`, an in-memory identity field used by the mounted `nfs_server`. The remote filehandle and attributes come from the server; nothing is persisted locally.

## Dependencies and Integration Points

`nfs4_server_common_setup` in `nfs4client.c` calls this before probing server capabilities and inserting the server into global lists. It depends on `nfs_alloc_fattr`, `nfs_free_fattr`, `nfs4_proc_get_rootfh`, and standard inode mode helpers.

## Risks and Edge Cases

The main risk is accepting a malformed root response. The helper requires a valid type attribute and a directory mode. Allocation failure returns `-ENOMEM`; procedure failure is logged with `dprintk`.

## Test Signals

Mount tests should cover a normal NFSv4 pseudo-root, auth probing, server errors from rootfh lookup, missing/invalid type attributes, and a server returning a non-directory root filehandle.
