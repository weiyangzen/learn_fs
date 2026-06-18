# sources/cloud-native/containerd/internal/fsview/register.go

## Purpose
Defines the plugin extension point for fsview filesystem handlers.

## Important APIs, Types, And Functions
`FSHandler` optionally supplies `HandleMount`, `Getxattr`, and `IsWhiteout`. `Register` appends handlers to the package-level `registered` slice.

## Control Flow
Mount resolution and overlay helpers iterate registered handlers in append order, using handler functions when present.

## State And Persistence
Global in-memory `registered` slice persists for the process. There is no synchronization around registration or lookup.

## Dependencies And Integration Points
Depends on `io/fs` and containerd `mount.Mount`. EROFS fsview plugin registration uses this hook.

## Risks
Registration should happen at init time before concurrent use. Handler order affects which filesystem claims a mount or xattr first.

## Test Signals
Indirect coverage from fsview tests importing the EROFS plugin and resolving EROFS mounts.
