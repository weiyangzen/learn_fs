<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/Makefile -->
# sources/distributed-fs/ceph-client/drivers/vdpa/pds/Makefile

Purpose: Builds the AMD/Pensando PDS vDPA module when `CONFIG_PDS_VDPA` is enabled.

Important APIs/types/functions: The Kbuild target is `obj-$(CONFIG_PDS_VDPA) := pds_vdpa.o`, with module objects `aux_drv.o`, `cmds.o`, `debugfs.o`, and `vdpa_dev.o`.

Control flow: Kernel build links the auxiliary-bus driver, admin command wrappers, debugfs support, and vDPA device implementation into one `pds_vdpa` module.

State and persistence: No runtime state; this file only controls compilation.

Dependencies and integration points: Depends on the Kconfig symbol and the PDS common/adminq/auxbus headers used by the component C files.

Risks: Omitting any object breaks core lifecycle: `aux_drv.o` owns module init/probe, `vdpa_dev.o` owns vDPA ops, `cmds.o` owns firmware commands, and `debugfs.o` owns observability.

Test signals: Build with `CONFIG_PDS_VDPA=m/y` and verify the final object contains symbols from all four listed object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/vdpa/pds/Makefile -->
