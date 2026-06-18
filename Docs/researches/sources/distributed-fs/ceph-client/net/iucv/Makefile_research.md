# sources/distributed-fs/ceph-client/net/iucv/Makefile

## Purpose
Builds the IUCV networking objects based on Kconfig selections.

## Important APIs, types, and functions
The object rules are `obj-$(CONFIG_IUCV) += iucv.o` and `obj-$(CONFIG_AFIUCV) += af_iucv.o`.

## Control flow
No runtime control flow. Kbuild includes the low-level driver and AF socket layer independently according to configuration.

## State and persistence behavior
No runtime state. It influences the build graph only.

## Dependencies and integration points
Ties `CONFIG_IUCV` to `iucv.c` and `CONFIG_AFIUCV` to `af_iucv.c`. This supports AF_IUCV being built when HiperSockets are desired even if classic IUCV is unavailable.

## Risks and test signals
Risk is build skew between the two symbols, especially AF_IUCV references to `iucv_if` when classic IUCV is conditionally available. Test allmodconfig/allyesconfig on S390 and modular load/unload paths.
