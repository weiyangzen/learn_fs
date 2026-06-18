# sources/cloud-native/containers-storage/drivers/chroot_unix.go

## Purpose
`chroot_unix.go` enters a filesystem root for reexec helper operations on non-Windows platforms.

## Important APIs, Types, And Functions
`chrootOrChdir(path string) error` calls `syscall.Chroot(path)` and then `syscall.Chdir("/")`.

## Control Flow
`chownByMapsMain` calls this before walking the layer so all subsequent paths are relative to the target root.

## State And Persistence
It changes process-local root and current working directory in the reexec child. It does not persist files.

## Dependencies And Integration Points
It depends on `os`, `syscall`, and `fmt`, and is part of the chown reexec flow.

## Risks
The function requires privileges/capabilities for `chroot`. Failure aborts the reexec helper. Once chrooted, error paths should avoid assuming access to the original filesystem.

## Test Signals
Indirectly covered by any ID-map chown tests on Unix platforms.
