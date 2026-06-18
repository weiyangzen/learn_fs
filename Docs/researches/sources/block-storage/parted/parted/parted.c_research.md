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
