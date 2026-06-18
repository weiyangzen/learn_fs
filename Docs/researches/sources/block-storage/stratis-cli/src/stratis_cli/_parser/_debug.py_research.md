# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_debug.py

## Role

Defines parser command specifications for debug commands.

## Command Groups

- Top-level debug: `refresh`, `uevent`.
- Pool debug: `get-object-path`, `get-metadata`.
- Filesystem debug: `get-object-path`, `get-metadata`.
- Blockdev debug: `get-object-path`.

## Dependencies

References debug action methods and shared UUID/name argument groups.

## Notable Behavior

The parser specs are declarative tuples consumed by `_parser/_parser.py`. Pool and filesystem metadata commands support pretty JSON output and written-vs-current metadata selection.
