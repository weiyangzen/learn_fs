<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/devfreq/event/Kconfig

Purpose: defines build-time configuration for devfreq-event provider support and the Exynos NoCP, Exynos PPMU, and Rockchip DFI event drivers.

Important APIs and control flow: `PM_DEVFREQ_EVENT` is a boolean menu gate for the event framework and its provider submenu. `DEVFREQ_EVENT_EXYNOS_NOCP` is tristate, depends on `ARCH_EXYNOS || COMPILE_TEST`, and selects `PM_OPP` plus `REGMAP_MMIO`. `DEVFREQ_EVENT_EXYNOS_PPMU` is tristate, depends on Exynos or compile testing, and selects `PM_OPP`. `DEVFREQ_EVENT_ROCKCHIP_DFI` is tristate, depends on Rockchip or compile testing.

State and persistence behavior: no runtime state; this file controls which provider modules are compiled and therefore whether DT phandles to those providers can bind.

Dependencies and integration points: consumed by the drivers/devfreq build. The selected symbols align with provider implementation dependencies on regmap, OPP, and SoC-specific headers. Consumer drivers such as Exynos bus and RK3399 DMC need matching providers available or probes defer.

Risks and test signals: missing `PM_DEVFREQ_EVENT` prevents all event providers from building even if consumers reference them. Rockchip DFI has optional perf-event code but no Kconfig select for `PERF_EVENTS`; it compiles that block only when the global symbol is enabled. Test signals are allmodconfig/allyesconfig builds, module builds for each tristate, and DT boot where providers probe before consumers or consumers defer cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/event/Kconfig -->
