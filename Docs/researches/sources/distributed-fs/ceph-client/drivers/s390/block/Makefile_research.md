## sources/distributed-fs/ceph-client/drivers/s390/block/Makefile

Purpose: Defines object aggregation for S/390 block drivers, especially the DASD core and its ECKD/FBA/DIAG disciplines.

Important APIs/types/functions: Kbuild composite objects are `dasd_mod-objs`, `dasd_eckd_mod-objs`, `dasd_fba_mod-objs`, `dasd_diag_mod-objs`, and `scm_block-objs`. Conditional object entries use `obj-$(CONFIG_...)`.

Control flow: `dasd_mod` is built from core files `dasd.o`, `dasd_ioctl.o`, `dasd_proc.o`, `dasd_devmap.o`, `dasd_genhd.o`, and `dasd_erp.o`; `dasd_eer.o` is added only when `CONFIG_DASD_EER` is set. ECKD combines `dasd_eckd.o`, `dasd_3990_erp.o`, and `dasd_alias.o`; FBA and DIAG each wrap one discipline file. `DCSSBLK` and `SCM_BLOCK` add their respective modules.

State and persistence: No runtime state. Build composition determines which exported symbols from `dasd.c` are linked into the core module and available to discipline modules.

Dependencies/integration: Receives Kconfig decisions from `drivers/s390/block/Kconfig` and emits modules consumed by the s390 CCW driver model and block layer.

Risks: Object ordering matters for module initialization and symbol availability. Forgetting to add a file to the composite object can create unresolved symbols only for certain configs. `dasd_eer.o` is conditionally part of the core, so call sites in `dasd.c` must have stubs when disabled.

Test signals: Build `CONFIG_DASD=y/m`, each discipline as `y/m`, `CONFIG_DASD_EER=y/n`, and `CONFIG_SCM_BLOCK=m`; check `modinfo` and link outputs for `dasd_mod`, `dasd_eckd_mod`, `dasd_fba_mod`, and `dasd_diag_mod`.
