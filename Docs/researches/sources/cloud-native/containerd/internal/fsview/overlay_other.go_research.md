# sources/cloud-native/containerd/internal/fsview/overlay_other.go

## Purpose
Provides non-Linux overlay helper behavior using registered handlers only.

## Important APIs, Types, And Functions
`getxattr` delegates to registered handlers. `isOpaque` checks overlay opaque xattrs through that abstraction. `isWhiteout` recognizes char-device mode only if a handler confirms it.

## Control Flow
Userspace overlay code can still handle non-native filesystem implementations such as EROFS plugins if they register xattr and whiteout capabilities.

## State And Persistence
No state beyond the shared handler registry.

## Dependencies And Integration Points
Uses `io/fs` and `register.go` handlers.

## Risks
Native non-Linux filesystems will not detect overlay whiteouts/opaque dirs unless a handler is registered. Behavior may differ from Linux overlay semantics.

## Test Signals
No direct non-Linux tests in this subset. Compile and plugin-driven EROFS behavior provide indirect signal.
