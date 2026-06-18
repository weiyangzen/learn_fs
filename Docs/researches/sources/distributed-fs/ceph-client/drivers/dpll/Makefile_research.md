# sources/distributed-fs/ceph-client/drivers/dpll/Makefile

## Purpose

This Makefile builds the generic DPLL subsystem objects and descends into the ZL3073x provider directory when enabled. It is the build glue connecting `CONFIG_DPLL` to the DPLL core, generated netlink family, and netlink operation implementation.

## Important Targets

`obj-$(CONFIG_DPLL) += dpll.o` builds the composite DPLL module/built-in object. `dpll-y` includes `dpll_core.o`, `dpll_netlink.o`, and `dpll_nl.o`; the last file is typically generated from the DPLL generic-netlink spec. `obj-$(CONFIG_ZL3073X) += zl3073x/` includes the vendor provider subtree independently of the core object's internal source list.

## Control Flow and Integration

When `CONFIG_DPLL=y`, kbuild links the three generic objects into `dpll.o`. `dpll_core.o` provides kernel registration and object lifetime APIs, `dpll_netlink.o` provides user-space netlink operations and notifications, and `dpll_nl.o` supplies generic-netlink family definitions. Provider drivers rely on the exported symbols from the composite object.

## State, Risks, and Test Signals

The Makefile has no runtime state. Build risks are mostly dependency-related: generated `dpll_nl.o` must be available in the kernel build, and provider configs should ensure the generic core is built before provider code references exported DPLL symbols. Test signals are successful `CONFIG_DPLL=y/m` builds, successful builds with `CONFIG_ZL3073X`, and modpost verification of exported DPLL symbols.
