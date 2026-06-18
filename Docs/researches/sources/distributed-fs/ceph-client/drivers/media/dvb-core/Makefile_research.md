# sources/distributed-fs/ceph-client/drivers/media/dvb-core/Makefile

## Purpose
This Makefile composes the `dvb-core` object from core DVB subsystem sources and optional DVB network and mmap support objects.

## Important APIs, Types, and Functions
The key Kbuild variables are `dvb-net-$(CONFIG_DVB_NET)`, `dvb-vb2-$(CONFIG_DVB_MMAP)`, `dvb-core-objs`, and `obj-$(CONFIG_DVB_CORE)`. Core objects include `dvbdev.o`, `dmxdev.o`, `dvb_demux.o`, `dvb_ca_en50221.o`, `dvb_frontend.o`, and `dvb_ringbuffer.o`, with `dvb_net.o` and `dvb_vb2.o` added conditionally.

## Control Flow
Kbuild evaluates `CONFIG_DVB_NET` and `CONFIG_DVB_MMAP` to populate optional object lists, then links all selected objects into `dvb-core.o` when `CONFIG_DVB_CORE` is enabled. If `DVB_CORE` is modular, this composition becomes the DVB core module.

## State and Persistence
There is no runtime state. The persistent effect is build artifact composition based on `.config` selections.

## Dependencies and Integration Points
The file is coupled to symbols defined in `drivers/media/dvb-core/Kconfig` and source files in the same directory. `dmxdev.o` is always part of DVB core, while mmap support is separated into `dvb_vb2.o` and only built when `CONFIG_DVB_MMAP` is selected.

## Risks and Edge Cases
A mismatch between Kconfig symbols and object names would either omit intended functionality or break builds. Because optional objects are folded into `dvb-core-objs`, dependency mistakes can affect built-in versus module linking. Removing `dvb_ringbuffer.o` or `dmxdev.o` would break the demux/DVR file operations.

## Test Signals
Run targeted builds with `CONFIG_DVB_CORE=y/m`, `CONFIG_DVB_NET=y/n`, and `CONFIG_DVB_MMAP=y/n`. Expected artifacts are `dvb-core.o` or `dvb-core.ko` containing optional symbols only when selected, with no unresolved references to `dvb_vb2_*` when mmap is disabled.
