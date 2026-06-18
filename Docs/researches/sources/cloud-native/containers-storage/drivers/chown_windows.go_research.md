# sources/cloud-native/containers-storage/drivers/chown_windows.go

## Purpose
`chown_windows.go` provides a Windows stub for platform `LChown`.

## Important APIs, Types, And Functions
It defines empty `platformChowner`, `newLChowner`, and `LChown`, which returns an `os.PathError` wrapping `syscall.EWINDOWS`.

## Control Flow
Any attempted ID-map chown on Windows fails immediately for the path being processed.

## State And Persistence
No state is mutated and no filesystem ownership changes occur.

## Dependencies And Integration Points
It satisfies the shared chown API on Windows builds.

## Risks
Callers must not assume ID-map shifting works on Windows. The error is explicit and should propagate to higher-level storage operations.

## Test Signals
Build coverage only in this subset.
