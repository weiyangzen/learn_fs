# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeDirectoryView.java

Purpose: read-only interface for directory-specific inode metadata.

Important APIs and types: extends `InodeView` and adds `isMountPoint`, `isDirectChildrenLoaded`, and `getChildCount`.

Control flow: concrete inode implementations expose directory fields through this interface. `Inode.wrap` requires non-file delegates to implement it and wraps them in `InodeDirectory`.

State and persistence behavior: interface only. The fields represent persisted or derived directory metadata used for mount behavior, listing completeness, and child accounting.

Dependencies and integration points: depends on `InodeView`. Integrated across inode store, inode tree, listing, metadata sync, and mount handling.

Risks: implementations must keep `isDirectory` from `InodeView` consistent with directory-specific methods. Incorrect direct-children-loaded state affects metadata sync and listing behavior.

Test signals: implementation tests should verify mount point, direct children loaded, and child count survive journal/proto/checkpoint round trips.
