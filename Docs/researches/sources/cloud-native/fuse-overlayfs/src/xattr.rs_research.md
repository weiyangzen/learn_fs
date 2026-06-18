# sources/cloud-native/fuse-overlayfs/src/xattr.rs

## Purpose
`xattr.rs` defines overlay xattr namespaces and policy for hiding internal attributes, encoding otherwise-hidden attributes in container stat-override mode, and filtering listxattr results.

## Important APIs, Types, And Functions
Constants define internal prefixes and names: `user.fuseoverlayfs.*`, `user.overlay.*`, `trusted.overlay.*`, `user.containers.override_`, `security.`, and `.wh..wh..opq`. `can_access_xattr` decides whether a user-facing name is visible. `is_encoded_xattr_name`, `decode_xattr_name`, `encode_xattr_name`, and `filter_xattr_list` transform names according to `StatOverrideMode`.

## Control Flow
FUSE xattr operations call `encode_xattr_name` before get/set/remove and `filter_xattr_list` after listing raw layer xattrs. In containers mode, inaccessible internal names may be stored under the `user.containers.override_` prefix and decoded when listed.

## State And Persistence
The module is stateless policy logic. Persistent effects happen when encoded names are passed to `sys::xattr` from overlay operations.

## Dependencies And Integration Points
`overlay.rs` uses it in FUSE xattr callbacks. `whiteout.rs` uses constants for opaque xattrs and sentinels. The datasource stat override mode determines whether privileged/internal names can be encoded instead of rejected.

## Risks
Incorrect filtering can expose overlay internals or hide legitimate user attributes. The 255-byte xattr-name limit is enforced only for encoded names. Invalid UTF-8 names in list buffers are silently skipped. Containers mode hides `security.*`, which affects SELinux-like labels.

## Test Signals
Unit tests cover access policy, decode behavior, encode behavior, and filtering of null-separated list buffers. Integration tests cover user xattrs, large xattrs, opaque markers, and stat override behavior through FUSE.
