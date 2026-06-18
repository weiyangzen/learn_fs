# File Research: sources/block-storage/parted/parted/command.c

## Purpose

`command.c` implements command registration, lookup, help display, and dispatch for the interactive/non-interactive `parted` frontend.

## Main Responsibilities

- Allocates `Command` objects with names, method callback, summary, help text, and non-interactive flag.
- Frees command name/summary/help string lists.
- Registers commands into a NULL-terminated command array.
- Resolves command names by exact or unambiguous partial match.
- Collects all command names into one `StrList`.
- Prints command summaries and help text with wrapping based on terminal width.
- Runs a command callback.

## Important Functions

- `command_create()`
- `command_destroy()`
- `command_register()`
- `command_get()`
- `command_get_names()`
- `command_print_summary()`
- `command_print_help()`
- `command_run()`

## Behavior Details

`command_get()` returns an exact match immediately. For partial matches, it returns the command only if exactly one command matches partially; ambiguous partials return `NULL`.

## Dependencies and Interactions

Uses `StrList` helpers, UI `screen_width()`, `xmalloc()`, and libparted device/disk pointer types in command callbacks.
