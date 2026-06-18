# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl.h

Purpose: internal POSIX ACL translator header exposing ACL allocation, reference counting, context access, and cache get/set operations to companion source files.

Important APIs, types, and functions: declares `posix_acl_new()`, `posix_acl_ref()`, `posix_acl_unref()`, `posix_acl_destroy()`, `posix_acl_ctx_get()`, `posix_acl_get()`, and `posix_acl_set()`.

Control flow: `posix-acl-xattr.c` uses the allocation/destruction functions while translating xattrs; `posix-acl.c` implements all declarations and uses get/set/ref APIs throughout FOP callbacks.

State and persistence: no standalone state. The declared functions manipulate in-memory ref-counted ACLs and per-inode contexts that mirror persistent ACL xattrs.

Dependencies and integration points: assumes Gluster core types such as `xlator_t` and `inode_t` are available from including translation units. It is the local contract between ACL core logic and xattr codec.

Risks and test signals: because this header does not include the type definitions itself, include order matters. Callers must obey refcount ownership: returned ACLs from `posix_acl_get()` need unref, and ACLs passed into `posix_acl_set()` are retained by the context. Test signals include leak/refcount checks during lookup, setxattr, forget, and translator fini.
