# sources/distributed-fs/ceph-client/drivers/gpib/nec7210/Makefile

## Purpose

This Kbuild fragment builds the NEC7210 reusable GPIB controller support object when `CONFIG_GPIB_NEC7210` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_NEC7210) += nec7210.o` compiles `nec7210.c`, which exports symbols used by NEC7210-compatible board drivers.

## Control Flow and Integration

The parent GPIB Makefile includes this fragment. Board drivers that embed `struct nec7210_priv` depend on this object being available either built-in or as a module dependency.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies

The target depends on `CONFIG_GPIB_NEC7210`, `nec7210.c`, `board.h`, and headers under `drivers/gpib/include`.

## Risks and Test Signals

If board drivers select NEC7210 helpers without this object, symbol resolution fails. Build tests should cover modular and built-in combinations of NEC7210 core and dependent boards.
