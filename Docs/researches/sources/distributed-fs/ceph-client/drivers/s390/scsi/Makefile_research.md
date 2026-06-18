# sources/distributed-fs/ceph-client/drivers/s390/scsi/Makefile

Purpose: defines how the s390 zfcp SCSI/FCP driver is built.

Important APIs and functions: `zfcp-objs` lists all object files linked into `zfcp.o`, including the researched `zfcp_aux.o`, `zfcp_ccw.o`, and `zfcp_dbf.o`. `obj-$(CONFIG_ZFCP) += zfcp.o` connects the composite driver to kernel configuration.

Control flow: kbuild compiles and links the listed objects when `CONFIG_ZFCP` is enabled.

State and persistence: no runtime state; the file controls build composition.

Dependencies and integration: integrates zfcp auxiliary, ccw, debug, ERP, Fibre Channel, FSF, QDIO, SCSI, sysfs, unit, and diagnostic components into one module or built-in driver.

Risks: missing an object from `zfcp-objs` yields unresolved symbols or disabled functionality. Object ordering can matter for initcall/linkage expectations in rare cases, though this file uses conventional composite object linkage.

Test signals: `CONFIG_ZFCP=m` and `CONFIG_ZFCP=y` builds, link checks for all zfcp symbols, and ensuring researched objects are included in `zfcp.o`.
