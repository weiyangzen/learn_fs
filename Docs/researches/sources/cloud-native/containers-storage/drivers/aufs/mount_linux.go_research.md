# sources/cloud-native/containers-storage/drivers/aufs/mount_linux.go

## Purpose
`mount_linux.go` is the Linux syscall shim used by the AUFS driver to create and remount AUFS unions.

## Important APIs, Types, And Functions
`mount(source, target, fstype string, flags uintptr, data string) error` calls `unix.Mount` with the same arguments.

## Control Flow
`aufsMount` uses this helper for the initial AUFS mount and any remount append operations when readonly branches exceed the page-sized mount option buffer.

## State And Persistence
It mutates kernel mount state only. No persistent files or package state are created here.

## Dependencies And Integration Points
The helper depends solely on `golang.org/x/sys/unix` and is package-private for AUFS code.

## Risks
The thin wrapper carries syscall semantics directly to callers. Error interpretation, option construction, and cleanup all occur in `aufs.go`.

## Test Signals
Indirectly covered by AUFS mount tests, including deep layer mount-data splitting.
