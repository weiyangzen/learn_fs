# sources/distributed-fs/ceph/src/client/Dentry.cc

## Purpose
`Dentry.cc` implements debug/dump/refcount glue for client metadata-cache dentries.

## Important APIs, Types, and Functions
`Dentry::dump()` emits name, parent dir inode, target inode, refcount, offset, lease data, and cap shared generation. `Dentry::print()` formats a compact debug representation including alternate encrypted name and rename state. `intrusive_ptr_add_ref()` and `intrusive_ptr_release()` adapt `Dentry` to `boost::intrusive_ptr`.

## Control Flow
Dump/print read current dentry fields without modifying state. Intrusive pointer add/release call `get()`/`put()`, which are defined inline in `Dentry.h` and handle LRU pinning and deletion.

## State and Persistence Behavior
No persistent state is written. This file surfaces volatile cache state: lease TTL/gen/seq, link target, refcount, and cap shared generation for diagnostics.

## Dependencies and Integration Points
It depends on `Dentry.h`, `Dir.h`, `Inode.h`, `Formatter`, and string escaping helpers. `DentryRef.h` relies on these intrusive pointer functions.

## Risks and Edge Cases
Debug code assumes `dir` and `dir->parent_inode` are valid while dumping. Printing binary/encrypted names uses bounded escaping, which is important for fscrypt alternate names.

## Test Signals
Use cache dump/admin output, intrusive pointer ref balance, formatted encrypted alternate names, and negative dentries with null inode.
