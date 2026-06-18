<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Makefile -->
## sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Makefile

Purpose: this Makefile builds the Chelsio FCoE driver and sets the include path required for Chelsio cxgb4 hardware definitions.

Important APIs, types, and functions: `ccflags-y` adds `-I$(srctree)/drivers/net/ethernet/chelsio/cxgb4`. `obj-$(CONFIG_SCSI_CHELSIO_FCOE) += csiostor.o` ties the object to the Kconfig symbol. `csiostor-objs` composes the module from `csio_attr.o`, `csio_init.o`, `csio_lnode.o`, `csio_scsi.o`, `csio_hw.o`, `csio_hw_t5.o`, `csio_isr.o`, `csio_mb.o`, `csio_rnode.o`, and `csio_wr.o`.

Control flow: this is build orchestration only. When the Kconfig symbol is enabled, kbuild links the listed objects into `csiostor.o`; when built as a module, the same aggregate becomes `csiostor.ko`.

State and persistence behavior: no runtime state exists. Build state is determined by the selected kernel configuration and source tree include layout.

Dependencies and integration points: it integrates the csiostor driver with Chelsio cxgb4 register/header definitions and with the Linux kbuild object aggregation model. The source list shows the driver split between attributes, initialization, lnode/rnode state, SCSI I/O, hardware, T5 hardware specifics, ISR, mailbox, and work-request handling.

Risks: include-path coupling to cxgb4 means changes in networking driver headers can affect this SCSI driver. The object list must remain synchronized with exported symbols across the csiostor subsystem; missing one object can produce link failures or incomplete runtime behavior.

Test signals: build with `CONFIG_SCSI_CHELSIO_FCOE=m` and `=y`, run `modpost`, verify all object dependencies resolve, and check that cxgb4 header changes do not break csiostor compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/Makefile -->
