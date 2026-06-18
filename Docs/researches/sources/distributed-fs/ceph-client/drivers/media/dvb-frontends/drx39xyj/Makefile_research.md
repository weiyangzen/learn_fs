# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/Makefile

## Purpose
This Makefile wires the DRX39xyj frontend into the kernel media build.

## Important APIs, Types, and Functions
`drx39xyj-objs := drxj.o` declares the module object list. `obj-$(CONFIG_DVB_DRX39XYJ) += drx39xyj.o` connects the object to the Kconfig symbol. `ccflags-y += -I$(srctree)/drivers/media/tuners/` adds the tuner include directory for local compilation.

## Control Flow
When `CONFIG_DVB_DRX39XYJ` is built in or modular, kbuild compiles `drxj.o` and links it into `drx39xyj.o`. The additional include path is active for files in this directory.

## State and Persistence
This file affects build graph state only and has no runtime storage.

## Dependencies and Integration Points
It depends on the local `Kconfig` symbol and on a `drxj.c` implementation file in the same directory. It integrates with tuner headers through the extra include path.

## Risks and Edge Cases
The module object is a wrapper around `drxj.o`; if future source files are added but not listed, they will not be linked. The explicit tuner include path can hide missing local includes if a file accidentally relies on tuner-private headers.

## Test Signals
Run kernel/module builds with `CONFIG_DVB_DRX39XYJ=m` and `=y`, confirm `drx39xyj.o` links, and verify no include path regressions when tuner headers move.
