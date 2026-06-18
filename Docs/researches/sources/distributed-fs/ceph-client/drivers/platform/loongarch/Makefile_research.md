<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/loongarch/Makefile

## Purpose

This Makefile links the Loongson laptop ACPI platform driver when configured.

## Important APIs, Types, And Functions

It maps `CONFIG_LOONGSON_LAPTOP` to `loongson-laptop.o`.

## Control Flow

Kbuild includes the object as built-in or module according to Kconfig.

## State And Persistence

No runtime state is defined here.

## Dependencies And Integration Points

The file connects the LoongArch platform Kconfig symbol to `loongson-laptop.c`.

## Risks

No special local risks beyond object-symbol consistency.

## Test Signals

Build with `CONFIG_LOONGSON_LAPTOP=y`, `m`, and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/loongarch/Makefile -->
