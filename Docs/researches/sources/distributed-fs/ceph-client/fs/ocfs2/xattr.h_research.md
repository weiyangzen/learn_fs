# sources/distributed-fs/ceph-client/fs/ocfs2/xattr.h

Purpose: declares the OCFS2 xattr namespace identifiers, VFS handler exports, public xattr manipulation APIs, security initialization helpers, reflink/refcount hooks, and the value-buffer bridge used by xattr value extent-tree code.

Important APIs and types: `enum ocfs2_xattr_type` maps OCFS2 on-disk namespace indexes for user, ACL access, ACL default, trusted, and security xattrs. `struct ocfs2_security_xattr_info` carries deferred LSM xattr initialization data during inode creation. `struct ocfs2_xattr_value_buf` pairs a buffer head, journal access callback, and `ocfs2_xattr_value_root` pointer so common value-tree code can operate on inline inode storage, external xattr blocks, or bucket-contained roots. The header declares `ocfs2_xattr_get_nolock`, `ocfs2_xattr_set`, `ocfs2_xattr_set_handle`, `ocfs2_xattr_remove`, `ocfs2_reflink_xattrs`, and `ocfs2_init_security_and_acl`.

Control flow: this file has no executable control flow, but it separates locked and lockless contracts. `ocfs2_xattr_get_nolock` assumes the caller already holds the inode lock and xattr semaphore, while `ocfs2_xattr_set` owns normal locking and transaction setup. `ocfs2_xattr_set_handle` is the create-time variant that receives an existing handle and pre-reserved allocation contexts.

State and persistence behavior: all persistent layout is defined in `ocfs2_fs.h`; this header exposes only the helper state required to reach and journal value roots. `ocfs2_security_xattr_info.value` can own a kmemdup'd LSM value until `ocfs2_init_security_set` installs it.

Dependencies and integration points: includes Linux xattr definitions and is included by OCFS2 inode creation, ACL, security, reflink, and teardown code. Handler declarations feed the superblock xattr handler table, while refcount/reflink declarations connect xattrs to OCFS2 copy-on-write support.

Risks: callers must respect the locking distinction between public and `_nolock` APIs. Passing the wrong `vb_access` function or buffer head in `ocfs2_xattr_value_buf` can journal the wrong metadata class. Security init callers must free or consume deferred `ocfs2_security_xattr_info.value` according to the surrounding create path.

Test signals: compile coverage with ACL/security/reflink paths, create-time LSM xattr installation, direct `getxattr` under existing inode locks, xattr removal during evict, and reflink tests that preserve or drop security xattrs.
