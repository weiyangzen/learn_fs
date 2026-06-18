# sources/distributed-fs/ceph-client/drivers/infiniband/hw/efa/Makefile

## Purpose

`Makefile` wires the EFA driver into Kbuild. It declares the composite `efa` object and the source objects that form the module or built-in driver.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_INFINIBAND_EFA) += efa.o`: builds the driver only when the Kconfig symbol is enabled.
- `efa-y := efa_com_cmd.o efa_com.o efa_main.o efa_verbs.o`: lists the communication command wrappers, admin queue core, PCI/main driver, and verbs implementation objects.

## Control Flow

Kbuild evaluates the `CONFIG_INFINIBAND_EFA` tristate. For `m`, the listed objects are linked into `efa.ko`; for `y`, they are linked into the kernel image; for `n`, nothing in this directory is built.

## State and Persistence Behavior

The file has no runtime state. It persists build composition and therefore affects which symbols and init/exit paths are present in the final kernel/module.

## Dependencies and Integration Points

It depends on the corresponding `Kconfig` symbol and on the source files named in `efa-y`. Header-only files in this subset are included transitively by those objects rather than listed here.

## Risks and Edge Cases

- Adding a new EFA source file without updating `efa-y` can leave code unbuilt.
- Renaming generated admin command or communication files requires synchronized Makefile updates.
- Object order is normally not significant here, but init/exit symbol availability still depends on all objects being linked into the composite.

## Test Signals

Run kernel/module builds with EFA enabled, inspect that `efa_com_cmd.o`, `efa_com.o`, `efa_main.o`, and `efa_verbs.o` are linked, and confirm no stale object names remain after file moves.
