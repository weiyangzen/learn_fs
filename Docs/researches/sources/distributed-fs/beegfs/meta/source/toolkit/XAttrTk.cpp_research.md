## sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.cpp

Purpose: Wraps Linux xattr operations for metadata entries, translating user-visible xattrs into BeeGFS-internal names and mapping errno to `FhgfsOpsErr`.

Important APIs/types/functions: `UserXAttrPrefix` is `user.bgXA.`. `listXAttrs()` returns raw xattr names. `getXAttr()` reads bounded xattr data. `sanitizeForUser()` removes non-user metadata attrs and strips the prefix. `removeMetadataAttrs()` filters names. `setUserXAttr()` writes prefixed user xattrs and optionally enforces `XATTR_LIST_MAX`. `removeUserXAttr()` removes a prefixed xattr. `listUserXAttrs()` lists and sanitizes user-visible names.

Control flow: List uses a two-step `listxattr()` size/read sequence. Set first tries `setxattr()`; when list-length limiting is enabled and creation is needed, it locks one of 1024 path-hashed mutexes, checks current list length, and retries without forced replace. Errno is translated to BeeGFS errors with unexpected failures logged server-side.

State and persistence: Persists user xattrs under prefixed names on metadata files. The path-hashed static mutex array is in-memory concurrency control for list-length enforcement.

Dependencies and integration: Uses `Program::getApp()->getConfig()->getLimitXAttrListLength()`, BeeGFS logging, `StringTk`, `Mutex`, and POSIX xattr syscalls.

Risks and test signals: `listXAttrs()` allocates `new char[0]` when there are no xattrs and then builds a string from size 0; this is usually fine but worth guarding. The list-length check can still race with non-BeeGFS writers or hash collisions. Tests should cover errno mappings, prefix stripping, metadata filtering, list-limit NOSPACE behavior, and create-vs-replace flag semantics.
