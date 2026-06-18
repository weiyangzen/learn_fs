# File Research: sources/cow-pools/bcachefs-tools/src/commands/mod.rs

## Purpose
Defines the central bcachefs command framework: command metadata, typed/raw command macros, group command dispatch, clap CLI construction, module declarations, and top-level command grouping.

## Main Interfaces
- Types:
  - `CmdDef`
  - `CmdKind`
  - `GroupDef`
- Macros:
  - `typed_cmd!`
  - `raw_cmd!`
- Public functions:
  - `dispatch`
  - `build_cli`
  - `defers_shrinkers`
- Command table:
  - `COMMAND_GROUPS`

## Behavior
- `typed_cmd!` wraps a clap `Parser` type and handler into a `CmdDef`.
- `raw_cmd!` wraps manual argv parsers into a `CmdDef`.
- `CmdDef::dispatch` handles typed, raw, and group commands.
- Group commands dispatch to children by name or alias, otherwise print group help.
- `build_cli` constructs a clap command with all top-level subcommands.
- `defers_shrinkers` returns true for `mount` and `fusemount`.
- Defines a synthetic `fs` command group and an inline `version` command.

## Dependencies and Coupling
- Declares all command modules in this directory.
- Command grouping is the single registry used by dispatch/help.
- Relies on each module exporting expected `CMD` constants.
- Version command reads `../../version.h` at compile time.

## Important Implementation Notes
- Group child dispatch passes `argv[1..]`, making the child subcommand name become argv[0].
- Group help exits success for no subcommand or help request, failure for unknown subcommands.
- Aliases are stored per command and checked in both dispatch and group child matching.

## Risks and Edge Cases
- Any command missing from `COMMAND_GROUPS` is not reachable even if its module exists.
- `clap_command` for raw commands has minimal argument metadata.
- The command table manually controls user-visible organization and can drift from module additions.
