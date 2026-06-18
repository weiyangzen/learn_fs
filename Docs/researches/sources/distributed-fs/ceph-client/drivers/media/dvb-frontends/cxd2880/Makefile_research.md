# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Makefile

## Purpose
Defines the composite object list for the CXD2880 frontend module and maps it to `CONFIG_DVB_CXD2880`.

## Important APIs, Types, and Functions
`cxd2880-objs` includes common helpers, SPI device I/O, integration helpers, register I/O, tuner/demod common control, DVB-T/T2 tuning, DVB-T/T2 monitor code, generic monitor code, and `cxd2880_top.o`. `obj-$(CONFIG_DVB_CXD2880) += cxd2880.o` is the Kbuild entry point.

## Control Flow
Kbuild links the listed objects into one built-in or modular driver depending on the Kconfig tristate.

## State and Persistence
There is no runtime state. Persistent effect is build artifact composition.

## Dependencies and Integration Points
The object list is coupled to headers and exported functions across the CXD2880 directory. `cxd2880_top.o` provides DVB frontend glue that consumes lower-level control and monitor APIs.

## Risks and Edge Cases
Missing an object can produce unresolved symbols or silently remove functionality from the module. Formatting lacks spaces before continuations on two lines, but Kbuild still parses them; edits should preserve valid continuation syntax.

## Test Signals
Build `drivers/media/dvb-frontends/cxd2880/` with `CONFIG_DVB_CXD2880=m/y`, run `modinfo cxd2880`, and verify no undefined references from monitor or tuning helpers.
