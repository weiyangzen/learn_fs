<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/helptext_test.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/helptext_test.go

## Purpose

Recursively checks that commands have help taglines.

## Important APIs, Types, and Functions

`checkHelptextRecursive` calls `ProcessHelp`, skips external commands, and runs subtests for help fields. `TestHelptexts` starts from `Root`.

## Control Flow

For each command it verifies `Helptext.Tagline` is non-empty. Checks for long description, short description, and synopsis exist but are skipped. It then recurses into subcommands.

## State and Persistence Behavior

Pure metadata test.

## Dependencies and Integration Points

Uses the global `Root` command tree and go-ipfs-cmds help processing.

## Risks and Edge Cases

Skipped subtests mean only taglines are enforced. External commands are skipped to avoid requiring generated or plugin help.

## Test Signals

Good lightweight signal that command additions include a tagline. Weak signal for full help quality and option documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/helptext_test.go -->
