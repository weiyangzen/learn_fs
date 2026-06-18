# sources/distributed-fs/ceph-client/drivers/pinctrl/Makefile

## Purpose
kbuild file for pinctrl core, optional generic infrastructure, top-level drivers, and vendor subdirectories.

## APIs, Flow, And State
Always builds `core.o` and `pinctrl-utils.o`. Conditional objects include `pinmux.o`, `pinconf.o`, `pinconf-generic.o`, `pinctrl-generic.o`, and `devicetree.o`, plus many `CONFIG_PINCTRL_*` driver object mappings. `subdir-ccflags-$(CONFIG_DEBUG_PINCTRL) += -DDEBUG` enables debug diagnostics. Vendor directories are traversed through `obj-y` or config/architecture-gated rules. State is build output derived from `.config`.

## Dependencies And Integration
Integrates with `drivers/pinctrl/Kconfig`, generic pinctrl source files, and vendor subdirectory Makefiles. `CONFIG_OF` controls devicetree pinctrl support.

## Risks And Tests
Large symbol/object mapping surface can drift. Always-entered subdirectories must have clean internal Makefiles. Test minimal core, `PINMUX`, `PINCONF`, `CONFIG_OF`, representative built-in/module drivers, and `allmodconfig`.
