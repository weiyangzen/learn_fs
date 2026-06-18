<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/completion.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/completion.go

## Purpose

Generates bash, zsh, and fish completion scripts from the Kubo command tree.

## Important APIs, Types, and Functions

`completionCommand` and `singleOption` are template models. `commandToCompletions` converts a `cmds.Command` tree into sorted subcommands and option buckets. `writeBashCompletions`, `writeFishCompletions`, and `writeZshCompletions` execute templates initialized in `init`.

## Control Flow

`commandToCompletions` recursively parses subcommands, separates boolean options as flags from value options, records short and long names, and sorts names for deterministic template output. Templates define shell-specific functions that skip flags, descend subcommands, and complete options or subcommands based on current position.

## State and Persistence Behavior

No persistent state. Package-level templates are parsed once at initialization and reused.

## Dependencies and Integration Points

Depends on `text/template` and `go-ipfs-cmds` option metadata. Called from `CompletionCmd` in `commands.go`.

## Risks and Edge Cases

Template quoting is sensitive to option descriptions and subcommand names. Zsh generation reuses bash completion through `bashcompinit`. Fish predicates model subcommand traversal and may drift from command parser behavior.

## Test Signals

No dedicated tests here. Command tree tests indirectly ensure the completion command is registered. Useful tests would snapshot generated scripts for representative command trees and descriptions with quotes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/completion.go -->
