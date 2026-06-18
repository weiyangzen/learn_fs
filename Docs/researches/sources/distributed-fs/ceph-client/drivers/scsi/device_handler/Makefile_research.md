<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Makefile

Purpose: maps SCSI device-handler Kconfig symbols to their implementation objects.

Important APIs/types/functions: Kbuild entries compile `scsi_dh_rdac.o`, `scsi_dh_hp_sw.o`, `scsi_dh_emc.o`, and `scsi_dh_alua.o` for the corresponding `CONFIG_SCSI_DH_*` symbols.

Control flow: no runtime flow exists. Kbuild evaluates the `obj-$(CONFIG_...)` assignments and links or modules the selected handlers.

State and persistence: build state comes from `.config`; the Makefile itself does not carry runtime state.

Dependencies and integration: this is the build integration point for the adjacent Kconfig options and the SCSI device-handler source files. It expects each object to register and unregister itself with the SCSI device-handler core at module init/exit.

Risks: object-name drift or missing entries make a selectable handler fail to build or silently not appear. Built-in combinations should preserve registration ordering assumptions.

Test signals: build all four handlers as modules and built-ins; inspect generated modules or vmlinux link for the selected object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/device_handler/Makefile -->
