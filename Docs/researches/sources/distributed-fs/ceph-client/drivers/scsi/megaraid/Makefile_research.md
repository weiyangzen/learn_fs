# sources/distributed-fs/ceph-client/drivers/scsi/megaraid/Makefile

## Purpose
This Makefile connects the MegaRAID subdirectory to Kbuild. It selects the common management module, mailbox low-level driver, and SAS driver from kernel configuration and defines the composite object list for `megaraid_sas`.

## Important APIs and Integration Points
`obj-$(CONFIG_MEGARAID_MM) += megaraid_mm.o` builds the common management misc-device module. `obj-$(CONFIG_MEGARAID_MAILBOX) += megaraid_mbox.o` builds the mailbox SCSI driver. `obj-$(CONFIG_MEGARAID_SAS) += megaraid_sas.o` builds the SAS driver, with `megaraid_sas-objs` made from base, fusion, fast-path, and debugfs objects.

## Control Flow, State, Dependencies, and Risks
There is no runtime state or control flow here; behavior is entirely build-time. The important dependency is config consistency: the mailbox driver includes management interfaces and expects `megaraid_mm` exported symbols when management support is used. Test signals are `make M=drivers/scsi/megaraid` under module and built-in combinations for `CONFIG_MEGARAID_MM`, `CONFIG_MEGARAID_MAILBOX`, and `CONFIG_MEGARAID_SAS`, plus module dependency inspection.
