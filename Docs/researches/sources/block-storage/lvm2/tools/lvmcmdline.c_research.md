# File Research: sources/block-storage/lvm2/tools/lvmcmdline.c

## Purpose
Central command-line engine for LVM2. It registers generated command definitions, parses arguments, selects the matching command variant, applies config/profile/runtime settings, initializes subsystems, dispatches command functions, and performs cleanup.

## Command Registration
- Global `commands[COMMAND_COUNT]` stores generated command definitions.
- `_cmdline` stores command tables used by parsing, usage, shell completion, and dispatch.
- `_command_functions[]` maps specific generated command enums to newer variant-specific implementations.
- `lvm_register_commands()`:
  - Calls `define_commands()`.
  - Assigns command indexes.
  - Computes valid options for each command name with `_set_valid_args_for_command_name()`.
  - Registers command names and valid argument tables.

## Argument Access Helpers
Provides shared helpers for command implementations:
- `arg_count()`, `arg_is_set()`, `arg_value()`, `arg_str_value()`.
- Integer, size, sign, percent, and grouped-argument accessors.
- List validators such as `arg_from_list_is_set()`, `arg_outside_list_is_set()`, negative/zero checks.
- `arg_force_value()` maps repeated `--force` to prompt policy.

## Value Parsers
Implements many option value parsers:
- Boolean-like activation and yes/no parsing.
- Cache mode, discards, mirror log, metadata type, report format, config type.
- Numeric parsing with signed/unsigned variants.
- Size parsing with sector storage, locale-aware decimal handling, byte alignment checks, IEC suffixes, and percent suffixes.
- Extent parsing with percent scopes like `%VG`, `%LV`, `%PVS`, `%FREE`, `%ORIGIN`.
- Validation for tags, permissions, allocation policy, lock type, segment type, readahead, region size, metadata copies, poll operation, repair/dump/headings types.

## Option Synonyms
- Translates historical or alternate names into canonical options:
  - `--available` to `--activate`
  - `--corelog` to `--mirrorlog`
  - `--resizable` to `--resizeable`
  - RAID-prefixed aliases
  - `--metadatacopies` to PV/VG-specific forms
  - `--profile` to metadata profile for selected commands.
- `_merge_synonym()` rejects simultaneous use of synonyms and copies values into canonical slots.

## Command Matching
`_find_command()` is the syntax selector:
- Matches the command name to generated command variants.
- Checks required options, any-required option groups, required positionals, `--select` substitutions, and special `lvcreate` VG name extraction.
- Handles `--type` specially so a typed command only matches compatible definitions.
- Rejects unused options and unused positional args.
- Applies early command rules for invalid or required option combinations.
- Logs the recognized command enum.

## Usage and Help
- `_usage()` prints command help, compacting common options for multi-variant commands.
- `_usage_all()` prints all commands.
- `help()` prints global command list, all usage, or selected command usage.
- `version()` prints LVM, device-mapper library, driver, and configure-line versions.

## Runtime Settings
- `_get_current_output_settings_from_args()` applies logging, quiet, verbose, debug, udev output, and journal options early.
- `_get_current_settings()` applies:
  - test mode, yes mode, activation settings
  - archive/backup/read-only behavior
  - command flags such as exported VG access, hints, one-scan capability, device-id warnings
  - devices file/list handling
  - activation mode: complete, partial, degraded
  - foreign/shared/history LV inclusion
  - device-name search policy
  - unit and suffix formatting
  - synonym merging.
- `_apply_current_settings()` applies logging, memlock, activation, archive/backup, metadata format, and missing-PV defaults.

## Profiles and Locking
- `_prepare_profiles()` handles `--profile`, `--commandprofile`, `--metadataprofile`, and `LVM_COMMAND_PROFILE`.
- Applies profile config trees and processes profilable config.
- `_init_lvmlockd()` configures lvmlockd use, lock options, skip flags, socket path, and command exceptions.
- `_init_md_checks()` sets md component detection/check mode.

## Main Dispatch
`lvm_run_command()`:
- Normalizes `--long-option` spellings by removing hyphens before `=`.
- Copies the command line for logging/backups.
- Finds command name and parses options with generated getopt data.
- Applies early output settings.
- Selects the exact command definition.
- Applies `--config`, refreshes toolcontext if needed, prepares profiles, initializes connections and filters.
- Applies final settings, locking, multipath, lvmlockd, and dmeventd monitoring.
- Dispatches either a command-enum-specific function or the command-name function.
- Cleans lvmlockd, locking, mpath, hints, lvmcache, labels, devices file, temporary config/profile trees, command memory pool, errno/log duplicate state.

## Program Entry
`lvm2_main()`:
- Detects aliases versus `lvm`/`lvm.static`/`initrd-lvm`.
- Ensures standard fds exist and configures custom log/report fds from environment.
- Closes stray daemon fds.
- For static builds, may exec the normal `lvm` binary once.
- Handles `lvm version` before full initialization.
- Rewrites help shorthand.
- Initializes tool context, registers commands, then runs:
  - interactive shell,
  - script file via `_run_script()`,
  - or single command via `lvm_run_command()`.
- Converts final internal return codes through `lvm_return_code()`.

## Other Utilities
- `lvm_split()` tokenizes simple quoted command strings and comments.
- `_run_script()` executes shebang-marked LVM scripts line by line.
- `_check_standard_fds()` attaches missing stdin/stdout/stderr to `/dev/null`.
- Custom fd parsing reads `LVM_OUT_FD`, `LVM_ERR_FD`, and `LVM_REPORT_FD`.

## Research Notes
This file is the primary integration point for generated command metadata, runtime configuration, device scanning policy, locking policy, and command dispatch. Most tool command files in this group depend on its argument accessors and processing lifecycle.
