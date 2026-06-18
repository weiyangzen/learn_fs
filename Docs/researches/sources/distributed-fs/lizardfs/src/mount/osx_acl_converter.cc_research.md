## sources/distributed-fs/lizardfs/src/mount/osx_acl_converter.cc

Purpose: Apple-only conversion layer between macOS extended ACL xattr blobs and LizardFS `RichACL` objects.

Important APIs/functions: inside `#ifdef __APPLE__`, `extractAclObject` copies an ACL from xattr data and converts each allow/deny entry. `objectToOsxXattr` converts `RichACL` entries to a macOS ACL and serializes it. Helpers map RichACL permission bits to `acl_perm_t`, translate UUID qualifiers to uid/gid or NFS special identifiers, and map inheritance flags.

Control flow: extraction calls `acl_copy_int`, iterates entries with `acl_get_entry`, rejects unsupported tags/id types, builds `RichACL::Ace` values, inserts valid ACEs, and sets `RichACL::kAutoSetMode`. Serialization initializes an ACL sized to the RichACL, creates entries, fills permset/tag/qualifier/flags, then uses `acl_copy_ext`.

State and dependencies: no persistent state. Depends on macOS `sys/acl.h`, `membership.h`, RichACL, and syslog.

Risks: permission mappings are many-to-one for some RichACL bits, so round trips may lose detail. Errors often log and skip entries; an xattr with positive size but no valid ACE throws. The header includes macOS ACL declarations unconditionally, while implementation bodies are Apple-only, so build guards matter.

Test signals: should be tested on macOS with user/group/special identifier entries, allow/deny ACEs, inheritance flags, invalid UUIDs, and round-trip serialization.
