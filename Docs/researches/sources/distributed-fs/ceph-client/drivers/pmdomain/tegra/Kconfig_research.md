<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Kconfig

Purpose: Kconfig switch for Tegra BPMP-backed powergate domains.

Important APIs/types/functions: defines `SOC_TEGRA_POWERGATE_BPMP` as a default-y bool when `PM_GENERIC_DOMAINS` and `TEGRA_BPMP` are available.

Control flow: no runtime control flow; Kbuild selects compilation of `powergate-bpmp.o` through the Makefile when dependencies are met.

State/persistence: build-time only.

Dependencies/integration: ensures the driver is built only with generic PM domain support and the Tegra BPMP firmware transport.

Risks: default-y means platforms with BPMP automatically include the provider; dependency mistakes would surface as missing symbols at build time.

Test signals: kernel configuration should include this symbol on BPMP Tegra targets and build `drivers/pmdomain/tegra/powergate-bpmp.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/Kconfig -->
