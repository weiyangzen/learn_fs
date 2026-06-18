# File Research: sources/block-storage/lvm2/tools/command.c

## Purpose
`command.c` builds and parses LVM2 command definitions. It turns generated macro sources such as `args.h`, `vals.h`, `lv_props.h`, `lv_types.h`, `cmds.h`, `commands.h`, and `command-lines-input.h` into runtime `struct command` records, lookup tables, command help output, and man-page-oriented usage text.

## Main Flow
`define_commands()` is the central parser. It resets stale command data on reinitialization, sorts option/value lookup arrays, then walks `_command_input`, the generated `command-lines.in` content with comments stripped.

It recognizes command lines, reusable `OO_FOO:` optional-option groups, `OO:`, `IO:`, `OP:`, `DESC:`, `AUTOTYPE:`, `FLAGS:`, `RULE:`, and `ID:` lines, plus continuations. Parsed strings are converted into option enums, value enums, LV type bitsets, LV property bitsets, and positional/option argument definitions.

## Key Behavior
- `_opt_str_to_num()` maps long option strings to `foo_ARG`, including duplicate long-option handling.
- `_val_str_to_num()` maps command-definition value names to `foo_VAL`.
- `_set_pos_def()` and `_set_opt_def()` populate `struct arg_def`.
- `_add_rule()` parses command rules for option/LV type/LV property constraints.
- `factor_common_options()` computes options common to all variants of a command.
- `print_usage()` and related helpers generate compact command help/man usage.
- `configure_command_option_values()` adjusts accepted option value types for command-specific size/extents semantics.

## Integration Notes
The file bridges generated command metadata and the runtime command-line engine. It is used both in normal LVM builds and in `MAN_PAGE_GENERATOR` builds.

## Risks
Hard-coded capacity constants, generated-file ordering assumptions, and in-place parsing make this file sensitive to changes in `command-lines.in`, `args.h`, `vals.h`, `lv_props.h`, `lv_types.h`, and `commands.h`.
