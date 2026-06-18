<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Makefile

Purpose: Kbuild rule for the T-HEAD pmdomain provider.

Important APIs/types/functions: maps `CONFIG_TH1520_PM_DOMAINS` to `th1520-pm-domains.o`.

Control flow/state: build-time only.

Dependencies/integration: paired with the local Kconfig and TH1520 AON firmware headers.

Risks: config/object name drift would omit the driver from builds.

Test signals: compile with `CONFIG_TH1520_PM_DOMAINS=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Makefile -->
