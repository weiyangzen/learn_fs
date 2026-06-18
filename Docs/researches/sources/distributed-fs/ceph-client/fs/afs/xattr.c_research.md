# sources/distributed-fs/ceph-client/fs/afs/xattr.c

Purpose: Exposes AFS metadata and ACL operations through Linux extended attributes instead of pioctl-style control calls.

Important APIs and functions: The exported handler table `afs_xattr_handlers[]` registers `afs.acl`, `afs.cell`, `afs.fid`, `afs.volume`, and `afs.yfs.*`. `afs_xattr_get_acl()`/`afs_xattr_set_acl()` fetch and store classic AFS ACLs. `afs_xattr_get_yfs()` and `afs_xattr_set_yfs()` handle YFS opaque ACL data and metadata fields. Metadata getters return cell name, FID text, and volume name.

Control flow: ACL getters allocate an AFS operation, set vnode slot 0, issue fetch RPCs, detach returned ACL buffers from the operation, and copy the data or return required size. Setters reject `XATTR_CREATE`, package the user buffer in `struct afs_acl`, and run synchronous store operations. YFS getters interpret suffix names (`acl`, `acl_inherited`, `acl_num_cleaned`, `vol_acl`) and request only needed opaque ACL parts.

State and persistence: This file does not persist local metadata beyond temporary operation ACL buffers. Successful ACL RPCs commit vnode status through `afs_acl_success()`. The static metadata xattrs reflect current vnode, volume, and cell fields.

Dependencies and integration points: Uses Linux xattr handlers, AFS/YFS operation dispatch, vnode status commit, ACL allocation helpers, and YFS opaque ACL free logic from `yfsclient.c`.

Risks: Buffer-size behavior must match xattr ABI: size query when `size == 0`, `-ERANGE` for undersized buffers. YFS unsupported errors are translated to `-ENODATA`. Set paths must free ACL buffers on all operation outcomes.

Test signals: Size-query and short-buffer reads, invalid YFS suffixes, unsupported YFS ACL RPCs, setting only `afs.yfs.acl`, rejecting create-only set flags, and formatting FIDs with and without high vnode bits.
