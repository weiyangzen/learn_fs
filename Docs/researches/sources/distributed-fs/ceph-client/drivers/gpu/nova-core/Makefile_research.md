# sources/distributed-fs/ceph-client/drivers/gpu/nova-core/Makefile

## Purpose

`Makefile` connects the `CONFIG_NOVA_CORE` Kconfig symbol to the built kernel object for the Nova Core Rust GPU driver.

## Important APIs, Types, And Functions

The only build rule is `obj-$(CONFIG_NOVA_CORE) += nova_core.o`, under GPL-2.0 SPDX metadata.

## Control Flow

There is no program flow. During kbuild evaluation, `nova_core.o` is added to the object list when `NOVA_CORE` is enabled as built-in or module.

## State And Persistence Behavior

No runtime state is stored. The persistent build outcome is the presence or absence of the `nova_core` module or built-in object.

## Dependencies And Integration Points

It integrates with kbuild's Rust object handling and the `Kconfig` symbol in the same directory. The crate/module source composition is expected to be described by Rust module files and higher-level build metadata.

## Risks And Test Signals

Risks are mainly build-system drift: object name mismatch with module declarations, missing generated binding inputs, or absent inclusion from a parent Makefile. Test by building with `CONFIG_NOVA_CORE=m` and `y`, confirming `nova_core.o` is produced, and checking that disabling the symbol omits it.
