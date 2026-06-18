## sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.h

Purpose: Declares the metadata xattr toolkit API.

Important APIs/types/functions: Exposes `UserXAttrPrefix`, raw `listXAttrs()` and `getXAttr()`, sanitizers, user-prefixed set/remove/list helpers, and inline `getUserXAttr()` which prefixes the requested name before calling `getXAttr()`.

Control flow: Header-side flow is limited to inline prefix composition for `getUserXAttr()`.

State and persistence: API abstracts persisted Linux xattrs and BeeGFS's `user.bgXA.` namespace convention.

Dependencies and integration: Depends on `FhgfsOpsErr` and STL containers. Used by metadata xattr request handlers and ACL/user-xattr storage paths.

Risks and test signals: Callers must not pass already-prefixed names to user helpers. Tests should verify raw vs user helper behavior and exact name translation.
