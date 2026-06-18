# sources/distributed-fs/ceph-client/drivers/pmdomain/arm/Kconfig

Purpose: Kconfig fragment for ARM firmware-mediated power and performance domain providers.

Important APIs/types/functions: defines `ARM_SCMI_PERF_DOMAIN`, `ARM_SCMI_POWER_DOMAIN`, and `ARM_SCPI_POWER_DOMAIN`, each depending on the matching firmware protocol or compile-test with OF and selecting `PM_GENERIC_DOMAINS` when PM is enabled.

Control flow: no runtime flow; controls whether SCMI/SCPI genpd providers are built.

State and persistence: `.config` choices determine built-in/module objects.

Dependencies/integration: consumed by `arm/Makefile`; help text documents module names `scmi_perf_domain`, `scmi_pm_domain`, and `scpi_pm_domain`.

Risks: these drivers may be needed early for rootfs devices, so modular configuration can affect boot on some systems. Missing protocol dependencies would produce probe deferral or build errors.

Test signals: protocol-enabled builds, compile-test builds, and boot tests where storage/display/network devices use SCMI/SCPI power domains.
