# sources/cloud-native/containers-storage/drivers/driver_darwin.go

## Purpose
`driver_darwin.go` provides Darwin-specific driver priority and filesystem magic behavior.

## Important APIs, Types, And Functions
`Priority` contains only `vfs`. `GetFSMagic` returns `FsMagicUnsupported` with no error.

## Control Flow
On Darwin, automatic graphdriver selection will prefer VFS and filesystem-specific drivers cannot rely on actual statfs magic from this file.

## State And Persistence
No mutable state is maintained.

## Dependencies And Integration Points
It satisfies platform symbols required by `driver.go`.

## Risks
Filesystem compatibility checks are effectively disabled except by individual drivers. Darwin storage behavior is therefore expected to use VFS.

## Test Signals
Build-only in this subset.
