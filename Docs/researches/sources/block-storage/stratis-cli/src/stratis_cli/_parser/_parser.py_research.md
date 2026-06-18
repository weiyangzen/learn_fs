# File Research: sources/block-storage/stratis-cli/src/stratis_cli/_parser/_parser.py

## Role

Generic argparse builder for the `stratis` CLI.

## Parser Builder Functions

- `gen_subparsers()` customizes help behavior for subparser choices.
- `PrintHelpAction` prints help for a selected subcommand family.
- `print_help()` handles missing command errors.
- `_add_groups()`, `_add_args()`, and `_add_mut_ex_args()` add declarative parser specs.
- `add_subcommand()` recursively builds subcommand trees.
- `gen_parser()` builds the root parser.

## Root Commands

Defines root commands for `pool`, `blockdev`, `filesystem`/`fs`, `report`, `key`, `debug`, and `daemon`.

## Global Arguments

Adds `--propagate` and `--unhyphenated-uuids`.

## Version Gate

Most commands default to running `check_stratisd_version`; parser defaults can override this for commands that must work without a compatible daemon.

## Notable Risk Areas

The whole command tree depends on declarative tuple/dict specs from sibling parser modules. Incorrect keys or namespace names can surface only when a command path is exercised.
