# File Research: sources/block-storage/mdadm/ReadMe.c

## Purpose
`ReadMe.c` centralizes mdadm version text, command-line option tables, short-option strings, and user-facing help text.

## Contents
It defines:
- `Version`, with default `VERSION`, `VERS_DATE`, and `EXTRAVERSION`.
- Short option strings for normal, monitor, bitmap, and bitmap-auto parsing.
- `long_options[]`, mapping all major modes and flags to getopt tokens.
- General and mode-specific help strings for create, build, assemble, manage, misc, monitor, grow, incremental, and config.
- `mode_help[]`, selecting help by mdadm mode.
- `fprint_update_options()`, which prints valid `--update` or `--update-subarray` options from `update_options`.

## Integration Notes
This file is part parser metadata and part documentation. The option token values are consumed by mdadm's main argument parser, while the help strings define CLI-visible behavior and compatibility aliases such as `--monitor`/`--follow`, `--daemonise`/`--daemonize`, and deprecated `--auto`.

## Risks
Option definitions and help text can drift from parser behavior in other files. Because this file owns user-visible option registration, missing or mismatched entries can make otherwise implemented functionality inaccessible from the CLI.
