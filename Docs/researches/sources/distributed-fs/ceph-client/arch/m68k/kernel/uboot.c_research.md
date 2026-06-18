# sources/distributed-fs/ceph-client/arch/m68k/kernel/uboot.c

## Purpose

`uboot.c` extracts m68k U-Boot-passed command-line and initrd information from the initial stack and appends it to the kernel command-line buffer.

## Important APIs, Types, and Functions

The internal parser is `parse_uboot_commandline(char *commandp, int size)`. The exported init helper is `process_uboot_commandline(char *commandp, int size)`. It references external `_init_sp` and, when initrd support is enabled, writes `initrd_start`, `initrd_end`, and `ROOT_DEV`.

## Control Flow

`process_uboot_commandline()` finds the current end of the command buffer with `strnlen()`, appends one space when room remains, then calls `parse_uboot_commandline()` on the remaining buffer. The parser interprets `_init_sp` according to U-Boot's call convention, copies the command string if start/end pointers are nonzero, and records initrd bounds plus `Root_RAM0` when the initrd start/end pair is valid.

## State and Persistence Behavior

The file mutates the provided command buffer and global initrd/root-device state. It does not allocate memory. The parsed values persist into setup and initrd reservation.

## Dependencies and Integration Points

It depends on early assembly preserving `_init_sp`, U-Boot argument layout, setup code calling `process_uboot_commandline()`, and initrd/root device globals. Both MMU and no-MMU setup paths call it.

## Risks and Edge Cases

The parser trusts stack pointers supplied by firmware and assumes the referenced memory is still unmodified. `process_uboot_commandline()` writes `commandp[len - 1] = 0`; callers must pass a nonzero remaining size. Invalid initrd ranges are partially screened by start/end ordering here and by setup memory-bound checks later.

## Test Signals

Boot through U-Boot with command line only, initrd only, both, and empty arguments. Verify final `boot_command_line`, initrd log range, root device, and no buffer overrun when the command line is near maximum length.
