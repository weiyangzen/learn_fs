<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/external.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/external.go

## Purpose

Creates placeholder commands that delegate to external binaries named after the `ipfs` command path.

## Important APIs, Types, and Functions

`ExternalBinary(instructions string) *cmds.Command` returns a command with variadic `args`, `External: true`, `NoRemote: true`, and a run handler that locates and executes the external binary.

## Control Flow

The handler builds `ipfs-<path-components>` as the binary name. If missing and the user requested `--help` or `-h`, it emits explanatory help with installation instructions; otherwise it errors. If installed, it creates an `io.Pipe`, starts the process with arguments, discards stdin, combines stdout/stderr into the pipe writer, emits the pipe reader, waits for the process in a goroutine, and returns the process exit error.

## State and Persistence Behavior

Does not mutate repo state directly. It executes a local process that may have arbitrary side effects outside this code's control.

## Dependencies and Integration Points

Uses `os/exec`, process environment, pipes, and go-ipfs-cmds external command metadata.

## Risks and Edge Cases

Stdin is intentionally not passed through. Stdout and stderr are merged, losing stream distinction. External process behavior and side effects are outside command framework guarantees.

## Test Signals

No direct tests. Useful tests would mock PATH for missing/help behavior, successful streaming, nonzero exit status, and binary naming from nested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/external.go -->
