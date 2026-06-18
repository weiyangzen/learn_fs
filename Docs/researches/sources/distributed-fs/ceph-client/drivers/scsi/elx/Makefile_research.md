<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/elx/Makefile

Purpose: defines the composite `efct` module/object layout for the Emulex Fibre Channel target driver and its local protocol libraries.

Important APIs/types/functions: `obj-$(CONFIG_SCSI_EFCT) := efct.o` builds the composite object. `efct-objs` includes driver, I/O, SCSI target, transport, hardware queue, LIO, unsolicited-frame code, `libefc` discovery/state-machine files, and `libefc_sli/sli4.o`.

Control flow: no runtime flow exists. Kbuild links the listed objects into one `efct` module or built-in object when `CONFIG_SCSI_EFCT` is enabled.

State and persistence: no runtime state is stored here; build graph state follows `.config`.

Dependencies and integration: this file is the build integration point connecting `efct/`, `libefc/`, and `libefc_sli/` into one driver. `efct_driver.c` provides PCI/module entry points, while the other objects provide target I/O, FC discovery, SLI-4 hardware, and LIO integration.

Risks: missing or misordered object entries can cause unresolved symbols or partially linked driver functionality. Since this is a composite module, new cross-file helpers require Makefile updates.

Test signals: module and built-in builds of `CONFIG_SCSI_EFCT`, modpost symbol checks, and load-time availability of PCI, libefc, hardware, and LIO entry points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/elx/Makefile -->
