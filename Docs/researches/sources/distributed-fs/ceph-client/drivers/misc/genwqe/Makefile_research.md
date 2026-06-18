# sources/distributed-fs/ceph-client/drivers/misc/genwqe/Makefile

## Purpose
Build recipe for the GenWQE driver module.

## Important APIs, Types, And Functions
`obj-$(CONFIG_GENWQE) := genwqe_card.o` makes the module conditional on Kconfig. `genwqe_card-objs` composes the module from `card_base.o`, `card_dev.o`, `card_ddcb.o`, `card_sysfs.o`, `card_debugfs.o`, and `card_utils.o`.

## Control Flow
When `CONFIG_GENWQE` is enabled, Kbuild links the listed object files into one `genwqe_card` module or built-in object. `card_base.o` supplies module init/exit and PCI driver registration, while the other objects supply character device, DDCB queue, sysfs, debugfs, and utility support.

## State, Persistence, And Dependencies
No runtime state is stored here. The Makefile encodes intra-driver composition, so missing objects or renamed source files break the complete module.

## Integration Points
This file integrates with `drivers/misc` Kbuild and the `GENWQE` Kconfig symbol. The module name and object grouping must stay consistent with `MODULE_*` metadata and exported internal symbols across GenWQE source files.

## Risks
Object order can matter for initcall and symbol resolution only indirectly, but removing `card_base.o` would remove module entry points. The Makefile assumes all listed C files are present in the same directory.

## Test Signals
Run kernel build checks with `CONFIG_GENWQE=m` and `CONFIG_GENWQE=y`; verify `genwqe_card.ko` contains all expected objects and no unresolved internal GenWQE symbols.
