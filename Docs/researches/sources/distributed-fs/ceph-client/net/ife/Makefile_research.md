# sources/distributed-fs/ceph-client/net/ife/Makefile

## Purpose
The IFE Makefile wires the Inter-FE encapsulation implementation into the kernel build.

## Important APIs, types, and functions
It contains one build rule: `obj-$(CONFIG_NET_IFE) += ife.o`.

## Control flow
Kbuild expands the rule according to `CONFIG_NET_IFE`, compiling `ife.c` into built-in networking code or a loadable module when enabled.

## State and persistence
The file owns no runtime state. Its output is build-system state in the generated object/module list.

## Dependencies and integration points
It depends on `NET_IFE` from `Kconfig` and on `ife.c` as the object source.

## Risks and invariants
The object name must match the implementation file and module name described in Kconfig. Additional source files would require updating this Makefile to avoid missing symbols.

## Test signals
Kbuild with `CONFIG_NET_IFE=y` or `m` should produce `ife.o`; disabled configs should not compile the directory object.
