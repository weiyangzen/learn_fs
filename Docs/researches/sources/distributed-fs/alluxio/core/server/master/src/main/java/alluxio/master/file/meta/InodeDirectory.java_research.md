# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectory.java

Purpose: read-only forwarding wrapper for directory-specific inode view behavior.

Important APIs and types: extends `Inode` and implements `InodeDirectoryView`. Delegates `isMountPoint`, `isDirectChildrenLoaded`, and `getChildCount` to the wrapped directory view.

Control flow: created by `Inode.wrap` when the delegate is a non-file `InodeDirectoryView`. Callers use it after `asDirectory` or direct wrapping to access directory-only fields.

State and persistence behavior: no owned persistence. Delegated fields reflect persisted inode metadata such as mount-point flag, direct-children-loaded flag, and child count.

Dependencies and integration points: depends on `InodeDirectoryView` and base `Inode`. Used by metadata sync, inode traversal, and file master directory logic.

Risks: wrapper is read-only but not necessarily immutable if delegate changes. It assumes delegate is a directory view; construction does not independently validate `isDirectory`.

Test signals: tests should cover delegated directory fields, wrapping through `Inode.wrap`, and invalid `asDirectory` behavior in base class.
