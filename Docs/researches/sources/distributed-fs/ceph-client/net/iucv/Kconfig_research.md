# sources/distributed-fs/ceph-client/net/iucv/Kconfig

## Purpose
Defines build-time configuration for S390 IUCV support and AF_IUCV sockets. It gates low-level z/VM Inter-User Communication Vehicle support and the socket-facing AF_IUCV protocol including HiperSockets transport.

## Important APIs, types, and functions
Configuration symbols are `CONFIG_IUCV` and `CONFIG_AFIUCV`. `IUCV` depends on `S390`, defaults to built-in on S390, and prompts for z/VM-only IUCV support. `AFIUCV` depends on `S390`, defaults to module when `QETH_L3` or `IUCV` is enabled, and enables AF_IUCV socket applications.

## Control flow
There is no runtime control flow. Kconfig controls whether `iucv.o` and/or `af_iucv.o` can be built by the Makefile and whether AF_IUCV may use classic IUCV, HiperSockets, or both at runtime.

## State and persistence behavior
State is kernel build configuration only. It affects compiled objects and module availability, not runtime persistence.

## Dependencies and integration points
Integrates with S390 architecture support, z/VM, QETH L3 HiperSockets, and the `net/iucv/Makefile`. Enabling `AFIUCV` without runtime z/VM IUCV still allows HiperSockets-oriented behavior if devices exist.

## Risks and test signals
Risks are mostly configuration expectations: AF_IUCV may be available as a module when only QETH_L3 is enabled, while classic IUCV operations require z/VM and `CONFIG_IUCV`. Test build matrices for S390 built-in/module combinations, non-S390 exclusion, and runtime module loading with and without z/VM.
