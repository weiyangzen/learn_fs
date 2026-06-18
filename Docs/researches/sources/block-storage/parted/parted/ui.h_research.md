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
