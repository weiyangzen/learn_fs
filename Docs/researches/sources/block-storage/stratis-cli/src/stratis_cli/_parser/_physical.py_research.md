# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_physical.py

## Role

Defines parser command specifications for block-device commands.

## Commands

- `list`: list block devices, optionally filtered by pool name.
- `debug`: blockdev-level debug commands.

## Dependencies

Maps `list` to `PhysicalActions.list_devices` and imports blockdev debug subcommands.

## Notable Behavior

This is a compact parser module; actual listing behavior is implemented in `_actions/_physical.py`.
