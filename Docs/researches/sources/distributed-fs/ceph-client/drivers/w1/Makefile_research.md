## sources/distributed-fs/ceph-client/drivers/w1/Makefile

Purpose: this Makefile builds the 1-Wire core and descends into master and slave driver directories.

Important APIs/types/functions: `obj-$(CONFIG_W1) += wire.o` builds the core module/object, and `wire-objs` is composed from `w1.o`, `w1_int.o`, `w1_family.o`, `w1_netlink.o`, and `w1_io.o`. `obj-y += masters/ slaves/` always visits subdirectories so their own config symbols decide what to build.

Control flow: Kbuild links the core pieces into `wire.o` when `CONFIG_W1` is enabled, while child Makefiles contribute selected bus master and slave drivers.

State and persistence behavior: no runtime state. It controls build graph composition only.

Dependencies and integration points: integrates Kbuild with Kconfig symbols from `drivers/w1/Kconfig`, master Kconfig, and slave Kconfig.

Risks: `w1_netlink.o` is part of `wire-objs` regardless of `W1_CON`, so correctness depends on source-level conditional compilation for connector-specific behavior.

Test signals: allmodconfig and minimal `W1=m` builds, plus configurations with no master/slave modules selected.
