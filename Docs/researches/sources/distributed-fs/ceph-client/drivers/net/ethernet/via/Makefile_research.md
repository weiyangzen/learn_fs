# sources/distributed-fs/ceph-client/drivers/net/ethernet/via/Makefile

## Purpose
This Makefile maps VIA Ethernet Kconfig symbols to their driver objects.

## Important APIs, types, and functions
The build rules are `obj-$(CONFIG_VIA_RHINE) += via-rhine.o` and `obj-$(CONFIG_VIA_VELOCITY) += via-velocity.o`. There are no runtime APIs.

## Control flow and integration
Kbuild includes each object when its Kconfig symbol is built-in or modular. Module names are `via-rhine` and `via-velocity`, matching the Kconfig help text and module metadata in the source files.

## State and persistence behavior
No runtime state exists. The file contributes build graph state only.

## Dependencies and integration points
It depends on the neighboring source files and the parent Ethernet Makefile including this directory.

## Risks and edge cases
The file is intentionally simple. Rename drift between Kconfig symbols, object names, and source files is the primary risk.

## Test signals
Build with `CONFIG_VIA_RHINE=m` and `CONFIG_VIA_VELOCITY=m` and confirm both `.ko` files are produced; repeat with built-in selections for link coverage.
