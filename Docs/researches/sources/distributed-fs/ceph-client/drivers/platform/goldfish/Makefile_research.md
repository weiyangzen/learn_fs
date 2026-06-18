<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/goldfish/Makefile

## Purpose

This Makefile builds the Goldfish QEMU pipe platform driver object when configured.

## Important APIs, Types, And Functions

`obj-$(CONFIG_GOLDFISH_PIPE) += goldfish_pipe.o` is the only build mapping.

## Control Flow

Kbuild links `goldfish_pipe.o` as built-in or module according to `CONFIG_GOLDFISH_PIPE`.

## State And Persistence

There is no runtime state in this file.

## Dependencies And Integration Points

It integrates the Kconfig symbol with the `goldfish_pipe.c` source file.

## Risks

No local risks beyond keeping the object name aligned with the source file and Kconfig symbol.

## Test Signals

Build `CONFIG_GOLDFISH_PIPE=y`, `m`, and disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/goldfish/Makefile -->
