# sources/distributed-fs/ceph-client/drivers/infiniband/hw/qedr/Makefile

## Purpose
`Makefile` maps the `INFINIBAND_QEDR` kernel config symbol to the QEDR object and lists the translation units that compose the driver.

## Important APIs, Types, And Functions
It declares `obj-$(CONFIG_INFINIBAND_QEDR) := qedr.o` and builds `qedr-y` from `main.o`, `verbs.o`, `qedr_roce_cm.o`, and `qedr_iw_cm.o`.

## Control Flow
There is no runtime control flow. Kbuild includes the listed objects into the composite `qedr.o` when the config symbol is enabled. This means the core registration/lifecycle code, generic verbs implementation, RoCE GSI connection-management path, and iWARP CM path are always compiled together for QEDR.

## State And Persistence Behavior
No runtime state exists. The file affects build graph state only.

## Dependencies And Integration Points
The file integrates with the kernel Kbuild system and the `Kconfig` symbol in the same directory. It assumes the object names correspond to local source files and that exported symbols between them are resolved inside the composite module.

## Risks And Test Signals
The main risks are omitting a required object or adding an object without matching source, causing unresolved symbols or missing operation implementations. Test signals are clean `M=drivers/infiniband/hw/qedr` builds and link-time coverage of symbols referenced from `main.c` device ops, especially verbs in `verbs.o` and CM callbacks in the two CM objects.
