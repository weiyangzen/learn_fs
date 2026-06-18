# Group Research: group_1466_parted_sources_block_storage_parted_parted_parted_c_sources_block_s_df31e3806dba

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/parted`, which is included in subset A. Each listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/parted.c -->
# File Research: sources/block-storage/parted/parted/parted.c

## Purpose

`parted.c` is the main GNU Parted frontend. It wires command-line options, interactive/non-interactive command registration, libparted device/disk operations, partition table mutation commands, output formatting, progress timers, and process lifecycle cleanup.

## Main Responsibilities

- Defines global frontend options:
  - script/fix mode,
  - human/machine/JSON output mode,
  - requested alignment policy,
  - pretend-input-tty behavior,
  - disk modification tracking.
- Implements user-visible Parted commands:
  - `help`
  - `mklabel` / `mktable`
  - `mkpart`
  - `name`
  - `type`
  - `print`
  - `quit`
  - `rescue`
  - removed `resize`
  - `resizepart`
  - `rm`
  - `select`
  - `disk_set`
  - `disk_toggle`
  - `set`
  - `toggle`
  - `unit`
  - `version`
  - `align-check`
- Initializes internationalization, UI, commands, dynamically generated help strings, selected device, and libparted timer.
- Selects interactive mode unless commands or script mode are provided.
- Destroys the active disk/device/timer/commands/messages and prints post-write warnings on exit.

## Important Functions

- `main()` sets program name, initializes Parted, dispatches to `non_interactive_mode()` or `interactive_mode()`, then returns inverted command status.
- `_init()` initializes NLS, UI, command/help state, options, readline, selected device, and timer state.
- `_parse_options()` handles `--help`, `--list`, `--machine`, `--json`, `--script`, `--fix`, `--version`, `--align`, and `--pretend-input-tty`.
- `_choose_device()` selects the command-line device or probes for the first available device, then opens it.
- `_done()` destroys disk state, warns about dirty boot records/fstab, closes the device, and tears down UI/commands/messages.
- `_init_messages()` builds translated comma-separated help strings for flags, disk flags, units, disk labels, and filesystem types.
- `_init_commands()` creates and registers every command and its help text.
- `_timer_handler()` renders human-mode progress updates for long libparted operations.
- `do_mklabel()` creates and commits a fresh disk label after busy/loss warnings.
- `do_mkpart()` creates a partition, parses optional name/type/filesystem/start/end, applies IEC end adjustment, snaps to nearby boundaries, intersects user and device alignment constraints, handles fallback placement warnings, sets flags/system, and commits.
- `do_resizepart()` changes only the partition end, preserves busy-partition end input across warnings, applies IEC adjustment, warns on shrink, and commits.
- `do_rm()`, `do_set()`, `do_disk_set()`, `do_name()`, and `do_type()` mutate partition or disk metadata and commit.
- `do_print()` implements `print`, `print devices`, `print free`, `print list/all`, and single-partition printing paths across human, machine, and JSON modes.
- `_print_disk_info()` emits disk metadata, sector sizes, label, UUID, max partitions, and flags.
- `_print_list()` probes all devices and prints each partition table.
- `do_rescue()`, `_rescue_pass()`, and `_rescue_add_partition()` scan near user-supplied start/end ranges for filesystem signatures and optionally add recovered partitions.
- `partition_align_check()` checks partition start against minimal or optimum device alignment and can return an explanatory math string.
- `_adjust_end_if_iec()` implements the IEC-unit end-sector convention: with KiB/MiB/GiB/TiB input or default IEC units, non-1-sector partitions end one sector before the parsed boundary.

## Output Behavior

Human output uses `StrList` and `Table` to render aligned partition tables. Machine output emits colon-separated records and escapes `:` and `\`. JSON output uses `jsonwrt` and conditionally includes disk UUIDs, partition UUIDs, type IDs/UUIDs, names, filesystems, and flags.

## Dependencies and Interactions

- Depends heavily on libparted APIs for `PedDevice`, `PedDisk`, `PedPartition`, geometry, constraints, flags, probing, and commits.
- Uses `ui.c` for input parsing, prompts, exception behavior, and interactive/non-interactive execution.
- Uses `command.c` infrastructure through `command_create()`, `command_register()`, `command_run()`, and lookup helpers.
- Uses `strlist.c` for help strings and table rows.
- Uses `table.c` for human-mode table rendering.
- Uses libuuid for disk/partition type UUID display and parsing.
- Uses gnulib-style helpers such as `argmatch`, `xalloc`, `closeout`, and `version-etc`.

## Notable Edge Cases

- In script mode, some warnings become fatal errors or unhandled exceptions rather than prompts.
- Disk modifications on regular files do not set `disk_is_modified`.
- `mkpart` first tries strict user/device constraints, then falls back to any constraint and prompts or fails if the result differs from requested geometry.
- `mkpart` avoids the undocumented partition-name path for DVH primary partitions.
- `resize` remains registered but only reports that it was removed in Parted 3.0.
- `print devices` temporarily probes all devices, then restores the originally selected device by name.
- `partition_print()` is a stub returning success, so `print N` currently does not emit per-partition detail in this file.
- Machine/JSON end positions use byte formatting of `(end + 1) * sector_size - 1`, while starts and sizes use unit formatting.
- `_done_messages()` frees most generated help strings but omits `disk_flag_msg`, which is allocated in `_init_messages()`.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/parted.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/strlist.c -->
# File Research: sources/block-storage/parted/parted/strlist.c

## Purpose

`strlist.c` implements Parted’s linked-list string utility used for command aliases, completions, prompts, help text, wrapped output, translated option matching, and table row construction. It stores strings internally as `wchar_t` when NLS is enabled and as `char` otherwise.

## Main Responsibilities

- Allocate, append, insert, join, duplicate, and destroy `StrList` nodes.
- Convert between gettext/catalog strings and internal wide-character strings.
- Convert list nodes or whole lists back to multibyte strings.
- Print lists directly or wrapped to a target line width.
- Match input tokens against valid possibilities with full or prefix matching.
- Support case-insensitive command/option matching, including translated aliases.

## Important Functions

- `gettext_to_wchar()` converts multibyte gettext strings to internal wide strings under NLS; without NLS it duplicates bytes directly.
- `wchar_to_str()` converts internal strings back to multibyte strings, optionally truncating by character count.
- `str_list_create()` and `str_list_create_unique()` build varargs lists terminated by `NULL`.
- `str_list_append()` appends a translated string.
- `str_list_append_unique()` appends only if no case-insensitive equivalent exists.
- `str_list_insert()` prepends by creating a single-node list and joining it to the old list.
- `str_list_join()` links two lists without copying.
- `str_list_duplicate()` and `str_list_duplicate_node()` deep-copy nodes and strings.
- `str_list_convert()` concatenates every non-null node into a newly allocated `char *`.
- `str_list_print()` prints each node in sequence.
- `str_list_print_wrap()` wraps text at break points based on screen width, offset, and indent.
- `str_list_match_node()` returns full/partial/no match for one node.
- `str_list_match_any()` returns the best match status across a list.
- `str_list_match()` returns an exact match immediately, a single partial match if unambiguous, or `NULL` for no/ambiguous match.
- `str_list_length()` counts nodes.

## Data Model

Each `StrList` node owns its `str` allocation and its `next` link. Destruction is recursive for whole lists. Several APIs transfer or share list ownership directly: `str_list_join()` reuses existing list nodes rather than copying.

## NLS Behavior

With `ENABLE_NLS`, list strings are wide characters and matching uses `wcscasecmp()` / `wcsncasecmp()`. Printing converts back through `wcrtomb()`. Without NLS, `wchar_t` is macro-mapped to `char`, and wrappers use normal byte-string functions.

## Wrapping Behavior

`str_list_print_wrap()` treats spaces as removable whitespace and explicit `\n` as forced breaks. It searches backward for break points using `is_break_point()`, which is locale-aware under NLS. The comments explicitly discuss Japanese text where word spaces may not exist.

## Dependencies and Interactions

- Used by `command.c` for command names, summaries, help text, and matching.
- Used by `ui.c` for command-line token lists, completion possibilities, prompts, and exception choices.
- Used by `parted.c` to construct generated help strings and human output table rows.
- Used by `table.c` through direct access to `StrList->str`.

## Notable Edge Cases

- `str_list_create(NULL, ...)` creates a single node with a null string because it calls `str_list_append(NULL, first)` before checking `first`.
- `str_list_match()` treats multiple partial matches as ambiguous and returns `NULL`.
- Conversion errors in NLS paths print an error and terminate the process with `exit(EXIT_FAILURE)`.
- `str_list_destroy()` is recursive, so extremely long lists could consume call stack, though normal Parted lists are small.
- `str_list_convert()` uses `realloc()` directly instead of `xrealloc()` and does not explicitly check for allocation failure.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/strlist.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/strlist.h -->
# File Research: sources/block-storage/parted/parted/strlist.h

## Purpose

`strlist.h` declares Parted’s `StrList` linked-list string abstraction and its construction, conversion, printing, matching, and length APIs.

## Contents

- Includes `<wchar.h>`.
- If NLS is disabled:
  - defines `L_(str)` as `str`,
  - undefines and remaps `wchar_t` to `char`.
- Defines `typedef struct _StrList StrList`.
- Defines `struct _StrList` with:
  - `StrList *next`
  - `const wchar_t *str`
- Declares external charset/language variables:
  - `language`
  - `gettext_charset`
  - `term_charset`

## Declared API

- Creation:
  - `str_list_create()`
  - `str_list_create_unique()`
- Destruction:
  - `str_list_destroy()`
  - `str_list_destroy_node()`
- Copying and composition:
  - `str_list_duplicate()`
  - `str_list_duplicate_node()`
  - `str_list_insert()`
  - `str_list_append()`
  - `str_list_append_unique()`
  - `str_list_join()`
- Conversion:
  - `str_list_convert()`
  - `str_list_convert_node()`
- Output:
  - `str_list_print()`
  - `str_list_print_wrap()`
- Matching:
  - `str_list_match_any()`
  - `str_list_match_node()`
  - `str_list_match()`
- Introspection:
  - `str_list_length()`

## Dependencies and Role

This header is a shared utility contract for `parted.c`, `ui.c`, `command.c`, and `table.c`. It intentionally exposes the node layout, allowing `table.c` to read `list->str` directly.

## Notable Details

The NLS-disabled `wchar_t` remapping is invasive but lets the same implementation and table renderer compile against byte strings. Callers must treat returned `char *` conversions as owned allocations.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/strlist.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/table.c -->
# File Research: sources/block-storage/parted/parted/table.c

## Purpose

`table.c` implements a small wide-character table renderer for Parted’s human-readable `print` output. It accepts rows, calculates display widths, pads columns, strips trailing blanks, and returns one rendered string.

## Main Responsibilities

- Own an opaque table structure containing row strings and computed column widths.
- Add rows either as raw `wchar_t **` arrays or from `StrList` rows.
- Compute column widths using display width rather than byte length when NLS is enabled.
- Render all rows with two-space column delimiters and newline row suffixes.

## Data Model

The private `Table` struct contains:

- `ncols`: fixed column count.
- `nrows`: current row count.
- `rows`: array of rows, each row an array of owned `wchar_t *` cells.
- `widths`: computed display width per column.

## Important Functions

- `table_new()` allocates an empty table with a fixed column count.
- `table_destroy()` frees every cell, row array, row list, width array, and table object.
- `table_calc_column_widths()` recomputes maximum width per column after rows change.
- `table_add_row()` appends a caller-supplied row and transfers ownership of the row and cells to the table.
- `table_add_row_from_strlist()` duplicates every `StrList` cell into a new row and adds it to the table.
- `table_render_row()` appends one padded row to the accumulating rendered output.
- `table_render_rows()` renders all rows.
- `table_render()` returns a newly allocated rendered `wchar_t *`.

## Rendering Behavior

Columns are left-aligned. Widths are calculated with `wcswidth(..., MAX_WIDTH)` where available, with a hard maximum width of 512. Cells are separated by two spaces. After each row is appended, trailing blanks are removed before the newline is added.

## Dependencies and Interactions

- Used by `parted.c` human-mode `do_print()` to render partition tables.
- Uses `StrList` as a row source.
- Uses `xmalloc()`, `xrealloc()`, and `xalloc_die()` for allocation handling.
- Under non-NLS builds, wide-character operations are macro-mapped to byte-string equivalents.

## Notable Edge Cases

- `table_new()` asserts `ncols >= 0`, but `table_destroy()` asserts `ncols > 0`; zero-column tables cannot be safely destroyed through the normal path.
- `table_add_row_from_strlist()` allocates based on `str_list_length(list)` but does not verify that the list length matches `t->ncols`.
- `table_add_row()` recalculates all column widths after every appended row.
- The public comment in `table.h` suggests ownership of `list`, but this implementation duplicates `StrList` contents and does not store or free the list itself.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/table.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/table.h -->
# File Research: sources/block-storage/parted/parted/table.h

## Purpose

`table.h` declares Parted’s opaque table rendering API used to format human-readable partition tables.

## Contents

- Includes wide-character and standard headers.
- Includes `strlist.h`.
- If NLS is disabled, remaps `wchar_t` to `char`.
- Declares `typedef void Table;` as an opaque public handle.

## Declared API

- `table_new(int ncols)` creates a table with a fixed number of columns.
- `table_destroy(Table *t)` frees the table and owned row/cell memory.
- `table_add_row(Table *t, wchar_t **row)` appends a raw row; implementation takes ownership of the row.
- `table_add_row_from_strlist(Table *t, StrList *list)` appends a row derived from a string list.
- `table_render(Table *t)` returns the rendered wide-character string, owned by the caller.

## Dependencies and Role

This header is consumed by `parted.c` for human `print` output. It hides the actual `Table` struct layout from callers.

## Notable Details

The header comment says callers must not free either `row` or `list`, but the implementation only takes ownership of raw rows passed to `table_add_row()`. `table_add_row_from_strlist()` duplicates the list strings; callers in this tree destroy the original `StrList` after adding.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/table.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/ui.c -->
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

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/ui.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/parted/parted/ui.h -->
# File Research: sources/block-storage/parted/parted/ui.h

## Purpose

`ui.h` declares the interface between Parted’s command implementations and the UI/input layer implemented in `ui.c`.

## Contents

- Includes `strlist.h`.
- Defines `enum AlignmentType`:
  - `PA_MINIMUM = 1`
  - `PA_OPTIMUM`
- Declares `prog_name`.
- Declares UI lifecycle functions:
  - `init_ui()`
  - `init_readline()`
  - `done_ui()`
- Declares execution loops:
  - `non_interactive_mode()`
  - `interactive_mode()`
- Declares terminal helpers:
  - `screen_width()`
  - `wipe_line()`
- Declares command-line queue and parser helpers:
  - push/pop/peek/flush/count words,
  - prompt for words,
  - parse words, integers, sectors, state, devices, disks, partitions, filesystem types, disk types, disk flags, partition flags, partition types, exception options, units, and alignment type.
- Declares:
  - `help_msg()` as noreturn,
  - `print_using_dev()`,
  - frontend globals from `parted.c`,
  - help-printing functions from `parted.c`.

## Role in the Program

`parted.c` command handlers use these declarations to request typed command arguments without knowing whether the input came from argv, script defaults, or interactive prompts. The command loops declared here are the execution entry points used by `main()`.

## Notable Details

- The header references libparted types such as `PedDevice`, `PedDisk`, `PedPartition`, `PedGeometry`, `PedSector`, `PedUnit`, and `PedExceptionOption`, relying on includers to have the appropriate libparted declarations available.
- `command_line_get_disk()` is annotated nonnull for its second parameter.
- `command_line_is_sector()` is declared here but was not implemented in the read `ui.c`.
- The header exposes `opt_script_mode`, `opt_fix_mode`, and `pretend_input_tty` as globals owned by `parted.c`.

<!-- END FILE RESEARCH: sources/block-storage/parted/parted/ui.h -->