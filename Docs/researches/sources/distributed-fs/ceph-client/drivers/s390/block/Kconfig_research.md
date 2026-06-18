## sources/distributed-fs/ceph-client/drivers/s390/block/Kconfig

Purpose: Declares S/390 block-device configuration options for DCSSBLK, DASD core/disciplines, DASD profiling/EER, and SCM block devices.

Important APIs/types/functions: Kconfig symbols are `DCSSBLK`, `DASD`, `DASD_PROFILE`, `DASD_ECKD`, `DASD_FBA`, `DASD_DIAG`, `DASD_EER`, and `SCM_BLOCK`. Dependencies tie them to `S390`, `BLOCK`, `CCW`, `ZONE_DEVICE`, `EADM_SCH`, and `SCM_BUS`; `DCSSBLK` selects `FS_DAX`.

Control flow: Menu visibility starts with the comment depending on `S390 && BLOCK`. DASD defaults to built-in when `CCW && BLOCK` are available. ECKD/FBA/DIAG default to built-in or tristate according to their declarations and depend on DASD. DASD profiling and EER are boolean defaults when DASD is enabled. SCM block builds as a module by default when its S390 bus prerequisites are available.

State and persistence: Kconfig selections persist in `.config` and drive conditional compilation in the block Makefile and C sources. For example, `CONFIG_DASD_PROFILE` includes profiling/debugfs code in `dasd.c`, and `CONFIG_DASD_EER` adds `dasd_eer.o`.

Dependencies/integration: Integrates with s390 CCW channel subsystem, block layer, DAX/zone-device support, EADM subchannels, and SCM bus.

Risks: Defaults make DASD and common disciplines available automatically on S/390, so broken dependencies can affect boot-critical storage. Boolean `DASD_EER` and `DASD_PROFILE` increase compiled surface whenever DASD is on. Help text should remain clear because selecting DIAG only makes sense under VM.

Test signals: `olddefconfig` on S390 should select expected defaults; all combinations of `DASD` with ECKD/FBA/DIAG modular or built-in should link through `drivers/s390/block/Makefile`; `CONFIG_DASD_PROFILE=n` should compile out profiling sections cleanly.
