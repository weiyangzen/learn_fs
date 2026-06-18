# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/Makefile

## Purpose
Connects the Google Ethernet vendor directory to the gVNIC driver subdirectory.

## APIs and Build Semantics
The only build rule is `obj-$(CONFIG_GVE) += gve/`, so the subdirectory is compiled when `CONFIG_GVE` is built-in or modular.

## Control Flow and Integration
This file is reached from the parent Ethernet driver Makefile. It delegates all object composition to `google/gve/Makefile`.

## State and Persistence
No runtime state. It persists the build graph edge from `CONFIG_GVE` to the gve driver directory.

## Dependencies, Risks, and Tests
Depends on Kbuild's directory recursion semantics. The main risk is omission from the build when Kconfig is enabled. Test with `make M=drivers/net/ethernet/google/gve` in a kernel tree or full kernel builds with `CONFIG_GVE=m/y`.
