# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/Makefile

## Purpose
The SH3 `Makefile` selects CPU-family core objects and subtype-specific setup, serial, clock, hibernation, and pinmux objects.

## Important APIs, Types, And Functions
It always builds `ex.o`, `probe.o`, `entry.o`, and `setup-sh3.o`. It conditionally adds `swsusp.o`, subtype setup and serial files for SH7705/7706/7707/7708/7709/7710/7712/7720/7721, clock implementations through `clock-y`, and `pinmux-sh7720.o` when `CONFIG_GPIOLIB` and `CONFIG_CPU_SUBTYPE_SH7720` are enabled.

## Control Flow
Kbuild expands `obj-*` and `clock-*` variables from Kconfig symbols. Later assignments to `clock-$(...) := ...` select exactly one primary clock file for the configured subtype, then `obj-y += $(clock-y)` links it into the CPU backend.

## State And Persistence
The file has no runtime state. Its build-state effect is the linked kernel image contents.

## Dependencies And Integration Points
It integrates SH3 Kconfig choices with architecture code. SH4 reuses SH3 `entry.o`, `ex.o`, and `swsusp.o`, so changes here can affect shared low-level code availability.

## Risks
Incorrect object selection can leave a configured CPU without setup or clock support. The SH7720 clock mapping deliberately reuses `clock-sh7710.o`, which is easy to misread as an omission.

## Test Signals
Build coverage for each `CONFIG_CPU_SUBTYPE_*` choice is the primary signal. Link errors for missing `plat_*` hooks, `arch_init_clk_ops`, or serial ops indicate selection regressions.
