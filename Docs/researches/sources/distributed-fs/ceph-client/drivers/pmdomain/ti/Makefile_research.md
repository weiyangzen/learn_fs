<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Makefile

Purpose: Kbuild rules for TI pmdomain drivers.

Important APIs/types/functions: maps `CONFIG_OMAP2PLUS_PRM` to `omap_prm.o` and `CONFIG_TI_SCI_PM_DOMAINS` to `ti_sci_pm_domains.o`.

Control flow/state: build-time only.

Dependencies/integration: driven by the adjacent Kconfig symbols and architecture/platform config.

Risks: accidental symbol mismatch would omit required early boot providers.

Test signals: compile with OMAP2PLUS and TI SCI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Makefile -->
