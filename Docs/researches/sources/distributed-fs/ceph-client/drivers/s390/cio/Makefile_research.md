# sources/distributed-fs/ceph-client/drivers/s390/cio/Makefile

Purpose: builds the s390 common I/O subsystem objects and optional CIO-related drivers.

Important APIs/types/functions: not code, but defines object composition for built-in CIO core (`airq.o`, `blacklist.o`, `cio.o`, `css.o`, `ccwreq.o`, tracing/debugfs and others), compound objects `ccw_device.o`, `qdio.o`, and `vfio_ccw.o`, and config-gated objects for CCWGROUP, QDIO, VFIO_CCW, SCM, EADM, CHSC, and CIO injection.

Control flow: kbuild collects always-built `obj-y` pieces, assembles multi-object drivers through `*-objs`, and adds optional objects based on Kconfig symbols. It also adds local include paths for generated trace headers.

State and persistence: no runtime state; it defines build-time composition.

Dependencies and integration: integrates this directory with Kbuild, trace header include resolution, and config-driven s390 driver selection.

Risks: missing an object here can silently omit subsystem functionality; trace objects require `-I$(src)` for local `define_trace.h` inclusion; optional compound object ordering matters for link dependencies.

Test signals: s390 kernel builds across key configs, especially `CONFIG_CCWGROUP`, `CONFIG_QDIO`, `CONFIG_VFIO_CCW`, trace-enabled builds, and allyesconfig/allmodconfig link checks.
