# sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_no.c

## Purpose

`setup_no.c` is the no-MMU m68k/uClinux architecture setup implementation. It establishes the flat memory model, collects board and U-Boot command-line data, initializes memblock and paging, and exposes no-MMU CPU information.

## Important APIs, Types, and Functions

It defines exported `memory_start` and `memory_end`, `command_line`, machine hooks `mach_sched_init`, `mach_reset`, and `mach_halt`, `setup_arch()`, `show_cpuinfo()`, and `cpuinfo_op`. CPU name and instruction timing are selected through Kconfig macros such as `CONFIG_M68328`, `CONFIG_M68VZ328`, and `CONFIG_COLDFIRE`.

## Control Flow

`setup_arch()` aligns `_ramstart` into `memory_start`, records `_ramend`, initializes `init_mm`, calls `config_BSP()` to let the board fill the command line and hooks, applies built-in boot parameters, appends U-Boot command-line/initrd data, prints CPU/board support messages, adds the RAM range to memblock, reserves kernel/ROMFS-used memory, exports the command line to generic boot state, sets PFN limits, reserves a U-Boot initrd when valid, and calls `paging_init()`.

## State and Persistence Behavior

Persistent state includes the flat memory bounds, command line, memblock reservations, PFN bounds, machine hooks, and optional initrd range. There is no MMU state and no bootinfo parser in this file.

## Dependencies and Integration Points

It depends on linker symbols `_ramstart`, `_ramend`, `_rambase`, `_stext`, `_etext`, `_sdata`, `_edata`, and `__bss_*`, board `config_BSP()`, `process_uboot_commandline()`, memblock, `paging_init()`, and generic `/proc/cpuinfo` seq support.

## Risks and Edge Cases

The flat memory assumptions are sensitive to linker symbols and ROMFS placement. U-Boot initrd is reserved only when inside `memory_end`; invalid ranges are silently ignored. Command-line concatenation depends on bounded copies and available buffer space. Platform hooks must be installed by `config_BSP()` before timers and reboot paths use them.

## Test Signals

Boot a no-MMU target with and without U-Boot initrd, confirm memory ranges in debug logs, verify `/proc/cpuinfo` clock/BogoMips calculations, and ensure board reset/halt/timer hooks are installed.
