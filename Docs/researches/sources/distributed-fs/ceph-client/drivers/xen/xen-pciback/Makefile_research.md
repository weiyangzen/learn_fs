# sources/distributed-fs/ceph-client/drivers/xen/xen-pciback/Makefile

## Purpose
This Makefile builds the Xen PCI backend driver and its component objects for either `CONFIG_XEN_PCIDEV_BACKEND` or `CONFIG_XEN_PCIDEV_STUB`.

## Important APIs, types, and functions
It is kbuild metadata, not C code. It maps both backend and stub config symbols to `xen-pciback.o`, whose object list includes `pci_stub.o`, `pciback_ops.o`, `xenbus.o`, `conf_space.o`, `conf_space_header.o`, `conf_space_capability.o`, `conf_space_quirks.o`, `vpci.o`, and `passthrough.o`.

## Control flow
Kbuild selects `xen-pciback.o` when either supported config is enabled. The comment notes that a single `CONFIG_XEN_PCI_STUB` line would not express the needed module behavior because related symbols are mutually exclusive and one may remain built-in.

## State and persistence
Only build graph state exists. Runtime behavior comes from the compiled objects.

## Dependencies and integration points
It integrates Xen PCI backend Kconfig symbols with the implementation files in `drivers/xen/xen-pciback`.

## Risks and test signals
Risks are stale object lists, config-symbol mismatch, and module/built-in selection regressions. Test signals include builds for backend-only, stub-only, built-in, module, and allmodconfig configurations.
