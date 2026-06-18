# File Research: sources/block-storage/parted/parted/ui.c

## Purpose

`ui.c` implements Parted’s user interaction layer: readline integration, command-line token buffering, prompts, validation/parsing helpers, exception handling, signal handling, and the interactive/non-interactive command execution loops.

## Main Responsibilities

- Maintain a global `command_line` word queue used by both script and interactive modes.
- Parse input lines into words, preserving quoted strings and supporting single-word prompts for partition names.
- Prompt for missing arguments with defaults and completion possibilities.
- Validate and convert user input into libparted objects and enum values.
- Install libparted exception handler behavior.
- Provide readline completion and command history when available.
- Handle `SIGINT`, `SIGSEGV`, `SIGFPE`, and `SIGILL`.
- Initialize and destroy common option lists for exception options, on/off state, alignment type, filesystem types, and disk types.
- Run interactive and non-interactive command loops.

## Important Functions

- `screen_width()` returns terminal width via termcap/readline or defaults to 80; script and pretend-tty modes return a very wide value to avoid wrapping.
- `wipe_line()` clears a progress/prompt line in non-script mode.
- `_readline()` reads a line either through GNU Readline or plain `fgets()`.
- `command_line_push_line()` tokenizes a line into the global command queue, handling quotes, escaped characters inside quotes, multi-word mode, and single-word mode.
- `command_line_push_word()`, `command_line_pop_word()`, `command_line_peek_word()`, `command_line_flush()`, and `command_line_get_word_count()` manage queued tokens.
- `_construct_prompt()` builds prompts with possible choices and defaults.
- `command_line_prompt_words()` prompts or supplies defaults in script mode.
- `command_line_get_word()` pops/validates a token against a `StrList` of possibilities, supporting exact and unambiguous prefix matches.
- `command_line_get_integer()` parses bounded decimal integers.
- `command_line_get_sector()` parses sector/unit expressions with `ped_unit_parse()` and optionally returns raw input text.
- `command_line_get_state()` parses translated `on`/`off`.
- `command_line_get_device()` resolves a device path through `ped_device_get()`.
- `command_line_get_disk()` switches a disk to a newly selected device.
- `command_line_get_partition()` parses a partition number and resolves it on a disk.
- `command_line_get_fs_type()` and `command_line_get_disk_type()` resolve filesystem and disk label names.
- `command_line_get_disk_flag()` and `command_line_get_part_flag()` build available flag option lists dynamically.
- `command_line_get_part_type()` offers only currently creatable primary/extended/logical types.
- `command_line_get_ex_opt()` maps user-selected exception options back to `PedExceptionOption`.
- `command_line_get_align_type()` parses `minimal` or `optimal`.
- `command_line_get_unit()` parses Parted unit names.
- `init_ui()` initializes option lists, installs exception and signal handlers.
- `done_ui()` clears handlers and destroys global option lists.
- `help_msg()` prints usage, options, command summaries, and exits.
- `interactive_mode()` displays the banner, repeatedly prompts for commands, runs them, and resets disk state after failed commands.
- `non_interactive_mode()` loads all argv words into the command queue and executes registered non-interactive commands in sequence.

## Exception and Signal Behavior

`exception_handler()` prints wrapped exception text. If there is only one possible option, it returns it directly. In script mode with `--fix`, it chooses `PED_EXCEPTION_FIX` when available. In script mode or non-tty input without pretend-tty, it returns `PED_EXCEPTION_UNHANDLED`; otherwise it prompts the user.

`SIGINT` sets `got_ctrl_c` and jumps out of readline state. Fatal signals print a bug-report message and command history where readline is available, then abort.

## Dependencies and Interactions

- Uses `command.c` API for command lookup and execution.
- Uses `StrList` for prompts, completions, matching, and wrapped text.
- Uses libparted for devices, disks, units, partitions, filesystem types, disk types, flags, and exceptions.
- Uses global frontend options declared in `parted.c`: `opt_script_mode`, `opt_fix_mode`, and `pretend_input_tty`.
- Uses `print_options_help()` and `print_commands_help()` from `parted.c`.

## Notable Edge Cases

- `command_line_push_line()` limits individual parsed words to 255 characters.
- Single-word mode treats an empty quoted string as a valid word, allowing empty partition names in script mode.
- Invalid tokens flush the queued command line; in script mode invalid input returns failure rather than reprompting.
- `command_line_get_sector()` preserves exact defaults if formatted default text is accepted, avoiding rounded default values.
- `command_line_get_disk()` asserts `*value` is non-null despite accepting `PedDisk **`; callers must satisfy that precondition.
- `ex_opt_str` is initialized and destroyed but not used by the rest of this file.
- `ui.h` declares `command_line_is_sector()`, but no implementation appears in this file.
- In `command_line_get_ex_opt()`, `options_strlist` is not destroyed if `command_line_get_word()` returns `NULL`.
