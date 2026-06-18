# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Makefile

Purpose: Connects QLogic Kconfig symbols to driver objects or subdirectories in the kernel build.

Important build rules: `obj-$(CONFIG_QLA3XXX) += qla3xxx.o`, `obj-$(CONFIG_QLCNIC) += qlcnic/`, `obj-$(CONFIG_NETXEN_NIC) += netxen/`, `obj-$(CONFIG_QED) += qed/`, and `obj-$(CONFIG_QEDE)+= qede/`.

Control flow: Kbuild includes object files or descends into subdirectories based on resolved `.config` symbols.

State and persistence behavior: No runtime state. Build artifacts depend on Kconfig values.

Dependencies and integration points: Integrates the vendor directory with top-level kernel networking Kbuild and the per-driver Makefiles.

Risks: Symbol/rule mismatch would silently omit a configured driver or build the wrong directory. The `CONFIG_QEDE` assignment has no space before `+=`, which is valid make syntax but easy to overlook in style checks.

Test signals: Build with each QLogic symbol as module and built-in; verify expected modules and objects are produced.
