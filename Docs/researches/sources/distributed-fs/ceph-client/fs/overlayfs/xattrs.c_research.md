# sources/distributed-fs/ceph-client/fs/overlayfs/xattrs.c

## Purpose
`xattrs.c` implements OverlayFS VFS xattr handlers. It hides private OverlayFS metadata xattrs from users, escapes user-visible names that collide with OverlayFS' own namespace, copies up lower objects before xattr mutation, and selects trusted versus user xattr namespaces based on the `userxattr` mount option.

## Important APIs, types, and functions
Public functions are `ovl_is_private_xattr()`, `ovl_listxattr()`, and `ovl_xattr_handlers()`. Internal helpers classify names with `ovl_is_escaped_xattr()` and `ovl_is_own_xattr()`, perform real get/set/remove through `ovl_xattr_get()` and `ovl_xattr_set()`, filter list results with `ovl_can_list()`, allocate escaped names with `ovl_xattr_escape_name()`, and implement handler callbacks for own namespace and catch-all xattrs.

The handler arrays are `ovl_trusted_xattr_handlers` and `ovl_user_xattr_handlers`; each combines an "own" handler for `trusted.overlay.` or `user.overlay.` and a catch-all handler for all other xattrs.

## Control flow
Getting an xattr resolves the real metadata path via `ovl_i_path_real()` and calls `vfs_getxattr()` under OverlayFS creator credentials. Setting/removing first checks whether removal from a lower-only object is a valid replace by probing the lower xattr. If no upper exists, it copies the dentry up, takes upper write access, then sets or removes the real upper xattr via `ovl_do_setxattr()` or `ovl_do_removexattr()`. After mutation it copies timestamps and size metadata back to the overlay inode.

Listing xattrs reads the real dentry list, removes private OverlayFS metadata xattrs, conditionally exposes non-Overlay trusted xattrs only to init-user-namespace `CAP_SYS_ADMIN`, and unescapes xattrs that were stored as `*.overlay.overlay.<name>` to present the user's original collision name.

## State and persistence
This file mutates persistent xattrs on the upper layer only. Collision escaping protects OverlayFS metadata by storing user requests for `trusted.overlay.*` or `user.overlay.*` under an escaped prefix. It does not own separate in-memory state beyond temporary escaped-name buffers.

## Dependencies and integration points
It relies on namespace constants and upper write helpers from `overlayfs.h`, path helpers from `util.c`, copy-up from `copy_up.c`, and VFS xattr APIs. `super.c` installs the chosen handler array in `sb->s_xattr`.

## Risks
Namespace confusion is the main risk: exposing private xattrs, failing to escape collisions, or choosing the wrong trusted/user prefix could corrupt OverlayFS metadata or leak internals. Copy-up before mutation can fail, and removal semantics must avoid fabricating success for missing lower xattrs.

## Test signals
Test listing hides `overlay.*` metadata, escaped collision round trips, userxattr and trusted modes, unprivileged trusted xattr visibility, set/remove on lower-only files causing copy-up, `XATTR_REPLACE` removal failure when lower xattr is absent, and behavior when upper xattrs are unsupported.
