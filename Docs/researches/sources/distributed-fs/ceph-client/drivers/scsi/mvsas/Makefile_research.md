# sources/distributed-fs/ceph-client/drivers/scsi/mvsas/Makefile

Purpose: declares the Kbuild object composition for the Marvell `mvsas` driver.

Important APIs/types/functions: `ccflags-$(CONFIG_SCSI_MVSAS_DEBUG) := -DMV_DEBUG` enables debug logging. `obj-$(CONFIG_SCSI_MVSAS) += mvsas.o` builds the composite driver, and `mvsas-y` links `mv_init.o`, `mv_sas.o`, `mv_64xx.o`, and `mv_94xx.o`.

Control flow: no runtime behavior. Kbuild resolves the composite object from configuration symbols.

State and persistence: no runtime state. Build output depends on `.config`.

Dependencies and integration points: this file is the directory-level bridge between `Kconfig` and the source files that provide PCI/lifecycle code, libsas glue, and per-chip dispatch implementations.

Risks and test signals: omitting a component breaks dispatch or libsas symbol resolution. Compile/link tests with `CONFIG_SCSI_MVSAS=m` and `=y`, plus debug/tasklet variants, verify object list completeness.
