# sources/distributed-fs/ipfs-kubo/core/commands/mount_windows.go

## Purpose

`mount_windows.go` is the Windows-specific `ipfs mount` stub. It preserves the command name while returning a clear runtime error because FUSE mounting is not implemented for Windows in this command path.

## Important APIs, Types, and Functions

The file defines `MountCmd` with help text and a `Run` function that returns `errors.New("Mount isn't compatible with Windows yet")`.

## Control Flow

Every invocation fails immediately without checking config, repo, node state, or arguments. Help text states the command is not implemented on Windows.

## State and Persistence Behavior

No state is read or written. No mount attempt is made.

## Dependencies and Integration Points

Dependencies are limited to Go `errors` and `go-ipfs-cmds`. The file is selected by filename/build convention for Windows and complements `mount_unix.go` and `mount_nofuse.go`.

## Risks and Test Signals

Risks are mainly UX and build selection: users should receive the Windows-specific incompatibility error, and the build should not accidentally include Unix or no-FUSE definitions. Build tests should compile Windows targets and command tests should assert the exact failure behavior remains non-mutating.
