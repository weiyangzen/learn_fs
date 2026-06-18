# File Research: sources/block-storage/lvm2/tools/man-generator.c

## Purpose
Standalone generator for LVM manual pages, command indexes, category indexes, argument reference pages, and command syntax overlap checks.

## Build Context
- Defines minimal stubs and macros needed to include `command.h` and `command.c` outside the full LVM runtime.
- Uses generated command metadata, option metadata, value metadata, command names, and command definitions.
- Writes troff/man output to stdout.

## Formatting Helpers
- `_print_val_man()` formats option value syntax with man markup, including special size, extent, number, PV suffix, and pipe-separated variants.
- `_print_def_man()` formats argument definitions from value bits, constants, repeat flags, and LV type restrictions.
- `_man_long_opt_name()` formats long option names, including bracketed aliases like `--[raid]syncaction`.
- `_print_man_option()` prints short/long option pairs.
- `_print_header()` emits `.TH` and macros for option formatting.
- `_print_desc_man()` cleans generated command descriptions.

## Command Man Page Generation
`_print_man()`:
- Accepts names like `lvm-lvcreate` and maps to command name.
- Emits NAME, SYNOPSIS, optional DESCRIPTION from external file, USAGE, OPTIONS, VARIABLES.
- Iterates all command variants for the requested command.
- Skips previous syntax and optionally secondary syntax.
- Uses `_print_man_usage()` to print each command form.
- Prints common command and LVM options.

`_print_man_secondary()`:
- Emits only advanced/secondary command forms.

## Usage Generation
`_print_man_usage()`:
- Handles required options, any-required option sets, required positionals, optional options, optional positionals, and implied autotypes.
- Adds alternate `--extents` when a command supports size/extents interchange.
- Prints LV type constraints for positional LV arguments when needed.
- Separates repeated syntax and common options.

## Option/Variable Sections
- `_print_man_all_options_list_string()` creates reusable `.de O_<option>` macros.
- `_print_man_all_options_list()` prints compact option summaries.
- `_print_man_all_options_desc()` prints option descriptions, filtered by command-specific `#cmdname` description sections.
- `_print_man_all_positions_desc()` prints descriptions for VG, LV, PV, tag, select, String, Size, and environment variable notes.

## Description Inclusion
`_include_description_file()`:
- Reads an external description file up to `MAX_MAN_DESC`.
- Emits it under `.SH DESCRIPTION`.
- Validates open/stat/read/allocation errors.

## Index Generation
Supports alphabetical and category index pages:
- `_get_index_cname()` reads `_meta` files and derives entry data from sibling `_des`, `_main`, or builtin command metadata.
- Reads `category = ...` and optional `conditional = yes`.
- Optional condition markers wrap conditional entries.
- `_print_alphabetical_index()` emits `lvm-index(7)`.
- `_print_category_index()` emits `lvm-categories(7)`.
- `_print_index()` builds entries and dispatches index mode.

## Static Man Page Parsing
`_get_main_index_cname()`:
- Reads `.SH NAME` from `_main` files.
- Extracts command name and description split by `\(em` or ` - `.

## Command Definition Validation
- `_compare_opt_lists()` compares required option lists, with special handling for different `--type` strings.
- `_compare_cmds()` detects repeated/ambiguous command definitions, including cases where one command’s optional option makes it overlap another.
- `_check_overlap()` compares same-name command definitions and catches options that are both required and optional in any-required groups.

## Args Reference
`_print_args_man()`:
- Emits `lvm-args(7)`.
- Lists every used long option, optional short form, value syntax, generic option description, and commands that accept it.

## CLI Modes
`main()` supports exactly one mode group:
- `--primary <command> [description-file]`
- `--secondary <command>`
- `--check`
- `--index [--with-condition-markers] file...`
- `--categories [--with-condition-markers] file...`
- `--args`

## Important Details
- `--primary` and `--secondary` may combine; `--check` cannot combine with them.
- Index/category modes validate input file existence.
- Output buffering uses a large stdout buffer sized for description content.
- Command metadata is initialized by `define_commands()` and `factor_common_options()` before generation.
