<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/commands_test.go

## Purpose

Verifies that the exported root command tree contains the expected command and subcommand paths.

## Important APIs, Types, and Functions

`collectPaths` recursively walks `cmds.Command.Subcommands`. `TestCommands` compares the collected set to a long expected list and then verifies each listed path can be resolved with `Root.Get`.

## Control Flow

The test builds a set from `Root`, deletes every expected path, reports missing and unexpected paths, and then iterates expected paths again to assert command lookup succeeds and does not return nil.

## State and Persistence Behavior

Pure command metadata test. No repo state is used.

## Dependencies and Integration Points

Depends on the global `Root` command tree and exact command names from many files in `core/commands`.

## Risks and Edge Cases

This is intentionally brittle: adding, removing, renaming, deprecating, or relocating commands requires updating the list. It does not inspect options or handler behavior.

## Test Signals

Strong signal for command registration coverage, including all commands in this subset. Weak signal for runtime behavior, help text content, and completion generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/commands_test.go -->
