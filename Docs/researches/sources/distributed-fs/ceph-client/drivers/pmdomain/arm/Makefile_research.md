# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Makefile

Purpose: Kbuild mapping for ARM SCMI/SCPI PM-domain drivers.

Important APIs/types/functions: maps `CONFIG_ARM_SCMI_PERF_DOMAIN` to `scmi_perf_domain.o`, `CONFIG_ARM_SCMI_POWER_DOMAIN` to `scmi_pm_domain.o`, and `CONFIG_ARM_SCPI_POWER_DOMAIN` to `scpi_pm_domain.o`.

Control flow: no runtime flow.

State and persistence: object inclusion follows `.config`.

Dependencies/integration: synchronized with `arm/Kconfig`.

Risks: stale mapping breaks protocol provider builds.

Test signals: targeted builds for each symbol and module-name checks.
