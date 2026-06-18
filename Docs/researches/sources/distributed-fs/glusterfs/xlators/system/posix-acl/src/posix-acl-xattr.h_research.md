# sources/distributed-fs/glusterfs/xlators/system/posix-acl/src/posix-acl-xattr.h

Purpose: public internal header for POSIX ACL xattr conversion helpers.

Important APIs, types, and functions: declares `posix_acl_from_xattr()`, `posix_acl_to_xattr()`, and `posix_acl_matches_xattr()`.

Control flow: included by `posix-acl.c` so translator FOP wrappers can decode lower xattrs, encode inherited ACLs, and compare cached ACLs with newly returned xattr data.

State and persistence: no state. The functions declared here bridge transient in-memory ACL objects and persistent xattr bytes.

Dependencies and integration points: includes `posix-acl.h` for ACL allocation/refcount API and `glusterfs/glusterfs-acl.h` for ACL binary format constants.

Risks and test signals: API users must pass trusted buffer lengths and unref returned ACLs. Test signals mirror `posix-acl-xattr.c`: parse/serialize/match coverage and malformed xattr handling.
