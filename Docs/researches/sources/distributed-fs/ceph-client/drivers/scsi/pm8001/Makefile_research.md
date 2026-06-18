# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/Makefile

Purpose: Kbuild file for the PM8001/PM80xx SAS/SATA HBA driver.

Important entries: `obj-$(CONFIG_SCSI_PM8001) += pm80xx.o` builds the module. `CFLAGS_pm80xx_tracepoints.o := -I$(src)` supplies local tracepoint includes. `pm80xx-y` aggregates init, SAS, control, hardware-interface, PM80xx hardware-interface, and tracepoint objects.

Control flow/state: build-time only. No runtime state; it controls object composition for the driver.

Dependencies/integration: tied to `CONFIG_SCSI_PM8001` and the PM8001 source units in the same directory.

Risks/test signals: missing objects or include flags break builds. Test with `CONFIG_SCSI_PM8001=m/y`, tracepoint compilation, and module link.
