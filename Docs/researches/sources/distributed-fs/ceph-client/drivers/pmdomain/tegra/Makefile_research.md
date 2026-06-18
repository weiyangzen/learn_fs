<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Makefile

Purpose: Kbuild rule for the Tegra pmdomain directory.

Important APIs/types/functions: maps `CONFIG_SOC_TEGRA_POWERGATE_BPMP` to `powergate-bpmp.o`.

Control flow: no runtime logic.

State/persistence: build artifact selection only.

Dependencies/integration: paired with the local Kconfig and Tegra BPMP core that calls the exported init/remove functions.

Risks: a symbol rename in Kconfig or source would silently stop building this provider.

Test signals: `make drivers/pmdomain/tegra/` with the config enabled should compile exactly this object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Makefile -->
