# File Research: sources/block-storage/lvm2/tools/command.h

## Purpose
`command.h` defines the core data model for LVM2 command definitions, command names, option/value descriptors, positional arguments, command rules, and command parsing/help state.

## Main Types
It defines command function pointers, `struct command_name`, `struct command_name_args`, `struct command`, `struct arg_def`, `struct opt_arg`, `struct pos_arg`, `struct cmd_rule`, `struct opt_name`, `struct val_name`, `struct lv_prop`, and `struct lv_type`.

## Key Contracts
The header sets fixed array limits for required/optional options, required/optional positional args, ignored options, and command rules. It also defines command-definition flags such as `CMD_FLAG_ANY_REQUIRED_OPT`, `CMD_FLAG_SECONDARY_SYNTAX`, `CMD_FLAG_PREVIOUS_SYNTAX`, and `CMD_FLAG_PARSE_ERROR`.

## Integration Notes
This is the shared ABI between generated command metadata parsing, command-line processing, help/man generation, and concrete command handlers.
