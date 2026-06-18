# sources/distributed-fs/ceph-client/fs/nfs/export.c

## Purpose
`export.c` provides exportfs operations for re-exporting an NFS-mounted filesystem. It encodes NFS inode identity into export file handles, reconstructs dentries from those handles, finds parent dentries when supported, and advertises export behavior flags appropriate for a remote filesystem.

## Important APIs, types, and functions
The public object is `nfs_export_ops`. Its callbacks are `nfs_encode_fh`, `nfs_fh_to_dentry`, and `nfs_get_parent`. Helper `nfs_exp_embedfh` locates the embedded NFS server file handle inside the exportfs raw file-handle word array.

Encoded handles contain high and low 32-bit portions of `NFS_FILEID(inode)`, the inode file type, and a serialized `struct nfs_fh`. The file explicitly uses `EXPORT_OP_NOSUBTREECHK`, so parent handles are not embedded.

## Control flow
`nfs_encode_fh` computes the number of 32-bit words needed for the fixed identity words plus the embedded NFS file handle. If the caller buffer is too small it reports the required size and returns `FILEID_INVALID`; otherwise it stores fileid, type, padding, copies the server file handle, and returns the encoded length as the file-handle type.

`nfs_fh_to_dentry` validates bounds and type/length consistency, reconstructs a minimal `nfs_fattr` from encoded fileid and type, tries `nfs_ilookup` with the embedded file handle, and falls back to server `getattr` followed by `nfs_fhget`. The final inode is converted to a disconnected alias dentry with `d_obtain_alias`.

`nfs_get_parent` requires protocol `lookupp` support. It sends LOOKUPP for the child inode, obtains the parent file handle and attributes, then returns a parent alias dentry.

## State and persistence behavior
The encoded export file handle is persistent from exportfs/NFSD's perspective but depends on the remote NFS server file handle remaining valid. The implementation does not persist local state. Reconstructed dentries rely on NFS inode cache lookup or server getattr to refresh attributes.

## Dependencies and integration points
This file integrates with Linux exportfs, NFSD re-export behavior, NFS inode/filehandle helpers, NFS RPC operation vectors, and tracepoints for stale handle diagnostics. Export flags tell upper layers that this is a remote filesystem, subtree checking is unsupported, close-before-unlink and flush-on-close are needed, atomic local attributes and locks should not be assumed, and weak cache consistency data is not supplied.

## Risks
Re-export correctness depends on server file-handle stability. Subtree checking is intentionally disabled because parent file handles may not fit. Bounds validation around embedded `struct nfs_fh` is critical because the input handle comes from an external file-handle decoder. `fh_type` is treated as the encoded word length, so callers with stale or corrupted handles should receive ESTALE-like NULL/ERR behavior.

## Test signals
Test export handle encode/decode with small buffers, maximum NFS file handles, stale handles, cached inode hits, getattr fallback, missing `lookupp`, parent lookup failures, file type mismatch, and re-export unlink/close behavior through NFSD.
