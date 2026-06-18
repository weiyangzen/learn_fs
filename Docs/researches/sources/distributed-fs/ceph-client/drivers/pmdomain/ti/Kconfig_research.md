<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Kconfig

Purpose: Build configuration for TI PRM and TI SCI power-domain providers.

Important APIs/types/functions: `OMAP2PLUS_PRM` is a bool defaulting with `ARCH_OMAP2PLUS`; `TI_SCI_PM_DOMAINS` is a tristate under `SOC_TI`, depends on `TI_SCI_PROTOCOL`, and selects generic PM domains when PM is enabled.

Control flow: build-time selection only.

State/persistence: no runtime state.

Dependencies/integration: separates legacy OMAP PRM register-backed domains from K3/TI SCI firmware-backed domains.

Risks: `TI_SCI_PM_DOMAINS` help notes early-boot need before rootfs, so modular builds can be unsuitable for platforms needing domains early.

Test signals: OMAP configs build `omap_prm.o`; TI SCI configs build or include `ti_sci_pm_domains.o` with protocol support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/ti/Kconfig -->
