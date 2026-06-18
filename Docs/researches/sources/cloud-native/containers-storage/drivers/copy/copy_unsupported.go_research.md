# sources/cloud-native/containers-storage/drivers/copy/copy_unsupported.go

## Purpose
`copy_unsupported.go` provides fallback copy helpers for non-Linux or non-cgo builds.

## Important APIs, Types, And Functions
It defines `Mode` with only `Content`, `DirCopy`, `CopyRegularToFile`, and `CopyRegular`. `DirCopy` and `CopyRegular` use `chrootarchive.NewArchiver(nil).CopyWithTar`; `CopyRegularToFile` uses `io.Copy`.

## Control Flow
Fallback paths avoid Linux-specific syscalls and metadata logic by relying on tar-based copy where possible.

## State And Persistence
The destination tree/file is created by tar extraction or stream copy. No acceleration flags are used despite parameters being present for API compatibility.

## Dependencies And Integration Points
It preserves the public package API for unsupported platforms and depends on `chrootarchive`, `io`, and `os`.

## Risks
Behavior differs from Linux: no `Hardlink` mode constant, no explicit xattr selection logic, and `CopyRegular` uses tar copy semantics. Callers with Linux-specific metadata expectations must be build-tag aware.

## Test Signals
Build-only in this subset; Linux tests do not run against this implementation.
