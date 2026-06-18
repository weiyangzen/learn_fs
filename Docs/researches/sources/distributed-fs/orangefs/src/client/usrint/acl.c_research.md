# sources/distributed-fs/orangefs/src/client/usrint/acl.c
## sources/distributed-fs/orangefs/src/client/usrint/acl.c

**Purpose:** Implements POSIX ACL user-interface calls for OrangeFS by translating between libacl `acl_t` entries and OrangeFS ACL xattr records.

**APIs and control flow:** `pvfs_acl_delete_def_file()` verifies the path is a directory and removes `system.posix_acl_default`. `pvfs_acl_get_fd()` and `pvfs_acl_get_file()` fetch access/default ACL xattrs, resize the buffer if needed, allocate an `acl_t`, translate PVFS ACL tags to POSIX ACL tags, set qualifiers, and set permissions. `pvfs_acl_set_fd()` and `pvfs_acl_set_file()` validate `acl_t`, count entries, translate POSIX ACL tags/perms/qualifiers into `pvfs2_acl_entry` arrays, and write the appropriate xattr.

**State and dependencies:** No persistent state. Depends on `posix-pvfs.h` xattr/stat wrappers, libacl APIs, errno, and OrangeFS ACL constants from `usrint.h`.

**Risks and tests:** The get paths contain semicolons after permission-condition `if` statements, so READ/WRITE/EXECUTE are always added. Several error paths leak `pvfs_entry` or partially created ACLs. Set paths do not zero `pvfs_entry`, so `p_perm` can contain uninitialized bits before ORing. Tests should cover each tag/perm combination, default ACL on non-directories, xattr resize, invalid ACLs, qualifier memory handling, and round-trip get/set.
