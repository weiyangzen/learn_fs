# File Research: sources/block-storage/util-linux/sys-utils/ctrlaltdel.c

## Scope

Implements `ctrlaltdel`, which reads or sets the Linux Ctrl-Alt-Del behavior.

## Public And Internal APIs Covered

- Main command-line entry point.
- `get_cad()` reads current mode.
- `set_cad()` sets hard or soft mode.

## Control Flow And Behavior

- With no positional argument, reads `_PATH_PROC_CTRL_ALT_DEL` and prints `soft` for `0`, `hard` for `1`, or `implicit hard` plus warning for unexpected values.
- With an argument, accepts `hard` or `soft`.
- Uses `reboot(LINUX_REBOOT_CMD_CAD_ON)` for hard reset behavior and `reboot(LINUX_REBOOT_CMD_CAD_OFF)` for soft behavior.

## Dependencies

- Linux `reboot()` command constants, with local definitions for CAD on/off.
- `/proc/sys/kernel/ctrl-alt-del` path from pathnames.
- util-linux path, usage, i18n, and closestream helpers.

## Risks And Invariants

- Setting behavior requires sufficient privileges for `reboot()`.
- The program does not reject extra positional arguments; it uses `argv[1]`.
- Unexpected proc values return failure after printing the inferred mode.
