# sources/distributed-fs/juicefs/pkg/meta/utils_linux.go

## Purpose
`utils_linux.go` defines Linux-specific errno, flock, and xattr constants for metadata code.

## Important APIs, Types, and Functions
It exports `ENOATTR` as `syscall.ENODATA`, lock constants from `syscall`, and xattr create/replace constants from `golang.org/x/sys/unix`.

## Control Flow and State
There is no executable flow. Build selection ensures Linux metadata code uses Linux's xattr missing-value errno and native FUSE/lock flag values.

## State and Persistence Behavior
No state is persisted. Constants influence syscall-compatible return values and xattr flag validation in metadata operations.

## Dependencies and Integration Points
It is consumed by xattr and lock code throughout the meta package and by tests running on Linux. It depends on `syscall` and `x/sys/unix`.

## Risks and Test Signals
Risks are low but include wrong errno mapping for xattr absence or mismatched lock constants. Linux xattr create/replace and lock integration tests validate this file indirectly.
