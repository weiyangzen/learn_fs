<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Makefile

Purpose: maps the LPDDR Kconfig symbols to their object files.

Important APIs, types, and functions: `obj-$(CONFIG_MTD_QINFO_PROBE) += qinfo_probe.o`, `obj-$(CONFIG_MTD_LPDDR) += lpddr_cmds.o`, and `obj-$(CONFIG_MTD_LPDDR2_NVM) += lpddr2_nvm.o`.

Control flow: Kbuild includes probe support, command-set support, and LPDDR2-NVM platform support independently according to configuration. `lpddr_cmds.o` exports `lpddr_cmdset()` while `qinfo_probe.o` registers the chip probe driver that calls it.

State and persistence: no runtime state; this is build orchestration only.

Dependencies and integration points: consumes the symbols declared in `lpddr/Kconfig` and produces modules/objects linked into the MTD subsystem.

Risks: if `MTD_LPDDR` were enabled without a matching QINFO probe object, LPDDR devices would not bind; Kconfig currently avoids that by selecting `MTD_QINFO_PROBE`. Test signals are presence of expected objects in build logs and no unresolved `lpddr_cmdset` symbol when QINFO probing is modular.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/lpddr/Makefile -->
