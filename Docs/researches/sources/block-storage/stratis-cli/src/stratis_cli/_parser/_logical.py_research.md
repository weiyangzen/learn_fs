# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_logical.py

## Role

Defines parser command specifications for filesystem-level commands.

## Helpers

- `parse_range_or_current()` accepts a size range or the literal `current`.
- `FilesystemListOptions.verify()` rejects ambiguous filesystem list invocations where a pool name and UUID/name selector are both supplied inconsistently.

## Commands

Defines `create`, `snapshot`, `list`, `destroy`, `rename`, `set-size-limit`, `unset-size-limit`, `schedule-revert`, `cancel-revert`, and `debug`.

## Dependencies

Maps commands to `LogicalActions`, uses filesystem debug subcommands, and shared range/UUID/name parser helpers.

## Notable Risk Areas

The list command supports both pool-name filtering and detailed filesystem selection. The post-parser verifier prevents confusing combinations before action execution.
