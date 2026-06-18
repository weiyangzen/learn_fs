# sources/distributed-fs/ceph-client/fs/jffs2/xattr.h

## Purpose
Defines JFFS2 xattr in-memory data structures, lifecycle flags, delete-marker encoding, exported subsystem APIs, and compile-time fallbacks.

## Important APIs, types, and functions
`struct jffs2_xattr_datum` stores xid/version, CRC, hash, name/value cache pointers, and refcount. `struct jffs2_xattr_ref` stores an inode-to-datum link and is reused during scanning as raw `(ino,xid)`. Flags include `HOT`, `BIND`, `DEAD`, and `INVALID`; `XREF_DELETE_MARKER` marks deleted refs. The header exports build/setup/clear, inode delete/free/CRC-check, GC, get/set/list, and xattr handlers.

## Control flow
With `CONFIG_JFFS2_FS_XATTR`, consumers call real xattr functions from scan, inode eviction, GC, and VFS handlers. Without it, init/clear are no-ops, verification succeeds, and handlers/listxattr are null.

## State and persistence behavior
The structures mirror on-flash raw xattr and xref nodes. Unions in refs are interpreted as numeric ids during scan/build and as pointers after binding.

## Dependencies and integration points
Depends on Linux xattr/list types and JFFS2 core types. Optional security support exports `jffs2_init_security()` and a security xattr handler.

## Risks and test signals
Risks are structure contract drift, reading union fields in the wrong phase, and config guard mismatches. Build all xattr/security/ACL combinations.
