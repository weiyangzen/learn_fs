<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/commands.go

## Purpose

Implements command-tree introspection through `ipfs commands`, shell completion subcommand wiring, and a CLI streaming helper for responses with per-entry non-fatal errors.

## Important APIs, Types, and Functions

`CommandsCmd(root)` returns the command tree lister. `Command`, `Option`, `commandEncoder`, `cmd2outputCmd`, and `cmdPathStrings` produce structured and text command listings. `CompletionCmd(root)` registers bash, zsh, and fish generation. `streamResult` prints streamed entries and aggregates non-fatal display errors.

## Control Flow

`CommandsCmd.Run` converts the root command tree into a `Command`, annotates whether options should be shown, and emits it. The text encoder recursively builds command paths, adds flag variants when requested, sorts output, and writes one line per path. Completion subcommands render scripts into a buffer and emit it as a stream. `streamResult` consumes response entries, invokes a callback, writes non-fatal errors to stderr, and returns a summary error if any occurred.

## State and Persistence Behavior

Read-only command metadata. It does not use repo state and marks itself with `SetDoesNotUseRepo(true)`.

## Dependencies and Integration Points

Uses `go-ipfs-cmds`, completion template functions from `completion.go`, and standard IO. `streamResult` is reused by CID and filestore command post-runs.

## Risks and Edge Cases

Command map iteration is normalized by sorting text output, but structured subcommand order is map-derived unless consumers sort. `streamResult` catches panics and converts them to internal errors, which protects CLI display but can hide callback bugs behind a generic message.

## Test Signals

`commands_test.go` checks the full root command tree and `Root.Get` lookup. Completion rendering has no dedicated tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands.go -->
