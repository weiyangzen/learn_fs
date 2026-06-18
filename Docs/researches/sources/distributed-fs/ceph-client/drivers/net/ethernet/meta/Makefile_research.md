# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Makefile

## Purpose

`meta/Makefile` connects the Meta Ethernet vendor directory to the kernel build system.

## Important APIs, Types, And Functions

The file contains one build rule: `obj-$(CONFIG_FBNIC) += fbnic/`. When `CONFIG_FBNIC` is enabled, kbuild descends into the `fbnic` subdirectory.

## Control Flow

Kbuild evaluates `CONFIG_FBNIC`; if disabled, no objects from this vendor directory are built. If enabled as built-in or module, the subdirectory Makefile decides the actual object list and module composition.

## State And Persistence

There is no runtime state. Build state is determined by the kernel `.config`.

## Dependencies And Integration Points

This Makefile depends on the `FBNIC` Kconfig option and the existence of `meta/fbnic/Makefile`. It integrates into the broader `drivers/net/ethernet` vendor build structure.

## Risks And Edge Cases

The directory is built only when `CONFIG_FBNIC` is set. Renaming the option or subdirectory without updating this line breaks driver inclusion.

## Test Signals

Build tests should verify that `CONFIG_FBNIC=m` creates the fbnic module and `CONFIG_FBNIC=n` skips the directory. No local executable tests were run for this research item.
