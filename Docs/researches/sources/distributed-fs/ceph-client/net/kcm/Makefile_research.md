# sources/distributed-fs/ceph-client/net/kcm/Makefile

## Purpose
Builds the KCM socket implementation.

## Important APIs, types, and functions
`obj-$(CONFIG_AF_KCM) += kcm.o` declares the composite KCM object; `kcm-y := kcmsock.o kcmproc.o` links the socket implementation and procfs reporting.

## Control flow
No runtime control flow. Kbuild composes the module or built-in object from both source files when AF_KCM is enabled.

## State and persistence behavior
No runtime state. It affects object composition only.

## Dependencies and integration points
Connects Kconfig to `kcmsock.c` and `kcmproc.c`, so proc support is compiled into the KCM object and conditionally active inside `kcmproc.c` under `CONFIG_PROC_FS`.

## Risks and test signals
Risk is missing proc symbols or unresolved references if object composition changes. Test `CONFIG_AF_KCM=m/y` with `CONFIG_PROC_FS` on and off.
